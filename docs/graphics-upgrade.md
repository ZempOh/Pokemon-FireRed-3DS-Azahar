# Graphics upgrade validation (2026-11-18)

## FRLG+ battle pacing follow-up — Thor verified

The software scanline compositor snapshots display/window/blend registers
per scanline, builds a sparse object-window sprite list alongside the
existing normal-sprite lists, and uses the existing constant-mask path for
uniform mode-0 windows. Split windows, affine backgrounds and live HBlank
effects retain their general rendering paths. Image quality, game logic,
the game clock and the automatic frame-skip policy are unchanged.

The candidate passed the focused AYN Thor retest with Azahar
2126.2-googleplay. Both steady samples used the same Route 1 save, Bulbasaur
level 6 at 22/22 HP, settings, voxel battle mode and move-selection phase.
The opponent was Rattata level 4 before and level 3 after; this is a
comparison of the same scene type, not an identical replay. The first
potentially partial aggregate was discarded independently for each counter,
then the first 12 complete PROF windows and five complete PACE windows were
retained in both revisions. Each PROF window spans 300 logical game frames;
each PACE window spans 600.

| Retained steady-selection metric | Before | Qualified build |
| --- | ---: | ---: |
| Median of reported work-window averages | 12.660 ms | 9.265 ms |
| Median of scanline-window averages | 9.62 ms | 6.16 ms |
| Largest reported work peak in retained windows | 20.12 ms | 15.60 ms |
| Median drawn FPS | 59.0 | 59.8 |
| Minimum drawn FPS | 58.7 | 59.8 |
| Game FPS in every retained PACE window | 59.8 | 59.8 |

Reported work decreased 26.8%; every retained candidate PACE window reached
59.8 drawn FPS. This passed the preregistered minimum of 10% lower reported
work and at least 59.6 drawn FPS in every retained window. Active battle
coverage was a separate visual/gameplay check: Growl lowered Attack, Tackle
damaged and defeated Rattata, and the game returned to Route 1. Party then
showed Bulbasaur at 12/22 HP, matching the battle. Categories and PP remained
readable. The five Bag pockets remained present, with Potion under Medicine.
The active Azahar track advanced with 0→0 underruns during both idle and
active segments; system-wide mixer counters were excluded.

`work` is elapsed BeginFrame-to-EndFrame time minus the renderer's recorded
FrameBegin wait, clamped to zero. It includes FrameEnd and other blocking
inside presentation, so it is not pure CPU or GPU execution time. Hidden
frames use the renderer's most recent wait measurement; both revisions use
the same profiler code. Section timings are inclusive and must not be
summed. `lines` covers software scanline composition and HBlank callbacks/
DMA. Cadence comes from the independent PACE counters, not a count of work
values above 15 ms. These results do not establish zero stutter in every
move, map or later-game scene; no active-phase timing improvement is claimed.

The build workflow runs 600 pixel-differential cases against the original
compositor: full-only, UI-only and combined passes, normal/affine sprites,
wrapped/split/object windows, blending, sprite mosaic and simulated
HBlank/VCount register updates. The DMA stub checks 160 HBlank dispatches;
actual DMA destinations were reviewed in source. This harness does not
exercise fully hidden frames, background mosaic or DMA writes.
A separate 602-case review also checked live HBlank OAM affine-parameter
writes, including normal and object-window sprites whose output visibly
changed. Both renderers matched byte for byte. OAM geometry is populated in
VBlank; the slot-machine HBlank affine updates remain live per scanline.

| Qualified artifact | Provenance |
| --- | --- |
| Binary-producing commit | `e175dd3116da8ccdaec23df5eaa695dabb3077eb` |
| Matching build and recipe | [44377149759](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44377149759) |
| Raw blank engine SHA-256 | `f0cacb359bc2fc92bcc84b14901bfdd6b5b9893241548aacb5a600da761f89ec` |
| Web payload ZIP SHA-256 | `ce346c23ffb5314ca192f9bff8d129996cd280df8376f0584b5906edfff3826a` |
| Private Thor cartridge SHA-256 | `1ef165e9fe38203ca2164b4f07faae8d39585de7c4d5abd2a8be986f19ef177b` |

The installed cartridge was pulled back and matched the candidate exactly.
Use the [ground and pacing fixes bundle](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/releases/download/graphics-upgrade-2026-11-18/VoxelGraphics-Ground-Pacing-Fixes-2026-11-18.zip)
with your own matching ROM. It supersedes the earlier FRLG+ payloads; keep
the engine and recipe from the same build. Private cartridge hashes are
comparison identifiers only; ROMs, saves and generated game data are not
published. Subsequent documentation-only commits retain this built code.

