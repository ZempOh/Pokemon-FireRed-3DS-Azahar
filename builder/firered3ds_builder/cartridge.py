"""Fill the empty RomFS data slot of a matched, unencrypted makerom CCI."""

from __future__ import annotations

import gzip
import hashlib
import struct
from pathlib import Path

from .pak import PakReader
from .recipe import Recipe

BLOCK_BYTES = 0x1000
HASH_BYTES = 32


def align(value: int, boundary: int) -> int:
    return (value + boundary - 1) & -boundary


def romfs_files(image: bytearray, level3: int, data_size: int):
    header_size, _, _, _, _, _, _, table, table_size, data = struct.unpack_from("<10I", image, level3)
    if header_size != 0x28 or not 0x28 <= table <= table + table_size <= data <= data_size:
        raise ValueError("Invalid RomFS file table")
    index = level3 + table
    table_end = index + table_size
    while index < table_end:
        if index + 32 > table_end:
            raise ValueError("Truncated RomFS file entry")
        parent, _, position, size, _, name_size = struct.unpack_from("<IIQQII", image, index)
        following = index + 32 + align(name_size, 4)
        if name_size % 2 or following > table_end or data + position + size > data_size:
            raise ValueError("Invalid RomFS file entry")
        name = image[index + 32:index + 32 + name_size].decode("utf-16-le")
        yield parent, name, index, level3 + data + position, size
        index = following


def pack_slot(image: bytearray) -> tuple[int, int, int, int, int, int]:
    """Return the NCCH/RomFS locations and the reserved file entry and data."""
    if image[0x100:0x104] != b"NCSD" or image[0x18E] != 0:
        raise ValueError("Expected a 512-byte media unit NCSD cartridge")
    ncch, partition_size = struct.unpack_from("<II", image, 0x120)
    ncch *= 0x200
    if ncch < 0x200 or ncch + partition_size * 0x200 > len(image):
        raise ValueError("Invalid executable partition extent")
    if image[ncch + 0x100:ncch + 0x104] != b"NCCH" or image[ncch + 0x18E] != 0:
        raise ValueError("Expected an NCCH executable partition")
    if not image[ncch + 0x18F] & 4:
        raise ValueError("The cartridge executable partition is encrypted")
    offset, size, hash_size = struct.unpack_from("<III", image, ncch + 0x1B0)
    romfs = ncch + offset * 0x200
    if not 0 < hash_size <= size or offset + size > partition_size:
        raise ValueError("Invalid NCCH RomFS extent")
    if image[romfs:romfs + 8] != b"IVFC\x00\x00\x01\x00":
        raise ValueError("Expected a version 1 RomFS integrity tree")
    master_size = struct.unpack_from("<I", image, romfs + 8)[0]
    master = romfs + 0x60
    levels = [struct.unpack_from("<QQI", image, romfs + 12 + 24 * i) for i in range(3)]
    if any(shift != 12 for _, _, shift in levels):
        raise ValueError("Unsupported RomFS integrity block size")
    level3 = romfs + align(0x60 + master_size, BLOCK_BYTES)
    data_size = levels[2][1]
    level1 = level3 + align(data_size, BLOCK_BYTES)
    level2 = level1 + align(levels[0][1], BLOCK_BYTES)
    sizes = [level[1] for level in levels]
    if (level2 + align(sizes[1], BLOCK_BYTES) > romfs + size * 0x200
            or master_size != align(sizes[0], BLOCK_BYTES) // BLOCK_BYTES * HASH_BYTES
            or sizes[0] != align(sizes[1], BLOCK_BYTES) // BLOCK_BYTES * HASH_BYTES
            or sizes[1] != align(data_size, BLOCK_BYTES) // BLOCK_BYTES * HASH_BYTES):
        raise ValueError("Invalid RomFS integrity levels")
    if master + master_size > romfs + hash_size * 0x200:
        raise ValueError("NCCH does not hash the full RomFS master table")
    for parent, name, index, position, capacity in romfs_files(image, level3, data_size):
        if parent == 0 and name == "firered3ds.pak" and capacity:
            return ncch, romfs, level3, index, position, capacity
    raise ValueError("No FireRed data slot in cartridge RomFS")


def verify_engine_abi(image: bytearray, expected: int) -> None:
    _, romfs, level3, _, _, _ = pack_slot(image)
    data_size = struct.unpack_from("<Q", image, romfs + 68)[0]
    for _, name, _, position, size in romfs_files(image, level3, data_size):
        if name == "abi.bin" and size == 4:
            if struct.unpack_from("<I", image, position)[0] == expected:
                return
            break
    raise ValueError("The cartridge engine and extraction recipe have different data ABIs")


def fill_image(image: bytearray, pack: bytes) -> None:
    ncch, romfs, level3, entry, slot, capacity = pack_slot(image)
    if not pack or len(pack) > capacity or any(memoryview(image)[slot:slot + capacity]):
        raise ValueError("The cartridge data slot is populated or too small")
    image[slot:slot + len(pack)] = pack
    struct.pack_into("<Q", image, entry + 16, len(pack))

    sizes = [struct.unpack_from("<Q", image, romfs + 20 + 24 * i)[0] for i in range(3)]
    level1 = level3 + align(sizes[2], BLOCK_BYTES)
    level2 = level1 + align(sizes[0], BLOCK_BYTES)
    view = memoryview(image)
    for source, destination, size in ((level3, level2, sizes[2]),
                                      (level2, level1, sizes[1]),
                                      (level1, romfs + 0x60, sizes[0])):
        for index in range(align(size, BLOCK_BYTES) // BLOCK_BYTES):
            start = source + index * BLOCK_BYTES
            digest = hashlib.sha256(view[start:start + BLOCK_BYTES]).digest()
            offset = destination + index * HASH_BYTES
            image[offset:offset + HASH_BYTES] = digest
    length = struct.unpack_from("<I", image, ncch + 0x1B8)[0] * 0x200
    image[ncch + 0x1E0:ncch + 0x200] = hashlib.sha256(view[romfs:romfs + length]).digest()
    # The template's test signature no longer describes the modified header.
    # Azahar accepts unencrypted homebrew without Nintendo signatures.
    image[ncch:ncch + 0x100] = bytes(0x100)


def build_cartridge(template: Path, pack: Path, recipe: Path, output: Path) -> None:
    expected = Recipe.load(recipe)
    with PakReader(pack) as reader:
        if reader.abi != expected.engine_abi or reader.rom_sha1.hex() != expected.rom_sha1:
            raise ValueError("Data pack and cartridge recipe do not match")
        reader.verify()
    with gzip.open(template, "rb") as compressed:
        image = bytearray(compressed.read())
    verify_engine_abi(image, expected.engine_abi)
    fill_image(image, pack.read_bytes())
    output.write_bytes(image)
