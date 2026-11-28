"""Generate an exact English FireRed family registry from the audited private ROM digest."""
from pathlib import Path
import argparse
import hashlib
import json

FAMILY = {
    "firered": "dd88761c",
    "frlgplus": "964763c0",
    "ash-gray": "63478921",
    "rocket": "f2d16ebd",
}


def generate(audit, omitted):
    games = audit["games"]
    if any(games[name]["rom_crc32"] != crc for name, crc in FAMILY.items()):
        raise ValueError("Unexpected FireRed family cartridge identity")
    lines = [
        "/* Audited native Kanto fronts for the exact English FireRed family. */",
        "#pragma once",
        "",
        "static const struct BattleFamilyFront {",
        "    uint32_t art, normalPalette, shinyPalette;",
        "    uint8_t y;",
        "} battleFamilyFronts[] = {",
    ]
    fps = set()
    for species in range(1, 152):
        source_rows = [games[name]["rows"][str(species)] for name in FAMILY]
        identity = None
        for row in source_rows:
            front = row["front"]
            normal = row["normal"]
            shiny = row["shiny"]
            if len(front["frames"]) != 1 or normal["palettes"] != 1 or shiny["palettes"] != 1:
                raise ValueError(f"Noncanonical entry at species {species}")
            row_identity = (
                front["sheet_sha256"], normal["colors_sha256"], shiny["colors_sha256"],
                row["coord_bytes"], row["opponent_elevation"], row["single_32px_radius_y"],
                front["frames"][0]["fnv1a32"], normal["live_palette_fnv1a32"], shiny["live_palette_fnv1a32"]
            )
            if identity is not None and identity != row_identity:
                raise ValueError(f"Cartridge-family divergence at species {species}")
            identity = row_identity
        y, front_fnv, normal_fnv, shiny_fnv = identity[5:]
        if front_fnv in fps or not 0 <= y < 48:
            raise ValueError(f"Front fingerprint collision or unsupported y for species {species}")
        fps.add(front_fnv)
        if species not in omitted:
            lines.append(f"    {{0x{front_fnv}u, 0x{normal_fnv}u, 0x{shiny_fnv}u, {y}}}, // species {species}")
    lines.append("};")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--omit", type=int, action="append", default=[])
    args = parser.parse_args()
    data = args.audit.read_bytes()
    if any(not 1 <= i <= 151 for i in args.omit):
        parser.error("--omit takes native Kanto IDs 1 through 151")
    args.output.write_text(generate(json.loads(data), set(args.omit)), encoding="utf-8", newline="\n")
    print(f"{151-len(set(args.omit))} entries from source audit SHA-256 {hashlib.sha256(data).hexdigest()}")
