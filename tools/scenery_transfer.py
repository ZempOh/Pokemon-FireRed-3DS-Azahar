"""Prove reusable asset identity from local ROMs; never infer it from tile IDs.

This conservative first adapter handles FireRed's 640/384 two-layer layout.
Different engines and artwork are reported for adapters, never silently enabled.
No ROM bytes are written to the report.
"""
import argparse
import hashlib
import json
import re
import struct
import zlib
from pathlib import Path


class Art:
    def __init__(self, path):
        self.data = Path(path).read_bytes()
        self.cache = {}

    def read(self, address, size):
        offset = address - 0x08000000
        if not 0 <= offset <= len(self.data) - size:
            raise ValueError('ROM pointer outside file')
        return self.data[offset:offset + size]

    def word(self, address):
        return struct.unpack('<I', self.read(address, 4))[0]

    def tiles(self, ts):
        if ts in self.cache:
            return self.cache[ts]
        address = self.word(ts + 4)
        if self.read(ts, 1) == b'\0':
            result = self.read(address, 640 * 32)
        else:
            header = self.word(address)
            if header & 255 != 16 or not 0 < header >> 8 <= 65536:
                raise ValueError('Unsupported tile compression')
            result = bytearray()
            position = address + 4
            while len(result) < header >> 8:
                flags = self.read(position, 1)[0]
                position += 1
                for bit in range(7, -1, -1):
                    if len(result) >= header >> 8:
                        break
                    if flags & (1 << bit):
                        a, b = self.read(position, 2)
                        position += 2
                        distance = ((a & 15) << 8 | b) + 1
                        if distance > len(result):
                            raise ValueError('Invalid compressed back reference')
                        for _ in range(min((a >> 4) + 3, (header >> 8) - len(result))):
                            result.append(result[-distance])
                    else:
                        result.extend(self.read(position, 1))
                        position += 1
            result = bytes(result)
        self.cache[ts] = result
        return result

    def signature(self, ts, ids):
        """Both layers, transparent mask, actual colors and FR attributes.

        Only primary-owned pixels qualify, so secondary palette changes cannot
        accidentally reuse a profile. Flip bits are resolved into the pixels.
        """
        tiles = self.tiles(ts)
        palette = self.read(self.word(ts + 8), 7 * 32)
        result = bytearray()
        for mid in ids:
            if not 0 <= mid < 640:
                raise ValueError('Secondary metatile requires its own adapter')
            result.extend(self.read(self.word(ts + 20) + mid * 4, 4))
            entries = struct.unpack('<8H', self.read(self.word(ts + 12) + mid * 16, 16))
            for entry in entries:
                tile, pal = entry & 1023, entry >> 12
                if tile >= 640 or pal >= 7:
                    raise ValueError('Secondary-owned tile or palette')
                for y in range(8):
                    for x in range(8):
                        px = 7 - x if entry & 1024 else x
                        py = 7 - y if entry & 2048 else y
                        offset = tile * 32 + py * 4 + px // 2
                        if offset >= len(tiles):
                            raise ValueError('Tile outside decompressed data')
                        index = tiles[offset] >> (4 * (px & 1)) & 15
                        result.append(bool(index))
                        result.extend(palette[(pal * 16 + index) * 2:(pal * 16 + index) * 2 + 2] if index else b'\0\0')
        return hashlib.sha256(result).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--reference', type=Path, required=True)
    p.add_argument('--runtime', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    reference = Art(args.reference)
    if zlib.crc32(reference.data) != 0xfba55dd8:
        raise ValueError('Reference must be the verified Radical Red revision')
    families = {
        'outdoor': (0x082d4a94, sorted(set([0x9f,0xaf,0xb7,0x115,0xfa,0xfb] + list(range(40)) + [0xc1] + list(range(0xd0,0xe6)) + list(range(0xfe,0x108))))),
        'indoor_plants': (0x082d4bb4, [0x47,0x4f,0x57,0x5f]),
    }
    baseline = {key: reference.signature(*value) for key, value in families.items()}
    runtime = args.runtime.read_text()
    rows = []
    for game in json.loads(args.manifest.read_text())['games']:
        art = Art(args.manifest.parent / (game['key'] + '.gba'))
        if hashlib.sha256(art.data).hexdigest() != game['sha256'] or f'{zlib.crc32(art.data):08x}' != game['crc32']:
            raise ValueError('ROM identity mismatch: ' + game['key'])
        match = re.search(r'\{ 0x' + game['crc32'] + r', (PK_WIDE_FAMILY_\w+),', runtime)
        row = {key: game[key] for key in ('key','title','sha256','crc32')}
        row.update(runtime_family=match.group(1) if match else None, families={}, thor_passed=False)
        for family, inputs in families.items():
            try:
                digest = art.signature(*inputs)
                row['families'][family] = {'exact_match': digest == baseline[family], 'signature': digest}
            except (ValueError, struct.error) as error:
                row['families'][family] = {'exact_match': False, 'reason': str(error)}
        row['transfer_ready'] = row['runtime_family'] == 'PK_WIDE_FAMILY_FR' and all(v['exact_match'] for v in row['families'].values())
        rows.append(row)
        print(game['key'], 'exact family transfer' if row['transfer_ready'] else 'needs game-specific adapter',
              ', '.join(k for k,v in row['families'].items() if v['exact_match']))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'schema':1,'reference_crc32':'fba55dd8','families':{k:{'primary':hex(v[0]),'ids':v[1],'signature':baseline[k]} for k,v in families.items()},'games':rows}, indent=2))


if __name__ == '__main__':
    main()
