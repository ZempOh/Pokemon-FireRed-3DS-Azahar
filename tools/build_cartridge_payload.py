#!/usr/bin/env python3
"""Prepare the browser cartridge assets from the paired native build outputs."""

from __future__ import annotations

import argparse
import gzip
import tempfile
from pathlib import Path

from build_site import payload_from_zip
from build_web_payload import build
from firered3ds_builder.cartridge import pack_slot, verify_engine_abi
from firered3ds_builder.recipe import Recipe


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--windows-zip", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    template = bytearray(args.template.read_bytes())
    _, _, _, _, slot, capacity = pack_slot(template)
    if any(memoryview(template)[slot:slot + capacity]):
        raise SystemExit("Refusing to publish a cartridge containing game data")

    with tempfile.TemporaryDirectory() as tmp:
        payload = payload_from_zip(args.windows_zip, Path(tmp))
        verify_engine_abi(template, Recipe.load(payload / "firered3ds.recipe").engine_abi)
        build(payload, "0.5.1", args.out)
    output = args.out / "cartridge-template.gz"
    with output.open("wb") as file, gzip.GzipFile(fileobj=file, mode="wb", mtime=0, filename="") as archive:
        archive.write(template)
    print(f"Cartridge template verified with an empty {capacity:,} byte RomFS slot")


if __name__ == "__main__":
    main()
