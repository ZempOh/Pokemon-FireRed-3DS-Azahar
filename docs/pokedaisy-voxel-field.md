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

1. Download the [tested Android APK](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/releases/tag/pokedaisy-voxel-preview-v1).
   The package ID is `com.pokedaisy.app.voxelpreview`, with its own library
   and save directory.
2. Install and open **PokéDaisy Voxel Preview**. Import your ROM and, if
   desired, a copy of your battery save. Turn on **Voxel 3D** in Settings.
3. Walk a few tiles to activate the companion. On the lower screen, check
   the starter in Party, a known item in Bag, and the location in Map.
   Enter a building and a battle, then return to the overworld. Toggle the
   setting off to compare the original Expand view.

If Android reports a signing mismatch with an earlier test APK, back up
the preview app’s saves before replacing that preview package. The workflow
uses a debug signing key generated on its runner.

## AYN Thor validation

The [successful Android build](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44322760489)
was installed and tested using the Thor’s built-in screens. Each game
loaded into projected terrain and displayed its party, one Potion, and its
live location on the lower screen.

| Game | Party | Map |
| --- | --- | --- |
| Let’s Go Pikachu | Pikachu | Pallet Town and Route 1 |
| Radical Red | Chikorita | Route 1 |
| Pokémon Unbound | Beldum | Shadow Base and Frozen Heights |

During preview testing, Radical Red returned to the voxel overworld after
a wild encounter, and Unbound’s first double battle was completed. On the
release APK, switching from an enabled game to one with the toggle off
correctly returned to the standard Expand view in the same app process.