## FRLG+ Bag follow-up — Thor verified

The November 18 follow-up corrects the main Bag to five pockets: Items,
Medicine, Key Items, Held Items and Balls. Its state arrays, touch IDs and
bounds checks now match those five pockets; TM Case and Berry Pouch retain
their separate screens.

On the AYN Thor, every tab was selected without a crash. Medicine displayed
Potion ×1 with the correct icon and description. Key Items displayed Berry
Pouch and TM Case; Held Items and Balls were empty. Party displayed Bulbasaur
level 6 at 22/22 HP before battle. A level 3 Pidgey was defeated with Tackle,
and the game returned to Route 1. The Potion was then used at 16/22 HP and
consumed, leaving Medicine empty. Host label/order and touch-boundary tests
also passed. These results cover the affected Bag and battle-return flow;
they do not certify every item action or every map. This earlier build
predates the battle-pacing follow-up above.

| Follow-up artifact | Provenance |
| --- | --- |
| Binary-producing commit | `cf8ffae795e54800373f627821cfdb24e3642274` |
| Build workflow | [44362744670](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44362744670) |
| Raw blank cartridge engine SHA-256 | `6187341598230e975a3fdff6f04641a142a0cca5e1196afa29355836955042bf` |
| Private Thor-tested cartridge SHA-256 | `0243012eb9a584625f97cfddace53a85ed83082b5a156f4d7d8528d4432a5bc8` |

Use [VoxelGraphics-Native-Fixes-2026-11-18.zip](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/releases/download/graphics-upgrade-2026-11-18/VoxelGraphics-Native-Fixes-2026-11-18.zip)
and the [follow-up test report](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/releases/download/graphics-upgrade-2026-11-18/native-fixes-report-2026-11-18.md).
The original build-kit/source ZIPs and their hashes remain the initial
preview snapshot. Their FRLG+ contents are superseded by this follow-up.
FireRed and the Android APK are unchanged by this correction. The private
cartridge hash is provided for local comparison only; no ROM, save or
generated game-data pack is published.

## Initial preview validation — historical

Everything below records the initial graphics-preview builds, including
the original Medicine-label and Classic forest/PP observations, timings,
commits and hashes. Those tables are preserved as an as-built record; use
the follow-up results and hashes above for the corrected FRLG+ build. The
Classic follow-up result is documented separately in the follow-up report.

## Rendering paths

PokéDaisy reads the CRC-selected live mGBA session: map grid/VMap and connected-map layouts, tileset metatiles, VRAM tile pixels and palette RAM, then camera-matched snapshots and gSprites/OAM. `pk_wide.c` selects the eligible field projection; `pk_wide_voxel.h` projects textured terrain and depth-tested sprite pixels. `EmulatorEngine` applies the game's settings on the emulation thread through `MgbaCore` and JNI. The existing compositor handles battle, text, menu, unsupported effects, and transitions. Companion telemetry still reads this same core; no secondary emulator or imported companion snapshot was introduced.

The native FireRed/FRLG+ ports use `voxel_world.c` to resolve current and connected maps through the asset pack; atlas, relief, building and mesh modules turn these into GPU geometry. `voxel_entities.c` supplies live sprites; `voxel_camera.c` supplies the follow camera. `ctr_voxel.c` draws terrain, depth-ordered entities, shadows, lighting and particles through Citro3D. The ordinary video compositor and bottom UI continue to own text, menus and transitions. Classic uses the Emerald-derived variant with its own camera edge handling, weather and day/night implementation. Its runtime structures are not interchangeable with FireRed's.

## Changes

- PokéDaisy resolves sprite overlap after projection, with original OAM order as an equal-foot tie-breaker, instead of discarding pixels against a pre-projection sprite mask. Terrain-contact shading preserves nearest-neighbor samples.
- FireRed and FRLG+ use a constant camera distance across connected maps, matching Classic's existing boundary policy. Unconnected interiors retain their size-dependent framing.
- Climate is opt-in and defaults to Original. Automatic uses the local calendar (March-May spring, June-August summer, September-November autumn, December-February winter); its cosmetic weather has a deterministic daily schedule. Manual exposes season and Original/Clear/Rain/Snow/Fog. Reduced is the default particle detail.
- Settings are stored by ROM CRC in PokéDaisy and in each native title's separate settings directory. No encounters, collision, scripts, battle rules or save layouts were changed.
- Interiors, underground native maps, battles and native weather suppress added effects. PokéDaisy's existing field eligibility guards preserve text and scripted display effects. Preset changes fade out before the next preset fades in.

