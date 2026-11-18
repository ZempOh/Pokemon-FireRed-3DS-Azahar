# FireRed & LeafGreen+ Voxel for Azahar

This branch ports FireRed & LeafGreen+ v1.5.1 to native Nintendo 3DS with a voxel overworld and a touchscreen Party, Bag, and Kanto map. The standalone cartridge runs in Azahar on Android. It uses its own title ID and saves under `sdmc:/3ds/frlg-plus-voxel/`.

## Build and install

Use a locally patched FireRed & LeafGreen+ v1.5.1 GBA ROM. The matching ROM SHA-1 is `c34a4401f2fe86c515fc6d9a6d231224a98f55d5`. The cartridge builder reads the ROM locally.

For browser installs, open the [shared voxel builder](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/voxel.html), choose
**FireRed & LeafGreen+**, select your matching ROM, then build and download
the `.3ds` cartridge. Close the game in Azahar before copying it into the
folder Azahar scans. Saves and settings remain in Azahar's virtual SD folder.
The browser serves published releases; the CI instructions below pin the
exact qualified build independently of browser rollout.

For the exact Thor-tested build, assemble the matching CI artifacts:

1. From [FRLG+ native build 44390865728](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44390865728), download `frlg-plus-cartridge-template` and `frlg-plus-cartridge-recipe` from that same run.
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

## Battle pacing follow-up — Thor verified

Build `dfb5e4d` reduces scanline and lower-screen redraw work, queues top
uploads inside the GPU frame, and converts only changed UI rows. Game
timing, image quality and frame-skip policy are unchanged.

| Scene | Retained PROF / PACE windows | Before minimum drawn FPS | V3 minimum drawn FPS |
| --- | --- | ---: | ---: |
| Steady move selection | 12 / 5 | 58.7 (original published build) | 59.8 |
| Held blinking battle text | 6 / 3 | 59.5 (withheld v1) | 59.8 |
| Controlled Fight/Back input | 12 / 5 | 58.1 (withheld v1) | 59.7 |

Retained game rates were 59.8–59.9 FPS, with a median of 59.8 in each scene.
Steady reported
work-window median fell from **12.660 to 9.080 ms**. That elapsed-work metric
excludes a wait whose boundary changed, so 28.3% lower reported work is not
an equal-percentage CPU speedup; the independent cadence counters establish
the result.

Bulbasaur used Growl and three Tackle turns, defeated Pidgey and returned to
Route 1. PP, damage, the five Bag tabs, Medicine/Potion and Party HP remained
correct. The separate active segment retained nine complete cadence windows,
with a minimum 59.6 drawn FPS, and active Azahar audio tracks advanced with
zero endpoint underruns. The installed cartridge matched the fresh same-run
build by SHA-256. These are targeted early-game checks, not a whole-game
zero-stutter guarantee.

The scanline-only v1 and queued-upload v2 were withheld after active/menu
cadence failures; their evidence remains in the [test history](docs/graphics-upgrade.md).
See [Thor gameplay checks](docs/frlg-plus-thor-testing.md) and use the
[shared voxel builder](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/voxel.html) for published browser builds.

## Earlier Bag pocket correction — historical Thor checks

The native Bag now follows FRLG+'s five main pockets: **Items**, **Medicine**,
**Key Items**, **Held Items**, and **Balls**. Five compact touch tabs replace
the inherited three-pocket layout. The scroll-state array and touch-ID ranges
cover all five pockets, with a bounds check before indexing pocket state.
The TM Case and Berry Pouch keep their existing separate screens.

The earlier Bag-correction build passed the affected AYN Thor checks: all five tabs could be
selected without a crash; Medicine showed Potion ×1 with the correct icon
and description; Key Items showed Berry Pouch and TM Case; Held Items and
Balls were empty. The live Party showed Bulbasaur level 6 at 22/22 HP before
battle. Bulbasaur defeated a level 3 Pidgey using Tackle and returned to Route
1. Using the Potion after battle at 16/22 HP consumed it, leaving Medicine
empty. The host regression also passes label/order and touch-boundary checks.

The historical [native fixes bundle](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/releases/download/graphics-upgrade-2026-11-18/VoxelGraphics-Native-Fixes-2026-11-18.zip)
contains the Bag-correction source, recipe and blank template. The original
`VoxelGraphics-Public-Build-Kit.zip` and `VoxelGraphics-Source.zip` are the
initial preview snapshots; their FRLG+ contents predate this correction.
Do not mix a new template with an older recipe. Use your own matching local
ROM. See the [follow-up report](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/releases/download/graphics-upgrade-2026-11-18/native-fixes-report-2026-11-18.md)
and [exact build hashes](docs/graphics-upgrade.md#frlg-bag-follow-up--thor-verified).

The earlier Bag-correction binary was built from `cf8ffae795e54800373f627821cfdb24e3642274`
in [run 44362744670](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44362744670).
This is a focused Bag and battle-return retest, not certification of every
item action or later-game scene. The qualified pacing build retains this
correction and repeats the five-pocket, Medicine and Party checks above.

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
