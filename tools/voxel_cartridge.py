"""Cartridge-only entry point for a payload built with FireRed3DS's pack format."""

import json
from pathlib import Path

from firered3ds_builder.build import Payload, build_pack
from firered3ds_builder.cartridge import build_cartridge
from firered3ds_builder.recipe import Recipe
from firered3ds_builder.rom import load_rom
from firered3ds_builder.web import STAGES, describe

ROOT = Path("/fr3ds")
PACK = Path("/sd/3ds/firered3ds/firered3ds.pak")
OUTPUT = Path("/out.3ds")


def run(rom_path, progress):
    payload = Payload(ROOT / "payload")
    try:
        recipe = Recipe.load(payload.recipe)
        rom_path = Path(rom_path)
        rom = load_rom(rom_path, (recipe.rom_sha1,))

        def report(fraction, message):
            stage = STAGES.get(message.partition(": ")[0], "data")
            progress(stage, fraction, message)

        info = build_pack(rom_path, payload, PACK, report, runner="inprocess", rom=rom)
        info.pop("payload")
        info["romSha1"] = rom.sha1
        return json.dumps({"ok": True, "result": info})
    except Exception as exc:
        return json.dumps({"ok": False, "error": describe(exc)})


def assemble():
    build_cartridge(ROOT / "cartridge-template.gz", PACK,
                    ROOT / "payload/firered3ds.recipe", OUTPUT)