## Thor verification and scope

Tested on AYN Thor with Azahar 2126.2-googleplay and Android package `com.pokedaisy.app.voxelpreview`. All six passed the early-game graphics smoke checks listed below. These results do not certify every map, bridge, reflection, scripted effect, or late-game scene. Climate defaults to Original and effect detail to Reduced. No gameplay or save-format changes were made.

| Game | Device coverage | Live lower-screen coverage | Remaining limitations |
| --- | --- | --- | --- |
| FireRed 3DS | Cold Continue; Pallet/Route 1; home entry/exit; Sentret battle and return; voxel off/on; all 20 manual season/weather combinations, Automatic, Original and persistent settings | Charmander level 7; Potion x1; Pallet/Route 1 map | Battle draw pacing is below a locked 60 FPS in some samples; no complete bridge/reflection survey |
| FRLG+ 1.5.1 | Cold Continue; Pallet/Route 1; lab entry/exit; Rattata level 3 defeated with Bulbasaur; voxel off/on; all 20 combinations, Automatic, Original and persistent Winter/Snow/Full | Bulbasaur level 6; newly obtained Potion x1; map changes to Route 1 | Inherited native Bag labels use FireRed's three-pocket layout: Medicine appears under Key. Wider pocket compatibility is not certified. Battle draw pacing has dips |
| Classic 1.5.1 | Cold Continue; Pallet/Route 1; lab entry/exit; Rattata defeated, Pikachu level 6 to 7, return; voxel off/on; all 20 combinations, Automatic, Original and persistence | Pikachu level 7; Potion x1 in Medicine; map | Existing forest gaps, occasional 2D ground speckles and PP-label overlap remain |
| Let's Go Pikachu English | Cold load; Pallet/Route 1; home entry/exit; Pidgey level 3 defeated and return; voxel off/on; all 20 combinations, Automatic, Original and persistence | Pikachu level 5; Potion x1; live Pallet/Route 1 | Settings header uses inherited FireRed profile name. Expanded art uses the existing inferred geometry; no full-map certification |
| Radical Red 4.10 | Cold load; Route 1/Pallet; home entry/exit; final APK Rattata level 3 defeated and return; voxel off/on; all 20 combinations, Automatic and Original | Chikorita level 5, live HP/PP; Potion x1; live route/town map | Occasional late draws; no claim that every hacked display effect projects correctly |
| Unbound 2.1.1.1 | Cold load; Frozen Heights/Route 1; lab/home entry/exit; Gible level 10 rival battle completed and return; voxel off/on; Automatic, Original, persistence and all manual presets | Beldum level 10; Potion x1 in Cube; actual Frozen Heights/Route 1 boundary | Native snow takes precedence. Outdoor preset sweep used the same renderer with diagnostic logging; final APK repeated indoor sweep, Auto outdoors, battle and boundary |

Android same-process switches verified CRC-specific settings: Unbound Manual Winter/Rain did not replace Radical Red Original or Let's Go Automatic. Unbound's incidental map selection of Route 4 was excluded from location evidence; the recorded Route 1 transition is an actual player movement. Native titles use separate native interfaces, not PokéDaisy telemetry.

## Performance

The baseline samples were collected before modifying the renderer. Durations, locations, menus and battle phases differ, so these are observations rather than a controlled benchmark or an improvement claim. Game FPS is distinct from the roughly 118–120 Hz screen refresh. Initial loading and user-paused gaps are not gameplay worst-frame measurements.

