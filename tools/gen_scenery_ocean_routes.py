"""Scan exact GBA inputs for outdoor ocean-route map headers."""
import argparse
from collections import Counter
import json
from pathlib import Path
from zlib import crc32

from scenery_inputs import resolve_input
from scenery_inventory import MapArt

MAP_TYPE_OCEAN_ROUTE = 6


def read_ocean_routes(work):
    capabilities = Path(__file__).with_name("scenery-profiles") / "android-capabilities.json"
    routes = []
    for profile in json.loads(capabilities.read_text(encoding="utf-8")):
        game = profile["game"]
        rom, inventory = resolve_input(work, game)
        art = MapArt(rom)
        crc = f"{crc32(art.data):08x}"
        if crc != profile["rom_crc32"]:
            raise ValueError(f"Cartridge changed for {game}")
        for pair in inventory["tileset_pairs"]:
            for item in pair["maps"]:
                header = int(item["header"], 16)
                weather, map_type = art.read(header + 0x16, 2)
                if map_type == MAP_TYPE_OCEAN_ROUTE:
                    layout = art.word(header)
                    if (layout != int(item["layout"], 16) or art.word(layout) != item["width"]
                            or art.word(layout + 4) != item["height"]):
                        raise ValueError(f"Stale source map header for {game}: {item}")
                    routes.append({"game": game, "crc": crc, "group": item["group"], "map": item["map"],
                                   "header": item["header"], "native_weather": weather})
    return routes


def header_source(routes):
    lines = ["// Exact cartridge ocean-route metadata. Regenerate with gen_scenery_ocean_routes.py.",
             "#pragma once", "#include <stdint.h>", "",
             "static int sceneryOceanRoute(uint32_t crc, int group, int map) {",
             "    if ((unsigned)group > 255 || (unsigned)map > 255) return 0;",
             "    int key = group * 256 + map;",
             "    switch (crc) {"]
    for crc in sorted({row["crc"] for row in routes}):
        keys = [row["group"] * 256 + row["map"] for row in routes if row["crc"] == crc]
        if len(keys) != len(set(keys)):
            raise ValueError(f"Duplicate ocean route for {crc}")
        lines += [f"    case 0x{crc}:",
                  "        return " + "\n            || ".join(f"key == 0x{key:04x}" for key in sorted(keys)) + ";"]
    lines += ["    default:", "        return 0;", "    }", "}", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, default=Path("work"))
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    routes = read_ocean_routes(args.work)
    if not routes:
        raise ValueError("No verified ocean-route headers")
    summary = {"routes": len(routes), "by_game": Counter(row["game"] for row in routes),
               "native_weather_ids": Counter(row["native_weather"] for row in routes)}
    args.header.write_text(header_source(routes), encoding="utf-8", newline="\n")
    args.report.write_text(json.dumps({"summary": summary, "routes": routes}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
