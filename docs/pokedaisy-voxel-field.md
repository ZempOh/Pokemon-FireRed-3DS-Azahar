# PokéDaisy voxel overworld preview

This Android build uses PokéDaisy 1.6.1 and accepts your existing GBA ROMs.
It adds a per-game **Voxel 3D** switch under **Settings → Screen**. Turning
it on selects Expand and activates the live projection in eligible overworld
scenes. The camera uses the game's tiles, elevation and sprite layers.
Menus, battles and unsupported display effects use the standard view.
Party, Bag and Map use the GBA session's existing companion profiles.

| ROM | CRC32 | SHA-1 |
| --- | --- | --- |
| Let's Go Pikachu, English translation | `25c3d89f` | `62bb900925118796fb963b7df92d02cb548c404e` |
| Radical Red 4.10 | `fba55dd8` | `964f951a0fdaf209e4ea1344883ef0d557bb3a80` |
| Pokémon Unbound 2.1.1.1 | `4b3d4957` | `b4776b82a4c7915d0fadeaa27e013523f99dfd94` |

## Install the test build

1. Open the [voxel preview workflow](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/workflows/pokedaisy-profiles.yml?query=branch%3Apokedaisy-voxel-field).
2. Download the `pokedaisy-voxel-preview` ZIP from a successful run and extract
   the APK. The package ID is `com.pokedaisy.app.voxelpreview`. The app has
   its own library and save directory.
3. Install and open **PokéDaisy Voxel Preview**. Import your ROM and, if
   desired, a copy of your battery save. Turn on **Voxel 3D** in Settings.
4. Walk a few tiles to activate the companion. On the lower screen, check
   the starter in Party, a known item in Bag, and the location in Map.
   Enter a building and a battle, then return to the overworld. Toggle the
   setting off to compare the original Expand view.
