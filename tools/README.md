# Shared voxel cartridge builder

The catalog is at `voxel.html`. `voxel-catalog.json` lists each game's display name and required ROM. An entry becomes buildable when it has both a `base` directory and an `output` filename.

The original FireRed entry uses the existing `cartridge-fps` payload. For a port with a compatible recipe and cartridge format, use the matching recipe ZIP and blank template from the same build.

```powershell
python tools/prepare-cartridge.py --source ../voxel-frlg-plus --template ../frlg-engine/cartridge-template.3ds --recipe-zip ../frlg-recipe/FireRed3DS-v1.5.1-Windows.zip --out voxel/frlg-plus/payload --name 'FireRed & LeafGreen+ v1.5.1' --code BPRE
```

The packager checks the template's empty RomFS data slot and matching engine ABI. The browser checks the package files and template hashes, and the builder checks the user's ROM fingerprint and generated pack before producing a cartridge. The published assets are the manifest, recipe, generators, and blank template. Perform builds from a local HTTP server before publishing and boot the resulting cartridge in Azahar.

Classic needs its own verified packager inputs. If it uses a different native pack format, provide a payload-specific `python/voxel_cartridge.py` implementing `run(rom_path, progress)` and `assemble()`. The worker expects the final image at `/out.3ds`.
