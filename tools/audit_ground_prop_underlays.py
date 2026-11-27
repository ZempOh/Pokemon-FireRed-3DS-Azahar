"""Prove a reviewed ground replacement matches a prop's native lower layer."""

import argparse
import hashlib
import json
from pathlib import Path

from scenery_inputs import resolve_input
from scenery_inventory import MapArt


def lower_entries(art, cell):
    split = art.numbers["metatiles"]
    tileset, local = (art.primary, cell) if cell < split else (art.secondary, cell - split)
    return art.read(art.word(tileset + 12) + local * art.numbers["size"], 8)


def rgba_digest(image):
    return hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()


def audit(workspace, profile):
    rom, inventory = resolve_input(workspace, profile["game"], profile["rom_sha256"])
    art = MapArt(rom)
    primary = int(profile["primary"], 16)
    prop, ground = profile["id"], profile["ground"]
    uses = []
    for pair in inventory["tileset_pairs"]:
        count = pair["used_metatiles"].get(hex(prop), 0)
        if int(pair["primary"], 16) != primary or not count:
            continue
        art.setup(inventory["numbers"], primary, int(pair["secondary"], 16))
        assert lower_entries(art, prop) == lower_entries(art, ground), pair["secondary"]
        assert all(not layer.getbbox() for layer in art.layers(ground)[1:]), pair["secondary"]
        assert rgba_digest(art.image(prop)) == profile["source_sha256"], pair["secondary"]
        assert rgba_digest(art.image(ground)) == profile["ground_sha256"], pair["secondary"]
        uses.append({"secondary": pair["secondary"], "mapped_cells": count})
    assert uses, f"No mapped cells for {profile['game']} prop {hex(prop)}"
    return {
        "game": profile["game"],
        "rom_sha256": profile["rom_sha256"],
        "primary": profile["primary"],
        "prop": hex(prop),
        "ground": hex(ground),
        "uses": uses,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    path = Path(__file__).with_name("scenery-profiles") / "android-ground-props.json"
    profiles = json.loads(path.read_text(encoding="utf-8"))
    results = [audit(args.workspace, profile) for profile in profiles if "ground_sha256" in profile]
    assert results, "No profiles with a verified native underlay"
    payload = json.dumps(results, indent=2)
    if args.report:
        args.report.write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
