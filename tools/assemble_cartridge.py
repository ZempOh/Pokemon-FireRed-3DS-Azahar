#!/usr/bin/env python3
"""Assemble a standalone FRLG+ cartridge from matching CI artifacts and a local ROM."""

import argparse
import gzip
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "builder"))

from firered3ds_builder.build import Payload, build_pack
from firered3ds_builder.cartridge import build_cartridge, pack_slot, verify_engine_abi
from firered3ds_builder.recipe import Recipe


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--template", type=Path, required=True, help="cartridge-template.3ds from CI")
    parser.add_argument("--payload", type=Path, required=True, help="payload directory from the matching builder ZIP")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = Payload(args.payload.resolve())
    recipe = Recipe.load(payload.recipe)
    template = args.template.read_bytes()
    verify_engine_abi(template, recipe.engine_abi)
    *_, offset, size = pack_slot(template)
    if any(memoryview(template)[offset:offset + size]):
        parser.error("the cartridge template must have an empty pack slot")

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".frlg-plus-", dir=output.parent) as tmp:
        work = Path(tmp)
        compressed = work / "template.3ds.gz"
        compressed.write_bytes(gzip.compress(template, compresslevel=1))
        pack = work / "firered3ds.pak"
        build_pack(args.rom.resolve(), payload, pack)
        cartridge = work / output.name
        build_cartridge(compressed, pack, payload.recipe, cartridge)
        cartridge.replace(output)
    print(output)


if __name__ == "__main__":
    main()
