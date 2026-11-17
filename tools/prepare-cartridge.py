"""Package a blank native cartridge template and its matching web recipe."""

import argparse
import gzip
import sys
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="native port source checkout")
    parser.add_argument("--template", type=Path, required=True, help="blank cartridge-template.3ds")
    parser.add_argument("--recipe-zip", type=Path, required=True, help="paired build artifact ZIP")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--code", required=True)
    args = parser.parse_args()

    sys.path.insert(0, str(args.source.resolve() / "tools"))
    from build_site import payload_from_zip
    from build_web_payload import collect, manifest_bytes, sha256, write_zip
    from firered3ds_builder.cartridge import pack_slot, verify_engine_abi
    from firered3ds_builder.recipe import Recipe

    template = bytearray(args.template.read_bytes())
    *_, slot, capacity = pack_slot(template)
    if any(memoryview(template)[slot:slot + capacity]):
        raise SystemExit("The cartridge template already contains game data.")

    with tempfile.TemporaryDirectory() as tmp:
        payload = payload_from_zip(args.recipe_zip, Path(tmp))
        recipe = Recipe.load(payload / "firered3ds.recipe")
        verify_engine_abi(template, recipe.engine_abi)
        files = collect(payload)
    files["python/voxel_cartridge.py"] = Path(__file__).with_name("voxel_cartridge.py").read_bytes()
    compressed = gzip.compress(template, compresslevel=9, mtime=0)
    manifest = {
        "schemaVersion": 1,
        "kind": "voxel-cartridge-payload",
        "releaseTag": recipe.release,
        "dataAbi": f"{recipe.engine_abi:08x}",
        "entrypoint": {"pythonPath": "python"},
        "supportedRoms": [{"sha1": recipe.rom_sha1, "code": args.code, "name": args.name}],
        "cartridgeSha256": sha256(compressed),
        "files": [{"path": key, "sha256": sha256(data), "size": len(data)}
                  for key, data in sorted(files.items())],
    }
    args.out.mkdir(parents=True, exist_ok=True)
    write_zip(args.out / "FireRed3DS-WebPayload.zip", files, manifest)
    (args.out / "web-manifest.json").write_bytes(manifest_bytes(manifest))
    (args.out / "cartridge-template.gz").write_bytes(compressed)
    print(f"Built {recipe.release}, ABI {recipe.engine_abi:08x}, {len(files)} payload files")


if __name__ == "__main__":
    main()
