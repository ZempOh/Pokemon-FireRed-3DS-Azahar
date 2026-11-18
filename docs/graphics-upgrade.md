# Graphics upgrade validation (2026-11-18)

## FireRed battle pacing follow-up — Thor verified

### Cadence and scope

The baseline is the original published build for steady selection and the
withheld scanline-only V1 for the controlled blink and input scenes.

| Scene | PROF / PACE windows | Before minimum drawn FPS | Candidate minimum drawn FPS | Candidate game FPS range |
| --- | --- | ---: | ---: | ---: |
| Steady move selection | 12 / 5 | 58.6 | 59.8 | 59.8–59.9 |
| Held blinking battle text | 6 / 3 | 59.5 | 59.8 | 59.8–59.9 |
| Controlled Fight/Back input | 12 / 5 | 58.0 | 59.7 | 59.8 |

Steady reported work-window median: **12.645 → 9.100 ms**. This is 28.0% lower reported elapsed work.

The first potentially partial aggregate is excluded independently for each
counter, then the first requested complete windows are retained. Steady and
interaction each use 12 PROF/5 PACE windows; blink uses 6/3. PROF spans 300
logical game frames and PACE spans 600. Blink holds the encounter text for
45 seconds without input/screenshots. Interaction uses 52 alternating A/B
inputs 1.5 seconds apart over 78 seconds, opening Fight and returning, with
no attacks or screenshots. The unchanged gate requires every candidate PACE
window to reach at least 59.6 drawn FPS, game FPS between 59.6 and 60.0, and
at least 10% lower steady reported work.

Same Thor/Azahar setup and Route 1 fixture, with voxel field/battle enabled. V4 uses Charmander level 6 at 21 HP versus Rattata level 3, matching the original steady baseline and V1 controlled blink/interaction matchup. Retain first 12 complete 300-frame PROF and 5 complete 600-frame PACE windows for idle/interaction, 6/3 for 45-second blink. First potentially partial aggregates independently excluded. Fixed 52 alternating A/B inputs every 1.5 seconds over 78 seconds, with no screenshots or attacks in controlled intervals. Actual moves and field return independently reviewed.

### Actual gameplay, audio and installed bytes

- Fresh full V4 cartridge installed and pulled back from Thor; SHA-256 matches the exact same-run candidate.
- Charmander level 6 at 21/21 HP versus Rattata level 3: held Wild appeared text, repeated Fight/Back and steady selection pass quantitative gates.
- Growl selected and PP reduced to 39/40; opponent Tail Whip text displayed; move labels, types and PP remain clear.
- Three Scratch turns showed progressive opponent damage and own HP changes from 21/21 to 16/21 then 11/21, followed by Rattata fainting and return to Route 1.
- Party screen agrees at 11/21 HP; standard three-pocket Bag and empty Items/Cancel screen render correctly after battle.
- Active Azahar audio tracks advanced with zero endpoint underruns across all four measured phases.

Inspected all 14 raw PACE rows, including the first potentially partial one: drawn 59.7-59.8, game 59.8-59.9. Thirteen complete retained PACE windows have drawn minimum 59.7, median 59.8 and game 59.8 throughout. The 139.33-second capture includes Growl, opponent Tail Whip, three Scratch turns, HP damage, knockout, UI screenshots and field return. Its mixed callbacks are not used as the steady comparison. Audio endpoint counters remain zero with advancing stable track identity. No retained reported-work frame exceeds 16.715 ms; work counts are not dropped-frame counts. No blanket locked-60 claim.

After all three retests, the original 18 save/settings/diagnostic paths were restored and reverified with binary-safe checks. All four installed executable/data files were pulled back and matched their qualified candidates.
These are limited Thor scene checks, not full-playthrough or physical-console
certification.

### Measurement and implementation scope

PROF work is elapsed BeginFrame-to-EndFrame time minus the soft presenter's
recorded FrameBegin wait, clamped to zero. It is elapsed work, not pure CPU
execution time or GPU duration. Each PROF value averages 300 logical game
frames; the summary is the median of those window averages. The queued-upload
change moves FrameBegin before texture uploads. Some synchronization that
previously counted as work can therefore fall inside the excluded wait or
queued GPU execution. The formula is unchanged, but the wait boundary moved:
a dynamic-UI work reduction is not an equal-percentage CPU speedup. Unchanged
steady selection isolates the scanline benefit more closely. Independent
PACE counters measure game and drawn frames over 600 logical frames and
establish cadence; their counting and the frame-skip policy are unchanged.
Sections are inclusive and must not be summed. Hidden frames retain the
pre-existing limitation of subtracting the last renderer wait measurement.
Reported work above the LCD budget is not a count of missed presentations.

