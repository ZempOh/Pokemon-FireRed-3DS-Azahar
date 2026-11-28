"""Inventory exact map height and ground-material boundaries for GBA review.

The report identifies ROM layouts and placements. It makes no semantic claim
about a cell being a stair, cliff, bridge, or ledge until the art is reviewed.
"""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
import struct
import zlib

from scenery_inputs import resolve_input
from scenery_inventory import MapArt

NIBBLE_SWAP = bytes((value << 4 & 255) | (value >> 4) for value in range(256))
ART_GROUP_FIELDS = ("map_type", "direction", "height_delta", "first_art", "neighbor_art", "first_flags", "neighbor_flags")


def rise(value, maximum):
    """GBA terrainRise deliberately gives layers 0 and 15 the normal height."""
    layer = value >> 12
    return min(4 * (layer - 1), maximum) if 0 < layer < 15 else 8


def flatten(rows, *fields):
    return [dict(zip(fields, key), placements=count) for key, count in sorted(rows.items())]


def art_signature(art, metatile, tile_cache):
    """Include native layer order, transforms, and all visible palette entries."""
    split, size = art.numbers["metatiles"], art.numbers["size"]
    tileset, local = ((art.primary, metatile) if metatile < split else
                      (art.secondary, metatile - split))
    entries = art.read(art.word(tileset + 12) + size * local, size)
    digest = sha256()
    for entry, in struct.iter_unpack("<H", entries):
        if entry not in tile_cache:
            offset = (entry & 1023) * 32
            data = art.tiledata[offset:offset + 32]
            if len(data) != 32:
                raise ValueError("Truncated native tile")
            strips = [data[y:y+4] for y in range(0, 32, 4)]
            if entry & 1024:
                strips = [row[::-1].translate(NIBBLE_SWAP) for row in strips]
            if entry & 2048:
                strips.reverse()
            pixels = b"".join(strips)
            base = (entry >> 12) * 16
            used = {p >> 4 for p in pixels} | {p & 15 for p in pixels}
            colors = bytes(component for i in sorted(used - {0}) for component in art.palette[base + i])
            tile_cache[entry] = sha256(pixels + colors).digest()
        digest.update(tile_cache[entry])
    return digest.hexdigest()


def group_art(art, primary, secondary, id_mask, variants):
    art.setup(art.numbers, primary, secondary)
    tile_cache, source = {}, {}
    groups = defaultdict(lambda: {"placements": 0, "variants": 0, "example": None})
    for (kind, axis, a, b, delta), row in variants.items():
        if not delta:
            continue
        source_ids = a & id_mask, b & id_mask
        for metatile in source_ids:
            if metatile not in source:
                source[metatile] = art_signature(art, metatile, tile_cache)
        group = groups[kind, axis, delta, source[source_ids[0]], source[source_ids[1]], a & ~id_mask, b & ~id_mask]
        group["placements"] += row["count"]
        group["variants"] += 1
        if group["example"] is None:
            group["example"] = {**row["example"], "cell": hex(a), "neighbor": hex(b)}
    return [dict(zip(ART_GROUP_FIELDS, key), **data) for key, data in sorted(groups.items())]


def accumulate_shared_art(shared, game, pairs):
    for pair in pairs:
        for row in pair.get("exact_source_art_groups", ()):
            key = tuple(row[field] for field in ART_GROUP_FIELDS)
            group = shared[key]
            game_row = group.setdefault(game, {"placements": 0, "source_variants": 0,
                                               "example": {**row["example"], "primary": pair["primary"],
                                                           "secondary": pair["secondary"]}})
            game_row["placements"] += row["placements"]
            game_row["source_variants"] += row["variants"]


