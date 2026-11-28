"""Build exact outdoor pure-floor profiles using verified private GBA inputs.

The generated C data stores identifiers and bit masks. Source-art evidence and
rendered review sheets stay in the optional private evidence directory.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import struct
import sys
import zlib

from PIL import Image, ImageChops, ImageDraw

PILOT = {
    8, 9, 17, 0x285, 0x286, 0x288, 0x28C, 0x28E, 0x28F, 0x290,
    0x295, 0x296, 0x297, 0x29E, 0x29F, 0x2A6, 0x2A7, 0x2AE, 0x2AF,
    0x2B6, 0x2BE, 0x2BF, 0x2C6, 0x2C7, 0x2CE,
}
PILOT_PAIR = (0x082D4A94, 0x082D4AAC)
MASK_LIMIT = 1024


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def exact_floor_candidates(capability, primary, secondary):
    primary_ground = {
        item for review in capability.get("land", [])
        if int(review["primary"], 16) == primary
        for item in review["ids"]
    }
    secondary_ground = {
        item for review in capability.get("secondary_land", [])
        if review["reviewed"] and (
            int(review["primary"], 16), int(review["secondary"], 16)
        ) == (primary, secondary)
        for item in review["ids"]
    }
    partial_ground = {
        cell["id"] for review in capability.get("secondary_land_masks", [])
        if (int(review["primary"], 16), int(review["secondary"], 16)) == (primary, secondary)
        for cell in review["cells"]
    } | {
        item for review in capability.get("land_caps", [])
        if int(review["primary"], 16) == primary
        for item in review["ids"]
    }
    if capability["game"] == "firered" and (primary, secondary) == PILOT_PAIR:
        primary_ground |= PILOT
        partial_ground -= PILOT  # Exact Pallet source review covers these complete cells.
    return primary_ground | secondary_ground | partial_ground, partial_ground


def count_outdoor_placements(art, locations, exceptions, primary, secondary):
    counts = Counter()
    for place in locations:
        header, layout = (int(place[key], 16) for key in ("header", "layout"))
        kind = art.read(header + 0x17, 1)[0]
        if not (1 <= kind <= 3 or (kind == 0 and (place["group"], place["map"]) in exceptions)):
            continue
        if (art.word(header), art.word(layout + 16), art.word(layout + 20)) != (layout, primary, secondary):
            raise ValueError(f"Stale map inventory row {place}")
        if (art.word(layout), art.word(layout + 4)) != (place["width"], place["height"]):
            raise ValueError(f"Stale map dimensions {place}")
        size = place["width"] * place["height"]
        cells = art.read(art.word(layout + 12), 2 * size)
        counts.update(cell & art.numbers["mask"] for cell, in struct.iter_unpack("<H", cells))
    return counts


def source_art(art, tile):
    layers = art.layers(tile)
    composite = Image.new("RGBA", (16, 16), (*art.palette[0], 255))
    opaque = Image.new("L", (16, 16))
    for layer in layers:
        composite.alpha_composite(layer)
        opaque = ImageChops.lighter(opaque, layer.getchannel("A"))
    if opaque.getextrema() != (255, 255):
        return None, None
    signature = hashlib.sha256(composite.tobytes() + b"".join(layer.tobytes() for layer in layers)).hexdigest()
    return signature, composite


def classify(art, tile, partial, decode_error, decision_by_signature, visual):
    if tile in partial:
        return "hold_rgb_or_row_mask", None, None
    if decode_error:
        return "hold_source_decode", None, decode_error
    try:
        signature, tile_image = source_art(art, tile)
    except (ValueError, struct.error) as error:
        return "hold_source_decode", None, str(error)
    if not signature:
        return "hold_no_complete_source_floor", None, None
    if visual is not None:
        visual.setdefault(signature, tile_image)
    return decision_by_signature.get(signature, "hold_unreviewed"), signature, None


def audit(args, visual):
    tools_dir = args.work / "pokedaisy-build/tools"
    sys.path.insert(0, str(tools_dir))
    from scenery_inputs import resolve_input
    from scenery_inventory import MapArt

    review = load_json(args.allowlist)
    decisions = {row["signature"]: row.get("hold", "include") for row in review["tiles"]}
    if (review["schema"] != 1 or len(decisions) != len(review["tiles"]) or
            any(len(digest) != 64 or bytes.fromhex(digest).hex() != digest for digest in decisions)):
        raise ValueError("Invalid exact source-art allowlist")
    capabilities = load_json(tools_dir / "scenery-profiles/android-capabilities.json")
    audited = []
    for cap in capabilities:
        game = cap["game"]
        rom, inventory = resolve_input(args.work, game)
        art = MapArt(rom)
        if format(zlib.crc32(art.data), "08x") != cap["rom_crc32"]:
            raise ValueError(f"Cartridge identity changed for {game}")
        art.numbers = inventory["numbers"]
        exceptions = {tuple(row) for row in cap.get("outdoor_maps", [])}
        for pair in inventory["tileset_pairs"]:
            primary, secondary = (int(pair[key], 16) for key in ("primary", "secondary"))
            candidates, partial = exact_floor_candidates(cap, primary, secondary)
            if not candidates:
                continue
            usage = count_outdoor_placements(art, pair["maps"], exceptions, primary, secondary)
            seen = candidates & usage.keys()
            if not seen:
                continue
            decode_error = None
            if seen - partial:
                try:
                    art.setup(inventory["numbers"], primary, secondary)
                except (ValueError, struct.error) as error:
                    decode_error = str(error)
            for tile in sorted(seen):
                if not 0 <= tile < MASK_LIMIT:
                    raise ValueError(f"Unsupported metatile ID for {game}: {tile:#x}")
                reason, digest, error = classify(art, tile, partial, decode_error, decisions, visual)
                row = dict(game=game, crc=cap["rom_crc32"], rom_sha256=inventory["rom_sha256"],
                           primary=hex(primary), secondary=hex(secondary), id=tile,
                           outdoor_placements=usage[tile], decision=reason)
                if digest:
                    row["source_signature"] = digest
                if error:
                    row["error"] = error
                audited.append(row)
    return audited


def generate_header(rows):
    profiles = defaultdict(set)
    for row in rows:
        if row["decision"] == "include":
            identity = tuple(int(row[key], 16) for key in ("crc", "primary", "secondary"))
            profiles[identity].add(row["id"])
    if not profiles:
        raise ValueError("No reviewed ground profiles")
    patterns = sorted({tuple(sorted(ids)) for ids in profiles.values()})
    index = {pattern: i for i, pattern in enumerate(patterns)}
    lines = [
        "// Generated by gen_hd_gba_ground.py from exact reviewed floor art. No source art.",
        "#pragma once",
        "#include <stdint.h>",
        "#include <stddef.h>",
        "",
        "enum { SCENERY_GROUND_ID_LIMIT = 1024 };",
        "static const uint32_t sceneryGroundMasks[][SCENERY_GROUND_ID_LIMIT / 32] = {",
    ]
    for ids in patterns:
        words = defaultdict(int)
        for tile in ids:
            words[tile // 32] |= 1 << (tile % 32)
        lines.append("    {" + ", ".join(f"[{word}] = 0x{bits:08x}u" for word, bits in words.items()) + "},")
    lines += [
        "};",
        "",
        "struct SceneryGroundSurfaceProfile { uint32_t crc, primary, secondary; uint16_t pattern; };",
        "static const struct SceneryGroundSurfaceProfile sceneryGroundProfiles[] = {",
    ]
    for identity, ids in sorted(profiles.items()):
        fields = ", ".join(f"0x{field:08x}u" for field in identity)
        lines.append(f"    {{{fields}, {index[tuple(sorted(ids))]}}},")
    lines += [
        "};",
        "",
        "static const uint32_t* sceneryGroundSurface(uint32_t crc, uint32_t primary, uint32_t secondary) {",
        "    size_t lo = 0, hi = sizeof(sceneryGroundProfiles) / sizeof(sceneryGroundProfiles[0]);",
        "    while (lo < hi) {",
        "        size_t mid = lo + (hi - lo) / 2;",
        "        const struct SceneryGroundSurfaceProfile* profile = &sceneryGroundProfiles[mid];",
        "        if (crc == profile->crc && primary == profile->primary && secondary == profile->secondary)",
        "            return sceneryGroundMasks[profile->pattern];",
        "        if (crc != profile->crc ? crc < profile->crc :",
        "            primary != profile->primary ? primary < profile->primary : secondary < profile->secondary)",
        "            hi = mid;",
        "        else lo = mid + 1;",
        "    }",
        "    return NULL;",
        "}",
        "",
        "static int sceneryGroundSurfaceContains(const uint32_t* mask, int metatile) {",
        "    return (unsigned)metatile < SCENERY_GROUND_ID_LIMIT &&",
        "           ((mask[(unsigned)metatile / 32] >> ((unsigned)metatile & 31u)) & 1u);",
        "}",
    ]
    return "\n".join(lines) + "\n", len(profiles), len(patterns)


def make_review_sheets(visual, output):
    output.mkdir(parents=True, exist_ok=True)
    labels = []
    for index, (signature, image) in enumerate(sorted(visual.items())):
        page, tile = divmod(index, 56)
        if tile == 0:
            sheet = Image.new("RGB", (768, 7 * 82), (37, 41, 47))
            draw = ImageDraw.Draw(sheet)
        x, y = (tile % 8) * 96, (tile // 8) * 82
        sheet.paste(image.resize((64, 64), Image.Resampling.NEAREST), (x, y))
        draw.text((x + 2, y + 64), str(index + 1), fill="white")
        labels.append({"number": index + 1, "signature": signature})
        if tile == 55 or index == len(visual) - 1:
            sheet.save(output / f"review-{page + 1:02}.png")
    (output / "review-cells.json").write_text(json.dumps(labels, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, default=Path("work"))
    parser.add_argument("--allowlist", type=Path,
                        default=Path(__file__).with_name("scenery-profiles") / "android-ground-surface-source.json")
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--review-sheets", type=Path)
    args = parser.parse_args()
    visual = {} if args.review_sheets else None
    rows = audit(args, visual)
    header, profiles, masks = generate_header(rows)
    counts = Counter(row["decision"] for row in rows)
    by_game = {game: dict(Counter(row["decision"] for row in rows if row["game"] == game))
               for game in sorted({row["game"] for row in rows})}
    included = [row for row in rows if row["decision"] == "include"]
    summary = dict(exact_tileset_pairs=profiles, packed_masks=masks, counts=dict(counts), by_game=by_game,
                   source_appearances=len({row["source_signature"] for row in rows if "source_signature" in row}),
                   included_source_appearances=len({row["source_signature"] for row in included}),
                   included_outdoor_placements=sum(row["outdoor_placements"] for row in included),
                   qualified_on_thor=False)
    args.header.write_text(header, encoding="utf-8", newline="\n")
    args.report.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2) + "\n", encoding="utf-8")
    if args.review_sheets:
        make_review_sheets(visual, args.review_sheets)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
