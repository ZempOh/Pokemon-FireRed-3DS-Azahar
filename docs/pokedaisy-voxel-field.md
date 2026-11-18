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

1. Download the [tested Android APK](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/releases/tag/graphics-upgrade-2026-11-18).
   The package ID is `com.pokedaisy.app.voxelpreview`, with its own library
   and save directory.
2. Install and open **PokéDaisy Voxel Preview**. Import your ROM and, if
   desired, a copy of your battery save. Turn on **Voxel 3D** in Settings.
3. Walk a few tiles to activate the companion. On the lower screen, check
   the starter in Party, a known item in Bag, and the location in Map.
   Enter a building and a battle, then return to the overworld. Toggle the
   setting off to compare the original Expand view.

If Android reports a signing mismatch with an earlier preview, export/back up
its battery saves and desired states before replacing that preview package.
This tested APK uses an explicit debug signing identity cached by the build
workflow. Cache retention is not a permanent production-key guarantee.
Do not uninstall an old preview before making a usable backup.

## Graphics controls

Settings → Screen exposes Voxel 3D, Visual Climate (Original, Automatic,
Manual), four seasons, Original/Clear/Rain/Snow/Fog and Reduced/Full detail.
Original and Reduced are the defaults. Settings are stored separately for
each ROM CRC. Indoor maps and native weather take precedence; these are
cosmetic effects and do not change battle weather, encounters or saves.

## AYN Thor validation

The [final build](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44341672959)
was installed and checked on the Thor with all three listed ROMs. See the
[per-game checks, measured performance, limitations and exact hashes](graphics-upgrade.md).
The shared [voxel builder](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/voxel.html)
also provides the three separately tested native Azahar titles.