| Game | Before | Candidate observations |
| --- | --- | --- |
| FireRed | 517 presentation intervals, mean 16.714 ms | Field typically 59.8 game/drawn FPS; field callback median 2.73 ms (includes transitions); battle callback median 11.69 ms, peak 25.80 ms, draw samples around 59.1–59.8 |
| FRLG+ | Field callback median 2.55 ms, 59.8 game/drawn FPS | Field callback median 2.56 ms, 59.8 game/drawn; battle median 12.05 ms, peak 25.03 ms; drawn 56.9–59.6 while game stayed 59.8 |
| Classic | Field callback median 2.61 ms; field/menu mix, not matched battle | Final field median 2.35 ms; battle median 5.34 ms, peak 13.82 ms; game samples roughly 59.7–59.9 |
| Let's Go | 58.7–59.3 FPS, average work 3.6–3.9 ms | Final Route 1 sample median 59.0 FPS, work 4.8 ms; 58.8–59.5 FPS, peak work 20.7 ms; 29 late draws across 31 logged intervals |
| Radical Red | About 59.0 FPS, work 4.0–4.2 ms | Final field median 59.0 FPS / 4.35 ms; battle 59.1 FPS / 2.7 ms; peak work 24.2 ms; 32 field late draws across 84 intervals, zero across 29 battle intervals |
| Unbound | 59.0–59.1 FPS, work 4.2–4.5 ms; short baseline had 31 and 22 late draws in two intervals | Final retained field log: median 59.0 FPS / 3.8 ms, range 58.7–59.7, peak 26.8 ms; 4 late draws across 589 intervals |

All retained Android gameplay samples reported zero audio underruns. Native active audio-track counters remained zero before/after the sampled runs (FireRed track 1102, FRLG+ 1122, Classic 1108); system-wide idle mixer counters are not attributed to the games. Native logs include slow frames during startup, transitions and battle; no locked-60 or zero-stutter claim is made. Original is the default; Reduced bounds cosmetic particle cost. Full was exercised on the device, but use Reduced if pacing degrades.

## Exact build provenance

| Runtime | Built code | Successful workflow | Public binary SHA-256 |
| --- | --- | --- | --- |
| FireRed | `a091bf9` | [44339347416](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44339347416) | Blank template `b679acc8239de17c871e38bda3d92e1908ae5dff6533dfae7158de4a4f533955` |
| FRLG+ | `3ef95df` | [44339473321](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44339473321) | Blank template `c63e2d4fddf129ffbdc4d3bbaa2975403dec3c40d099f71727b3ad2cf9d0e258` |
| Classic | `36225ee` | [44342010430](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44342010430) | 3DSX `fbbd64dc0ac9891a746889510f2451f2ebc3840f29ca08d1ab934543d1123041` |
| PokéDaisy | `9b26ce4` | [44341672959](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44341672959) | APK `d0bd911ee83c9e7bc5d4d79e1fa4d2b5df1ee001bcc5ccdfad0ce56079b541a6` |

Later source commits add test wiring and documentation only. The incorrect generic FireRed workflow on the FRLG branch was canceled, and its branch trigger removed. Its artifacts were never used for the staged site.

The staged shared builder was served on a fresh local port and all three games were built in Chrome from local ROMs. FireRed and FRLG+ cartridges matched the installed candidates byte for byte; Classic's engine and data pack both matched. A separate full host rebuild from each web archive produced the same results. A stale server on an older port was detected by its ABI/hash and excluded.

Private comparison hashes (no game data is published): FireRed cartridge `2cc1f058b24462f2c71a8b2a3debcc14108dc6f5e10a3b26ae3aca59e9d6360b`; FRLG+ cartridge `ef052cff9d9a97ca370e64adf2fc51cbf4b9dd481b06f7f6180f911aaba3a8ed`; Classic pack `ac693e3c972bfde9b82ed5576b02073abda8b39767730b0a710812e076d2d4b3`.

## Reproduce and regression checks

Native branches contain `graphics-tests.yml`: it compiles the actual climate header against all presets, tests native-weather precedence and, for FireRed/FRLG+, extracts and exercises the actual camera distance function. All pass locally. Existing native build workflows reproduce the pinned upstream trees, templates and matching extraction recipes. Classic's separate Emerald-derived layout remains isolated.

PokéDaisy's workflow pins upstream `79bd00e155fcc7d4373f23f5386d6e67c8c423eb`, applies patches 0001–0008, checks generated profiles and maps, and runs projection-depth/OAM-tie, terrain contact, bounds and climate tests before assembling the APK. The final patch contains no diagnostic climate logging. JNI settings changes run on the emulation thread.

Use the recipes with your own matching ROMs. The shared site's public packages contain generators, recipes and blank engines, never ROMs, saves or generated game-data packs. Local playable packages must not be uploaded. The preview APK uses a cached debug signing key, explicitly supplied to Gradle; cache retention is not a durable production signing guarantee. Back up/export saves before replacing an older preview that has a different signer. No signing key is included in source or release assets.
