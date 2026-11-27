"""Check stable flower palette slots against the exact private ROM artwork."""

import argparse
import hashlib
import json
from pathlib import Path
from struct import unpack

from scenery_inputs import resolve_input
from scenery_inventory import MapArt


def source_slot(art, entries, x, y):
    quadrant = y // 8 * 2 + x // 8
    for layer in range(len(entries) // 4 - 1, -1, -1):
        entry = entries[layer * 4 + quadrant]
        px = (x & 7) ^ (7 if entry & 0x400 else 0)
        py = (y & 7) ^ (7 if entry & 0x800 else 0)
        offset = (entry & 1023) * 32 + py * 4 + px // 2
        ink = (art.tiledata[offset] >> (4 * (px & 1))) & 15
        if ink:
            return (entry >> 12) * 16 + ink
    return 0


def audit(workspace, profile):
    rom, inventory = resolve_input(workspace, profile["game"], profile["rom_sha256"])
    source = MapArt(rom)
    numbers = inventory["numbers"]
    primary = int(profile["primary"], 16)
    cell = profile["id"]
    assert cell < numbers["metatiles"], "Profiled flower must belong to the primary tileset"
    size = numbers["size"]
    entries = unpack("<" + "H" * (size // 2), source.read(source.word(primary + 12) + cell * size, size))
    pairs = [
        pair for pair in inventory["tileset_pairs"]
        if int(pair["primary"], 16) == primary and pair["used_metatiles"].get(hex(cell), 0)
    ]
    assert pairs, f"No mapped uses of {profile['game']} flower {hex(cell)}"
    colors = None
    for pair in pairs:
        source.setup(numbers, primary, int(pair["secondary"], 16))
        art = source.image(cell).convert("RGBA")
        assert hashlib.sha256(art.tobytes()).hexdigest() == profile["source_sha256"], pair["secondary"]
        slots = [source_slot(source, entries, x, y) for x, y in zip(profile["ink"][::2], profile["ink"][1::2])]
        assert slots == profile["palette_inks"], (profile["game"], pair["secondary"], slots)
        actual = [source.palette[slot] for slot in slots]
        if colors is None:
            colors = actual
        assert colors == actual, pair["secondary"]
    return {
        "game": profile["game"],
        "rom_sha256": profile["rom_sha256"],
        "primary": profile["primary"],
        "metatile": cell,
        "mapped_tileset_pairs": len(pairs),
        "palette_slots": profile["palette_inks"],
        "palette_rgb": colors,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    path = Path(__file__).with_name("scenery-profiles") / "android-ground-props.json"
    profiles = json.loads(path.read_text(encoding="utf-8"))
    results = [audit(args.workspace, profile) for profile in profiles if "palette_inks" in profile]
    assert results, "No profiles with stable flower palette slots"
    payload = json.dumps(results, indent=2)
    if args.report:
        args.report.write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
