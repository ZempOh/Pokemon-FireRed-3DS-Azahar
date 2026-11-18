# FireRed & LeafGreen+ Voxel for Azahar

This branch ports FireRed & LeafGreen+ v1.5.1 to native Nintendo 3DS with a voxel overworld and a touchscreen Party, Bag, and Kanto map. The standalone cartridge runs in Azahar on Android. It uses its own title ID and saves under `sdmc:/3ds/frlg-plus-voxel/`.

## Build and install

Use a locally patched FireRed & LeafGreen+ v1.5.1 GBA ROM. The matching ROM SHA-1 is `c34a4401f2fe86c515fc6d9a6d231224a98f55d5`. The cartridge builder reads the ROM locally.

1. From a successful [FRLG+ native build](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/workflows/frlg-port.yml?query=branch%3Avoxel-frlg-plus), download `frlg-plus-cartridge-template` and `frlg-plus-cartridge-recipe` from the same run.
2. Unzip the template artifact. Open the release ZIP inside the recipe artifact and extract its `payload` directory.
3. From this branch checkout, assemble a cartridge with Python 3.12 or later.

   ```sh
   python tools/assemble_cartridge.py --rom frlg-plus.gba \
     --template cartridge-template.3ds --payload payload \
     --output FRLGPlusVoxel.3ds
   ```

4. Copy `FRLGPlusVoxel.3ds` to the folder Azahar scans and launch it. Close Azahar before replacing an existing cartridge.

## Play on the Thor

Voxel 3D starts enabled with fresh settings. Tap **3D** on the lower-screen map to switch views. The lower-screen gear opens camera and battle presentation settings. Open Party or Bag on the lower-screen dock, or press **Start** and select one with the D-pad and **A**.

The [Thor test notes](docs/frlg-plus-thor-testing.md) cover the cold launch, first rival battle, lower-screen controls, and Pallet Town sprite fix.

## Build from source

The [native workflow](.github/workflows/frlg-port.yml) pins the devkitARM container, produces the blank cartridge, and verifies the v1.5.1 GBA identity before generating the matching recipe. For a local native toolchain, follow the workflow steps with devkitARM, makerom, a host C/C++ compiler, libpng, Python and Pillow.

```sh
python3 tools/bootstrap.py --dir build/upstream
make -C build/upstream -j4 tools
make -C build/upstream -j4 generated
make -C build/upstream/3ds_port -j4 PYTHON=python3 cartridge-template
```

## Related branches

- [FireRed 3DS on the Thor](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/tree/thor-rendering-tuning)
- [Pokémon Classic Voxel](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/tree/voxel-pokeclassic)
- [PokéDaisy GBA companion profiles](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/tree/pokedaisy-hack-profiles)

PokéDaisy's GBA companion runs the GBA edition in its own emulator. The Azahar cartridge provides its own live touchscreen UI.

## Credits

[FireRed & LeafGreen+](https://github.com/Deokishisu/FRLG-Plus) by Deokishisu and contributors. This port builds on [NachoGonzalez2001's Pokémon FireRed 3DS](https://github.com/NachoGonzalez2001/Pokemon-FireRed-3DS) and [ZallaxDev's Pokémon Emerald 3DS Dual Screen](https://github.com/ZallaxDev/pokeemerald-3Ds-dualscreen). See [NOTICE.md](NOTICE.md) for licenses and upstream credits.

## Graphics upgrade

See [rendering paths, controls and validation status](docs/graphics-upgrade.md). The graphics preview passed the documented early-game Thor checks. Climate remains opt-in; see the per-game limitations and exact tested build hashes.
