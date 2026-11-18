# PokéDaisy companion profiles

This branch builds **PokéDaisy Dev** from PokéDaisy 1.6.1 with profiles for two
specific GBA ROMs. Each profile identifies its ROM by SHA-1. Use your own
patched ROMs. The APK and GitHub Actions artifacts contain the app and profile
metadata.

| Game | GBA ROM SHA-1 | Validation |
| --- | --- | --- |
| Pokémon Classic v1.5.1 | `7e27a7878d6aeb3b798757f98e60d1064d762dbb` | In live GBA memory, the profile reads the starter, Pallet Town and Route 1, and one Potion in the Medicine pocket. |
| Pokémon FireRed & LeafGreen+ v1.5.1 | `c34a4401f2fe86c515fc6d9a6d231224a98f55d5` | In live GBA memory, the profile reads the starter, the first rival battle, Pallet Town and Route 1, and one Potion in the Medicine pocket. Use the English v1.5.1 patch for FireRed Rev 0. |

PokéDaisy 1.6.1 also recognized the installed English Let's Go Pikachu,
Radical Red 4.10, and Unbound 2.1.1.1 builds on the Thor. Let's Go Pikachu
showed its live party and map and opened the bag. Radical Red and Unbound
reached their introductions. On-device verification of the two new
profiles in PokéDaisy Dev is pending.

## Install and verify on Android

1. Download the `pokedaisy-profile-dev` artifact from the latest successful
   build and extract `app-dev.apk`. [GitHub Actions builds](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/workflows/pokedaisy-profiles.yml?query=branch%3Apokedaisy-hack-profiles)
2. Install the APK by opening it on Android or run
   `adb install -r app-dev.apk` from a connected PC. Its package ID is
   `com.pokedaisy.app.dev`, with a separate library and save directory.
3. Launch **PokéDaisy Dev**, import the two matching `.gba` files, and check
   that the library recognizes both games. If you need existing progress,
   import a copy of the corresponding GBA save.
4. Start each game and check that **Party** shows the starter and **Map**
   follows the move from Pallet Town to Route 1. Collect the free Route 1
   Potion and check that **Bag** shows one Potion in Medicine.

APK builds made on fresh CI runners can have different development signing
keys. If Android reports a signature mismatch while updating PokéDaisy Dev,
back up the dev app's saves before uninstalling it and installing the new APK.

## Voxel 3D ports

The native 3DS ports run in Azahar. Launch their native files from the
Azahar library and use the game's own lower-screen controls for Party, Bag,
Map, and the 3D toggle. PokéDaisy Dev's profiles read the GBA games running
inside PokéDaisy.

| Branch | Build and verification |
| --- | --- |
| `main` | FireRed 3DS and its published browser builder. [FireRed project README](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/tree/main) |
| `voxel-frlg-plus` | FireRed & LeafGreen+ native build, including the Pallet Town rendering fix. The Thor test covered the first rival battle and the lower-screen Party, Bag, and Map. [FRLG+ native workflow](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/workflows/frlg-port.yml?query=branch%3Avoxel-frlg-plus) · [Thor test notes](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/blob/voxel-frlg-plus/docs/frlg-plus-thor-testing.md) |
| `voxel-pokeclassic` | Pokémon Classic native engine and matching data pack pipeline. Full gameplay verification in Azahar is pending. [Classic native workflow](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/workflows/ci.yml?query=branch%3Avoxel-pokeclassic) |
| `pokedaisy-hack-profiles` | PokéDaisy Dev source patches and Android build workflow. |

The shared build site is staged for publication after both native ports
pass gameplay checks in Azahar on the Thor.

## Build from source

The workflow checks out PokéDaisy commit
`79bd00e155fcc7d4373f23f5386d6e67c8c423eb` with submodules, applies the
patches in name order, and regenerates and checks the profile and area map
tables. It uses Java 17, Python 3.12, Android SDK 34, NDK
`28.2.13676358`, and CMake `3.22.1`. [Android build workflow](../.github/workflows/pokedaisy-profiles.yml)

You can use the same steps locally on Linux with those tools installed. Run
them from this branch's checkout.

```sh
git clone --recurse-submodules https://github.com/lidor30/pokedaisy.git
cd pokedaisy
git checkout 79bd00e155fcc7d4373f23f5386d6e67c8c423eb
git submodule update --init --recursive
for patch in ../patches/pokedaisy/*.patch; do
  git apply "$patch" || exit 1
done
python3 scripts/gen_gamedata.py
python3 scripts/gen_gamedata.py --check
python3 scripts/gen_area_maps.py
python3 scripts/gen_area_maps.py --check
./gradlew :app:assembleDev
```

The APK is in `app/build/outputs/apk/dev/`. The app is based on the
[upstream PokéDaisy project](https://github.com/lidor30/pokedaisy/tree/79bd00e155fcc7d4373f23f5386d6e67c8c423eb).