The renderer snapshots display/window/blend registers per scanline, builds
a sparse object-window list alongside the existing sprite lists, and uses
the existing constant-mask path for uniform mode-0 windows. Split windows,
affine backgrounds and live HBlank effects retain their general paths.
The lower screen repaints changed header/body/footer bands and copies their
rows; cache flushes still cover whole affected framebuffer columns. Rounded
shapes preserve their pixels while writing contiguous vertical spans.

Top texture uploads run after a successful FrameBegin. UI conversion now
compares source rows, converts only changed rows and coalesces adjacent
dirty-row cache flushes. The full queued 512×512 transfer, texture format,
alpha, filtering and 2× expansion are preserved. Upload buffers are reused
only after FrameBegin completes the preceding GPU work. The game clock,
automatic frame-skip policy, image quality and gameplay are unchanged.

Host checks compare 600 full-only, UI-only and combined scanline passes,
including normal/affine sprites, split/wrapped/object windows, blending,
sprite mosaic and simulated HBlank/VCount register changes. The DMA stub
checks all 160 HBlank dispatch calls; actual destinations were source-audited.
The harness does not execute fully hidden frames, background mosaic or DMA
writes. A separate 602-case review includes live HBlank OAM affine updates.

The lower-screen oracle compares 1,200 old/new rounded-raster cases and 2,003
battle-state transitions against a full repaint. Shapes/layout/dirty decisions
are production code; fonts and icons are deterministic stand-ins. Actual
page/menu invalidation was reviewed in source. The real upload functions
are tested with an asynchronous queue model, exact colour/alpha/expansion/
padding, edge/adjacent/disjoint dirty rows, transparent clear/restore, 100
alternating source buffers, unchanged frames, failed FrameBegin, held UI and
voxel fallback. One changed source row flushes 2,048 upload-buffer bytes;
two separated rows flush 4,096, versus 327,680 for all used rows. These host
checks complement Thor testing; they do not emulate PICA or certify physical
Nintendo 3DS hardware.

FireRed additionally caches 128 glyphs keyed by font and character, storing
canonical indexed pixels/dimensions rather than asset pointers or RGB colours.
Font spacing remains live. Small-font hits reproduce only the two left-tile
scratch writes; the other bytes retain their previous contents. The cache
clears at initialization and game reset. Upstream font assets are immutable.

The dedicated regression compares 9,572 full canvases, widths, complete
glyph-scratch states and printer palettes against uncached rendering. It uses
existing upstream Latin font PNGs and extracted production conversion,
decompression and text functions; temporary arrays are never published.
All 256 byte glyphs in four fonts, cold/warm hits, clipping, controls,
collisions and resets are covered. Japanese rendering is outside this path;
the wrapper always selects Latin. A twelve-character centered label needs
24 uncached decompressions, eight cold cached and zero across 100 warm
repeats. These call counts are not a Thor speedup measurement. Deliberate
mutations that overwrite the untouched small-font scratch bytes or disable
cache hits fail the test. Both native build CI and graphics CI run it.

### Exact build provenance

| Artifact | Identity |
| --- | --- |
| Binary-producing commit | `5c31e6edc68a9baeee4fec5c51a7ca8386d6fa20` |
| Raw blank engine SHA-256 | `b24047b350b4ec1790271cc17ebd79ea03414880dd3a777de58fa6f133ef4701` |
| Web payload ZIP SHA-256 | `328819dfded9fa21b15571f00927821600b85ead56fdb13ade1ab9e91fa66a7b` |
| Private cartridge SHA-256 | `4093854f7506d14a599d9da40a3bbf62f3bfde09ded6f0ca23e72650ed453f19` |
| Data ABI | `fd2785b3` |
| Matching engine and recipe run | [44398302950](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44398302950) |

The cartridge was freshly generated from this matching same-run recipe
and compared with the installed bytes. Private hashes identify local test
cartridges; ROMs, saves and generated packs are not published. Current browser
installs use the [shared voxel builder](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/voxel.html).

### Withheld V2 and V3 history

