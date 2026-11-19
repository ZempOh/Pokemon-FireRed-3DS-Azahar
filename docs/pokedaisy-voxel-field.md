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

The [native-clock follow-up](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44421988072)
passed fresh Thor checks with all three listed ROMs. Patch 0009 corrects the
Let’s Go settings title, uses the native GBA clock at normal speed, keeps audio
writes nonblocking with bounded buffer rate control, and waits at most one
cartridge frame before reusing a pending video frame. Fast-forward retains its
existing refresh grouping and overwrite behavior.

Across nine final field, battle, and active-battle phases, the measured
120-frame windows held 59.6–59.8 FPS with zero unshown frames, dropped audio
samples, or audio underruns. Field and steady battle phases were 65 seconds;
active phases were 90 seconds. Battles and overworld returns were verified.
These are targeted early-game checks, not a full-playthrough guarantee.

- APK SHA-256: `2467e8063f73030ac745e2e449fb6f34c67a60503cffb242ad22dc785065a68a`
- Patch/workflow commit: `18259de0421456a50ed695ec94da50dab30b3d5f`
- [Measured results, rejected candidates, method and limits](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/android-pacing.html)
- [Six-game lossless screenshots and gameplay GIFs](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/gallery.html)

The earlier [initial validation](graphics-upgrade.md) remains historical context.
The shared [voxel builder](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/voxel.html)
also provides the three separately tested native Azahar titles.
