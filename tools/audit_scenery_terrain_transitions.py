"""Inventory exact map height and ground-material boundaries for GBA review.

The report identifies ROM layouts and placements. It makes no semantic claim
about a cell being a stair, cliff, bridge, or ledge until the art is reviewed.
"""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import struct
import zlib

from scenery_inputs import resolve_input
from scenery_inventory import MapArt


def rise(value, maximum):
    """GBA terrainRise deliberately gives layers 0 and 15 the normal height."""
    layer = value >> 12
    return min(4 * (layer - 1), maximum) if 0 < layer < 15 else 8


def flatten(rows, *fields):
    return [dict(zip(fields, key), placements=count) for key, count in sorted(rows.items())]


def inventory_game(workspace, cap, maximum):
    game = cap["game"]
    rom, inventory = resolve_input(workspace, game)
    art = MapArt(rom)
    crc = f"{zlib.crc32(art.data):08x}"
    assert crc == cap["rom_crc32"]
    id_mask = inventory["numbers"]["mask"]
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
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True, help="Workspace's work directory with private inputs")
    parser.add_argument("--runtime", type=Path, required=True, help="Source snapshot used by the exact renderer")
    parser.add_argument("--games", nargs="+")
    args = parser.parse_args()
    header = (args.runtime / "app/src/main/cpp/pk_wide_voxel.h").read_text(encoding="utf-8")
    maximum = int(re.search(r"^#define VOXEL_MAX_RISE (\d+)$", header, re.MULTILINE)[1])
    caps_path = Path(__file__).resolve().with_name("scenery-profiles") / "android-capabilities.json"
    caps = {r["game"]: r for r in json.loads(caps_path.read_text(encoding="utf-8"))}
    if args.games and (unknown := set(args.games) - set(caps)):
        parser.error("Unknown cartridge profiles: " + ", ".join(sorted(unknown)))
    args.output.mkdir(parents=True, exist_ok=True)
    summary = {}
    for game in dict.fromkeys(args.games or caps):
        cap = caps[game]
        data = inventory_game(args.workspace, cap, maximum)
        path = args.output / f"{cap['game']}.json"
        path.write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")
        summary[cap["game"]] = {
            "crc32": data["crc32"], "map_inventory_holds": len(data["map_inventory_holds"]),
            "maps": sum(len(p["maps"]) for p in data["pairs"]),
            "tileset_pairs": len(data["pairs"]),
            "raw_height_boundary_variants": sum(len(p["boundary_variants"]) for p in data["pairs"]),
            "review_status": "Unclassified source inventory", "inventory": str(path),
        }
        print(cap["game"], summary[cap["game"]]["raw_height_boundary_variants"], flush=True)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