def inventory_game(workspace, cap, maximum, include_art=False):
    game = cap["game"]
    rom, inventory = resolve_input(workspace, game)
    art = MapArt(rom)
    crc = f"{zlib.crc32(art.data):08x}"
    assert crc == cap["rom_crc32"]
    art.numbers = inventory["numbers"]
    id_mask = art.numbers["mask"]
    assert not id_mask & 0xf000
    result = {"game": game, "crc32": crc, "source_sha256": inventory["rom_sha256"],
              "map_inventory_holds": inventory.get("failures", []), "pairs": []}
    for tileset in inventory["tileset_pairs"]:
        primary, secondary = (int(tileset[key], 16) for key in ("primary", "secondary"))
        variants = defaultdict(lambda: {"count": 0, "example": None})
        cells = Counter()
        rooms = []
        for row in tileset["maps"]:
            header, layout = (int(row[key], 16) for key in ("header", "layout"))
            width, height = row["width"], row["height"]
            assert art.word(header) == layout
            assert (art.word(layout), art.word(layout + 4)) == (width, height)
            assert (art.word(layout + 16), art.word(layout + 20)) == (primary, secondary)
            mode = art.read(header + 0x17, 1)[0]
            grid = struct.unpack(f"<{width * height}H", art.read(art.word(layout + 12), 2 * width * height))
            changes = 0
            for y in range(height):
                for x in range(width):
                    a = grid[y * width + x]
                    cells[mode, a & id_mask, a >> 12] += 1
                    neighbors = (("east", x + 1, y), ("south", x, y + 1))
                    for direction, other_x, other_y in neighbors:
                        if other_x >= width or other_y >= height:
                            continue
                        b = grid[other_y * width + other_x]
                        if a >> 12 == b >> 12:
                            continue
                        key = (mode, direction, a, b, rise(b, maximum) - rise(a, maximum))
                        record = variants[key]
                        record["count"] += 1
                        changes += 1
                        if record["example"] is None:
                            record["example"] = {"group": row["group"], "map": row["map"], "x": x, "y": y}
            rooms.append({"group": row["group"], "map": row["map"], "map_type": mode,
                          "cells": len(grid), "raw_height_boundaries": changes})
        result["pairs"].append({
            "primary": tileset["primary"], "secondary": tileset["secondary"], "maps": rooms,
            "used_ground_and_structure_ids": flatten(cells, "map_type", "metatile", "raw_layer"),
            "boundary_variants": [dict(map_type=kind, direction=axis, cell=hex(a), neighbor=hex(b),
                                       projected_height_delta=delta, **record)
                                  for (kind, axis, a, b, delta), record in sorted(variants.items())],
        })
        if include_art:
            try:
                result["pairs"][-1]["exact_source_art_groups"] = group_art(art, primary, secondary, id_mask, variants)
            except (ValueError, struct.error) as error:
                result["pairs"][-1]["source_decode_hold"] = str(error)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True, help="Workspace's work directory with private inputs")
    parser.add_argument("--runtime", type=Path, required=True, help="Source snapshot used by the exact renderer")
    parser.add_argument("--games", nargs="+")
    parser.add_argument("--group-art", action="store_true", help="Hash exact source-art pairs for visible height changes")
    args = parser.parse_args()
    header = (args.runtime / "app/src/main/cpp/pk_wide_voxel.h").read_text(encoding="utf-8")
    maximum = int(re.search(r"^#define VOXEL_MAX_RISE (\d+)$", header, re.MULTILINE)[1])
    caps_path = Path(__file__).resolve().with_name("scenery-profiles") / "android-capabilities.json"
    caps = {r["game"]: r for r in json.loads(caps_path.read_text(encoding="utf-8"))}
    if args.games and (unknown := set(args.games) - set(caps)):
        parser.error("Unknown cartridge profiles: " + ", ".join(sorted(unknown)))
    args.output.mkdir(parents=True, exist_ok=True)
    summary = {}
    shared = defaultdict(dict)
    for game in dict.fromkeys(args.games or caps):
        cap = caps[game]
        data = inventory_game(args.workspace, cap, maximum, args.group_art)
        path = args.output / f"{cap['game']}.json"
        path.write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")
        summary[cap["game"]] = {
            "crc32": data["crc32"], "map_inventory_holds": len(data["map_inventory_holds"]),
            "maps": sum(len(p["maps"]) for p in data["pairs"]),
            "tileset_pairs": len(data["pairs"]),
            "raw_height_boundary_variants": sum(len(p["boundary_variants"]) for p in data["pairs"]),
            "review_status": "Unclassified source inventory", "inventory": str(path),
        }
        if args.group_art:
            accumulate_shared_art(shared, game, data["pairs"])
            summary[cap["game"]]["art_groups_in_tileset_pairs"] = sum(len(p.get("exact_source_art_groups", [])) for p in data["pairs"])
            summary[cap["game"]]["source_decode_holds"] = sum("source_decode_hold" in p for p in data["pairs"])
        print(cap["game"], summary[cap["game"]]["raw_height_boundary_variants"], flush=True)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if args.group_art:
        cross_game = [dict(zip(ART_GROUP_FIELDS, key), games=cases) for key, cases in shared.items() if len(cases) > 1]
        (args.output / "shared-art-index.json").write_text(json.dumps({
            "all_exact_art_groups": len(shared), "groups_shared_by_multiple_games": len(cross_game),
            "qualification": False, "groups": cross_game,
        }, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
