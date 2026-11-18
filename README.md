# Pokémon Classic Voxel for Azahar

This branch ports Pokémon Classic v1.5.1 to Nintendo 3DS with a voxel overworld, an optional voxel battle view, and touchscreen Party, Bag, and Map. It uses a dedicated save directory at `sdmc:/3ds/pokeclassic-voxel/`.

## Build status

Build `e6531b5` passed the November 18 AYN Thor retest in Azahar. Route 1's repeated forest now has continuous ground and canopy, and the move-category icons render cleanly beside PP. The retest covered cold Continue, walking along the forest edges, special and status move selection, a completed wild battle, return to Route 1, and the live Party panel. [Thor results and exact build hashes](docs/pokeclassic-thor-testing.md)

The physical category passed the host regression; it was not available on the device test Pokémon. The earlier climate survey was not repeated in this focused retest. Historical tests also covered Oak's capture, the first rival battle, and the other touchscreen panels.

## Build and install

Use the [shared builder](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/voxel.html) or download the [native fixes bundle](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/releases/download/graphics-upgrade-2026-11-18/VoxelGraphics-Native-Fixes-2026-11-18.zip). This bundle supersedes the initial graphics-preview downloads' FRLG+ and Classic contents. Keep each engine together with its matching recipe.

Use your local Pokémon Classic v1.5.1 GBA ROM, SHA-1 `7e27a7878d6aeb3b798757f98e60d1064d762dbb`. The game data pack is rebuilt from that ROM on your device.

1. From [Thor-tested build 44364733602](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44364733602), download `pokeclassic-voxel-engine` and `pokeclassic-voxel-recipe`. Always pair artifacts from the same [Classic Actions run](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/workflows/ci.yml?query=branch%3Agraphics%2Fazahar-classic). Extract the two engine files, `emerald3ds.recipe`, and the `voxelgen` directory together into `payload`.
2. Run the builder from the branch checkout with Python 3.13 and Pillow.

   ```sh
   PYTHONPATH=builder python -m emerald3ds_builder --payload payload build \
     --rom pokeClassic.gba --output classic-install
   ```

3. Copy `classic-install/3ds` into the `sdmc` folder of your Azahar user directory. Open `3ds/pokeclassic-voxel/Emerald3DS.3dsx` with Azahar. You can also put the launcher in Azahar's scanned games folder. The data pack and saves use the same `sdmc:/3ds/pokeclassic-voxel/` directory.

The output file names retain the original engine's naming convention. This branch accepts the exact Classic ROM above.

## Controls

Voxel 3D starts enabled with fresh settings. On the lower screen, open **Option → World → 3D** to toggle voxel mode and adjust the camera. The **Battle** tab controls voxel battle scenery. Use the lower-screen dock or **Start** and the D-pad to open Party and Bag.

## Source builds

The [CI workflow](.github/workflows/ci.yml) runs the host tests, assembles the native engine, and audits its shipping files. On a recipe build it also rebuilds the pinned GBA source, verifies its SHA-1, creates the extraction recipe, and checks the data pack assembled from it. Work on the native changes through `patches/pokeclassic/` and `3ds_port/`. `tools/bootstrap.py` applies the patches in order to the pinned source in `upstream.lock`.

## Related branches

- [FireRed 3DS on the Thor](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/tree/thor-rendering-tuning)
- [FireRed & LeafGreen+ Voxel](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/tree/voxel-frlg-plus)
- [PokéDaisy GBA companion profiles](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/tree/pokedaisy-hack-profiles)

PokéDaisy reads the GBA edition inside its own emulator. The Azahar port provides its own native lower-screen interface.

## Credits

[Pokémon Classic](https://github.com/DaniRainbow/pokeclassic) by danenders/LazyDev, DaniRainbow, and contributors. The native engine and voxel renderer come from [ZallaxDev's Pokémon Emerald 3DS Dual Screen](https://github.com/ZallaxDev/pokeemerald-3Ds-dualscreen). See [NOTICE.md](NOTICE.md) for the port's source and licenses.

## Graphics upgrade

See the [initial graphics report and Classic followup](docs/graphics-upgrade.md). Its original tables preserve the earlier builds, performance samples, and limitations; the followup records the forest and PP corrections. Climate remains opt-in. These early-game checks do not certify every map or effect.