Queued uploads/lower redraws in V2 (`a2c0963`) reached 59.2 minimum drawn FPS
in controlled Fight/Back input. V3 dirty-row UI conversion (`59768aa`) reached
59.5, with median 59.7; both failed the unchanged 59.6 gate and were withheld.
The V3 work-window median was 9.360 ms, peak 18.21 ms. Repeated input spent
6.6–6.7 ms in the lower screen even without top uploads, leading to the glyph
cache change. Six logged work frames exceeded the LCD budget; that is not a
dropped-presentation count. The scanline-only V1 history follows.

### Scanline-only v1 evidence — historical

The software scanline compositor snapshots display/window/blend registers
per scanline, builds a sparse object-window sprite list alongside the
existing normal-sprite lists, and uses the existing constant-mask path for
uniform mode-0 windows. Split windows, affine backgrounds and live HBlank
effects retain their general rendering paths. Image quality, game logic,
the game clock and the automatic frame-skip policy are unchanged.

The scanline-only candidate was tested on AYN Thor with Azahar
2126.2-googleplay. Both steady samples used the same Route 1 save, Charmander
level 6 at 21/21 HP, settings, voxel battle mode and move-selection phase.
The opponent was Rattata level 3 before and Zigzagoon level 3 after; this is
a comparison of the same scene type, not an identical replay. The first
potentially partial aggregate was discarded independently for each counter,
then the first 12 complete PROF windows and five complete PACE windows were
retained in both revisions. Each PROF window spans 300 logical game frames;
each PACE window spans 600.

| Retained steady-selection metric | Before | Scanline-only v1 |
| --- | ---: | ---: |
| Median of reported work-window averages | 12.645 ms | 9.440 ms |
| Median of scanline-window averages | 9.58 ms | 6.24 ms |
| Largest reported work peak in retained windows | 20.07 ms | 15.59 ms |
| Median drawn FPS | 58.7 | 59.8 |
| Minimum drawn FPS | 58.6 | 59.8 |
| Game FPS in every retained PACE window | 59.8 | 59.8 |

Reported work decreased 25.3%; every retained candidate PACE window reached
59.8 drawn FPS. This passed the idle thresholds of 10% lower reported
work and at least 59.6 drawn FPS in every retained window, but the later
active dips mean the broader pacing fix is not qualified. Active battle
coverage was a separate visual/gameplay check: Growl executed and reduced
its PP to 39/40, Scratch damaged Zigzagoon, the battle Bag opened and closed,
and Run displayed “Got away safely” before returning to Route 1. Party then
showed Charmander at 10/21 HP, matching the battle. Move categories and PP
remained readable. This candidate check did not include a knockout. The
active Azahar track advanced with 0→0 underruns during both idle and active
segments; system-wide mixer counters were excluded. Original device state
was restored and checked with binary-safe hashes after all three retests.

`work` is elapsed BeginFrame-to-EndFrame time minus the renderer's recorded
FrameBegin wait in `3ds_soft_video.c`, clamped to zero. It includes
FrameEnd, synchronous uploads before FrameBegin in v1, and other blocking
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
exercise fully hidden frames, background mosaic or DMA writes. A separate
602-case review also checked live HBlank OAM affine-parameter writes,
including normal and object-window sprites whose output visibly changed.
Both renderers matched byte for byte. OAM geometry is populated in VBlank;
the slot-machine HBlank affine updates remain live per scanline.

| Withheld scanline-only artifact | Provenance |
| --- | --- |
| Binary-producing commit | `39f698b5a47a2278f2088596af6b2e0a7df09dd3` |
| Matching build and recipe | [44377144384](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44377144384) |
| Raw blank engine SHA-256 | `7c3e70e968c68a5b7c19883d7f6d2cdc4b2adea76eecfa67a57c640b20039284` |
| Web payload ZIP SHA-256 | `9c43076daa1ae1ff53a9acb4d3c1c5eae165bd40b284a72286e0f36abe5eec26` |
| Private Thor cartridge SHA-256 | `df81d7d09868424b6a49db0427b0723ce3a6282508a0a0d1a01bc0e96d272a3d` |

The installed cartridge was pulled back and matched the candidate exactly.
The hashes above identify a local test candidate, not a published pacing fix.
The later follow-up and its separate build identities are documented above. ROMs, saves and generated game data are not published.

## Initial preview validation — historical

The sections below preserve the initial graphics-preview observations,
limitations and artifact hashes. The qualified follow-up above records newer
test evidence; the published build has not yet been replaced.

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
