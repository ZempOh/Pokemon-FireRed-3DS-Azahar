# Shared voxel cartridge builder

The catalog is at `voxel.html`. `voxel-catalog.json` lists each game's display name and required ROM. An entry becomes buildable when it has both a `base` directory and an `output` filename.

The original FireRed entry uses the existing `cartridge-fps` payload. For a port with a compatible recipe and cartridge format, use the matching recipe ZIP and blank template from the same build.

```powershell
$release = '../frlg-guard-test'
python tools/prepare-cartridge.py --source ../voxel-frlg-plus --template "$release/cartridge-template.3ds" --recipe-zip "$release/FireRed3DS-v1.5.1-Windows.zip" --out voxel/frlg-plus/payload --name 'FireRed & LeafGreen+ v1.5.1' --code BPRE
```

The packager checks the template's empty RomFS data slot and matching engine ABI. The browser checks the package files and template hashes, and the builder checks the user's ROM fingerprint and generated pack before producing a cartridge. The published assets are the manifest, recipe, generators, and blank template. Perform builds from a local HTTP server before publishing and boot the resulting cartridge in Azahar.

## Release the shared builder

1. Verify the exact FRLG+ cartridge and Classic engine/data pair on the Thor. For Classic, reach the first battle with voxel graphics enabled and open the party, bag and map.
2. Copy the verified Classic release's matching `Emerald3DS-WebPayload.zip` and `web-manifest.json` to `voxel/pokeclassic/payload/`. Set its catalog entry's `base` to `voxel/pokeclassic/`, its `format` to `homebrew` and its `output` to `PokeClassicVoxel-SD.zip`.
3. Serve the worktree with `python -m http.server 8091 --bind 127.0.0.1`. Build both titles from their matching ROMs at `http://127.0.0.1:8091/voxel.html`. Compare the FRLG+ output hash with the tested cartridge and compare Classic's ZIP members with the tested engine, icon and PAK. The Classic ZIP installs under `3ds/pokeclassic-voxel/`.
4. Review the staged diff and commit the catalog, manifests and release payloads. Do not add ROM files, saves, data packs, completed cartridges or test ZIPs to the site branch.
5. Fetch the deployed branch and verify the local release is a fast-forward with `git merge-base --is-ancestor origin/gh-pages HEAD`. After both games pass, publish with `git push origin HEAD:gh-pages`. Confirm the deployed catalog and both payload manifests load on [GitHub Pages](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/voxel.html).
