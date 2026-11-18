# Graphics upgrade validation (2026-11-18)

## Rendering paths

PokéDaisy reads the CRC-selected live mGBA session: map grid/VMap and connected-map layouts, tileset metatiles, VRAM tile pixels and palette RAM, then camera-matched snapshots and gSprites/OAM. `pk_wide.c` selects the eligible field projection; `pk_wide_voxel.h` projects textured terrain and depth-tested sprite pixels. `EmulatorEngine` applies the game's settings on the emulation thread through `MgbaCore` and JNI. The existing compositor handles battle, text, menu, unsupported effects, and transitions. Companion telemetry still reads this same core; no secondary emulator or imported companion snapshot was introduced.

The native FireRed/FRLG+ ports use `voxel_world.c` to resolve current and connected maps through the asset pack; atlas, relief, building and mesh modules turn these into GPU geometry. `voxel_entities.c` supplies live sprites; `voxel_camera.c` supplies the follow camera. `ctr_voxel.c` draws terrain, depth-ordered entities, shadows, lighting and particles through Citro3D. The ordinary video compositor and bottom UI continue to own text, menus and transitions. Classic uses the Emerald-derived variant with its own camera edge handling, weather and day/night implementation. Its runtime structures are not interchangeable with FireRed's.

## Candidate changes

- PokéDaisy resolves sprite overlap after projection, with original OAM order as an equal-foot tie-breaker, instead of discarding pixels against a pre-projection sprite mask. Terrain-contact shading preserves nearest-neighbor samples.
- FireRed and FRLG+ use a constant camera distance across connected maps, matching Classic's existing boundary policy. Unconnected interiors retain their size-dependent framing.
- Climate is opt-in and defaults to Original. Automatic uses the local calendar (March-May spring, June-August summer, September-November autumn, December-February winter); its cosmetic weather has a deterministic daily schedule. Manual exposes season and Original/Clear/Rain/Snow/Fog. Reduced is the default particle detail.
- Settings are stored by ROM CRC in PokéDaisy and in each native title's separate settings directory. No encounters, collision, scripts, battle rules or save layouts were changed.
- Interiors, underground native maps, battles and native weather suppress added effects. PokéDaisy's existing field eligibility guards preserve text and scripted display effects. Preset changes fade out before the next preset fades in.

## Baseline and release gate

The connected device is AYN Thor `fa17bd72`; Azahar is `2126.2-googleplay` (package `io.github.lime3ds.android`). The Android preview is `com.pokedaisy.app.voxelpreview`. Original saves/states and settings were copied locally before testing. ROMs and saves must never be staged or attached to releases.

Initial short PokéDaisy samples, before changes: Let's Go 58.7-59.3 FPS, 3.6-3.9 ms average frame work; Radical Red 59.0 FPS, 4.0-4.2 ms; Unbound 59.0-59.1 FPS, 4.2-4.5 ms. All logged zero audio underruns in these samples. Unbound logged late draws (31 and 22 in two 120-frame intervals) and activated its slow-frame pacing guard. These are short baseline observations, not complete movement/battle certification. Thor's display runs at approximately 120 Hz; presentation refresh counts must not be reported as game FPS.

FireRed's initial release presentation sample contained 517 intervals averaging 16.714 ms. Native cold boot, field, transition and battle counters must be compared separately: boot-time asset loading otherwise dominates worst-frame timing.

No candidate is approved for publication until all requested device checks pass. Build success and host tests alone are insufficient. The shared site remains on the previous verified releases until a matching artifact hash is recorded here.

## Companion coverage

PokéDaisy profiles: Let's Go Pikachu English translation, Radical Red 4.10, Unbound 2.1.1.1 — Party, Bag/Cube and Map read the live GBA session. Verify an actual party member, Potion (or another known item), and a location change on the lower screen in each game, including a same-process switch.

Azahar titles use their native lower-screen interfaces rather than PokéDaisy telemetry. FireRed/FRLG+ and Classic expose native Party, Bag and Map; coverage and regression results must be recorded separately.

## Repeatable checks

For each title: disposable save copy, cold boot, movement through adjacent maps, building entry/exit, battle and return, voxel off/on, every manual season and weather, Original restoration, per-game settings isolation, and representative before/after screenshots. Capture game FPS, frame-work/slow-frame counters, presentation intervals and audio-underrun deltas for the same route. Keep failures associated with the title and location. Only verified binaries may replace site artifacts.
