# Reusable scenery pipeline

Start with `tools/scenery_profiles.json`, not a fresh line-by-line code survey.
The rollout covers the original six games and the ten additional games in the
expansion manifest. Actors and battle Pokémon are a separate pass.

## Repeatable sequence

1. Run `python tools/scenery_pipeline.py --workspace WORK inventory --output inventory.json`.
   This records active entrypoints and source hashes for all six games. Coverage
   starts unverified; finding a definition does not prove it is rendered.
2. Identify a family using ROM revision plus primary/secondary tileset plus the
   complete metatile pattern. Keep raw ROM atlases local. Add a declarative profile
   and reuse the family geometry; do not guess from collision or green pixels alone.
3. Generate from the player's verified local ROM. Check source projection, opaque
   sides, floor/wall preservation, finite vertices and geometry cost. Match generated
   room tables to their packed texture. Keep caches keyed to source and input hashes.
4. Build once, record commit and artifact SHA-256, take a fresh device backup, then
   run the same field, battle, interactions, season/weather and audio/pacing fixtures
   on the Thor. Retain failures; never rerun unchanged candidates to cherry-pick a pass.
5. Capture 2D/3D, seasonal and interaction media from that exact artifact. Review
   moving views as well as stills. Restore and verify the original device state.
6. Run `gate --candidate BUILD --report qualification.json --output gate.json` after
   the inventory command's global options. The gate rejects changed sources,
   changed artifacts, missing checks, or changed evidence. It does not replace the
   game-specific performance thresholds or human visual review, and never publishes.
7. Publish only eligible artifacts. Update the site, repo and release notes from
   the same qualification manifest, preserving each game's previous passing build.

## Shared geometry rules

Host stages can be expressed once as a JSON recipe and reused:
`run-host --game firered --recipe steps.json --output WORK/run --toolchain COMPILER_VERSION`.
Each stage has `name`, `kind: "host"`, a `commands` list of argument lists,
`inputs` and `outputs`. List all external inputs (local ROM, recipe, reconstructed
tree, build scripts and dependencies) in `inputs`; files and directories are
hashed without uploading their contents. The profile fingerprint covers the
scenery source, not every possible external build dependency.
Available substitutions are `{python}`, `{repo}`, `{workspace}`,
`{output}` and `{game}`. Commands run without a shell; failure stops the recipe.
Successful results are reused only when the source/profile, recipe, command,
toolchain identity and every output hash match. Device stages cannot use this
cache. Keep fixture execution and Thor qualification fresh.

The first shared recipe, `tools/scenery-recipes/native-room-volume.json`, compiles
and checks every generated plant cell for FireRed and FRLG+. It requires the
candidate's volume renderer and test sources. Reusing it for another game requires
an explicit adapter; it rejects games outside its supported list.

- Plants share closed botanical geometry with source-palette materials. Silhouette
  extrusion was rejected after rotating previews exposed striped, flattened sides.
- Preserve source backgrounds separately: grass, water, cliffs, walls and floors
  are different materials. Snow must not turn water or indoor flooring white.
- Movable/breakable objects follow live object position and visibility. Never bake
  them into static terrain or change their collision/interaction rules.
- Keep geometry and recognition separate. New games normally add profiles and
  fixtures, not another renderer implementation.

`tools/scenery-geometry/scenery_plant_geometry.h` is the shared renderer-neutral
botanical family: rounded pot, closed stem and eight solid leaves, 144 triangles,
or a rounded topiary canopy, 128 triangles.
Its adapter receives triangles in pixel units (Y is height), six material indices,
and shading. Native and Android adapters can reuse it with their coordinate and UV
conventions. The CI test checks closed edges, finite coordinates, material bounds
and positive volume. These are geometry checks, not game or Thor certification.

Do not classify by comments alone: Sea Cottage's `0x29c/0x2af` pair was described
as a plant in an old list but its actual artwork is a blue cabinet. Palette/profile
validation caught it. Keep such exclusions explicit and preserve the original asset.

`tools/scenery-profiles/android-potted-plants.json` records nine verified source
patterns across Let's Go, Radical Red and Unbound. The Android adapter matches the
ROM CRC, primary tileset and both metatiles, samples live palette colors, and keeps
the original lower floor/wall layer. Unbound's rounded topiary uses the second
shared shape. These profiles establish recognition, not complete scenery coverage.

## Findings that must not be rediscovered

- Run `tools/scenery_transfer.py --manifest LOCAL/manifest.json --reference
  LOCAL/radical.gba --runtime POKEDAISY/app/src/main/cpp/pk_wide_games.h --output
  report.json` before investigating additional FireRed games. It verifies each
  local ROM hash and compares decoded pixels, transparency, palette and attributes
  for complete asset families. No ROM bytes are exported. Different art or engines
  fail closed; matching numeric IDs or even matching art without an engine mapping
  is insufficient. Regression fixtures cover palette changes, flip bits, attributes,
  secondary ownership and invalid pointers.
- The first expansion candidate adds identical indoor plants to Ash Gray, Gaia,
  Rocket Edition and Odyssey; Rocket also matches the outdoor family. They reuse
  the existing real-clock natural weather, manual weather and season controls.
  This is partial, unqualified support. It does not establish complete winter
  ground, environmental coverage or Thor performance for any new game.
- Fakemon and Better Than Better Emerald 2 pass PokeDaisy's existing retail-engine
  fingerprint proof, which supplies a derived renderer row at runtime. Fakemon
  also passes the exact artwork checks and reuses Rocket's scenery families.
  Better Than Better Emerald 2, Lazarus and Seaglass are climate/terrain candidates.
  Patch 0019 adds reviewed live-object profiles and complete tree patterns. Modern
  Emerald and Dragonsden fail the retail proof; their separate EX engine mappings
  are candidates, not device-qualified builds.
- `tools/scenery-profiles/android-capabilities.json` and the plant profiles generate
  the recognition headers with `tools/gen_scenery_registry.py --output DIR`.
  CI checks these byte-for-byte against the applied patch stack. Adding a game
  normally edits reviewed data, not renderer conditionals. Climate support includes
  the shared 15-minute real-clock fronts, seasonal weights, fades and indoor/native
  weather suppression; candidate support does not establish Thor qualification.

- Classic uses `classic_building_specs.py`; the imported Emerald definitions are
  not its active model list. Its outdoor renderer and indoor path differ from FireRed.
- Classic metatiles can have three layers. Omitting entries 8–11 drops plant leaves
  from extracted artwork; compare the composite against the live atlas/reference
  compositor before building geometry from it.
- FireRed and FRLG+ buildings use `fr_building_specs.py`; indoor objects use
  `fr_gen_rooms.py` and `voxel_room.c`. Editing generic `vb.Card` hooks alone has no
  effect on these active plant paths.
- The checked-in native room table and generated texture are a pair. FRLG+ ROM
  generation differs from vanilla FireRed; identical renderer files do not establish
  matching layouts, masks or UV slots.
- Android profiles require exact supported ROM CRCs and tileset identities.
  Unbound's water-backed conifers need water-preserving erasure; grass replacement
  beneath every conifer is incorrect.
- Preserve the established pacing gates and Reduced-effect-detail qualification
  scope. A passing geometry test or generator is not a Thor pass.

## Qualification record

### Reusable expansion findings

`scenery_inventory.py` inventories bounded map banks, tileset pairs and observed
metatile combinations from hash-verified local ROMs. Optional atlases are local
review inputs, never release screenshots. It supports two/three-layer art and
Modern Emerald's compression bitfield. Preserve and investigate inventory failures.

`android-engines.json`, `android-live-objects.json`, and `android-tree-quads.json`
generate candidate runtime headers; CI checks reproduction. Modern Emerald 3.6
uses EX objects (16-bit graphics ID at +4, sprite ID +35), not vanilla Emerald's
layout. Its exact source compiler gives SaveBlock1 templates/flags/vars at
3428/4964/5264. Dragonsden's fixture verifies EX objects, graphics table 0x08ba3760,
and save templates/flags/vars at 0x16a8/0x1ca8/0x1f6c. Its bank lists are halfword
aligned; do not reinterpret their low bit as an XOR key. It uses 24-byte,
three-layer metatiles. A 16-byte decoder produces plausible but wrong fragments;
verify complete source objects before selecting a profile.

The 38 reviewed live profiles match ROM CRC plus the actual sprite image table,
preserve visibility and movement, and sample the live palette. Let's Go's movable
slot is a metal bin; Rocket's corresponding blank slot stays blank. Source palette
indices preserve Ash Gray's yellow cut-tree canopy. Never infer semantics solely
from a numeric graphics ID.

The 85 complete 2x2 tree patterns cover Better Emerald 2, Seaglass, Lazarus,
Modern Emerald and Dragonsden. Source tiles and palettes must be primary-owned.
Lazarus patterns containing a neighboring canopy are excluded. Ground reconstruction caches one tile instead
of sampling it for every tree pixel. These counts describe partial coverage only.

Required fields: `game`, `build_commit`, `source_sha256`, `artifact_sha256`,
`device: "AYN Thor"`, `claim`, `coverage`, and `checks`. Every check named in the
profile file needs `passed: true` and nonempty `evidence`, each with a path relative
to the report and SHA-256. Use `partial_environment_update` until all families have
passed; `all_environment_assets` additionally requires every family in `coverage`
to be `passed`. Never construct a passing record from unobserved results.

### Dragonsden layout regression

The captured Celadon field matches all 1,800 live BG entries with 24-byte
metatiles and a 640 primary-metatile split; a 512 split scores only 785/1000.
Seven primary palettes match live palette RAM. The EX640 family therefore uses
Emerald u16 attributes and expansion objects with 640 metatiles, seven palettes
and sized borders. A shorter primary array is not evidence of a different global
split: unused primary IDs may remain reserved. Layout byte +24 is border width,
not a version discriminator. Device qualification remains pending.

`android-tall-trees.json` adds 21 reviewed complete 2x3 patterns for Ash Gray,
Gaia and Odyssey. Recognition requires the exact ROM, primary tileset and all six
cells; it reuses the solid tree renderer and verified ground cell. Odyssey's
stacked double-canopy patterns are excluded. This remains partial coverage.

### Night palettes and winter ground

Reviewed full land cells now use semantic recognition for winter coverage, so
blue night palettes do not make known grass lose its snow. Recognition requires
ROM CRC, primary tileset and metatile ID. Unclassified cells retain the color
filter; water, walls and indoor surfaces are not broadly classified as land.
`land` entries in `android-capabilities.json` currently cover the reviewed base
ground in all thirteen Android games, including Dragonsden's separately reviewed
Hoenn and Kanto base ground cells. This does not cover every ground variant.

`tools/scenery_state_probe.py` compares a private mGBA state against local ROM
metatiles. Supply `--rom`, `--state`, `--profiles`, `--game`, `--metatiles`, `--size`
and `--output`. It verifies the ROM hash and exports metadata only. Both Modern
Emerald (512/16) and Dragonsden (640/24) match 1,800/1,800 captured BG entries.
This is an engine diagnostic, not a release qualification.

Dragonsden's corrected source inventory also verifies both base ground cells and
its Kanto tree/grass/shrub/rock/flower family. Capabilities can now specify their
own primary tileset address instead of inheriting FireRed's address. Celadon
(1/6) stores map type NONE despite being outdoors, so an exact reviewed map
override enables climate there; other NONE maps remain unclassified because the
ROM uses that type for interiors too.

Dragonsden uses transparent BG0 tile 530 for empty UI. `textUp` now checks actual
tile transparency, caching visibility per tile for each check. It no longer
mistakes that empty layer for dialogue. Regression checks cover nonzero blank
IDs, real ink, 4/8-bit pixels and VRAM bounds. Actual menus still trigger 2D
fallback. This fix awaits the next exact Thor candidate.

### Interactive object variants

`tools/scenery_object_variants.py` scans map-object scripts against already
reviewed Cut/Strength/Rock Smash graphics. Supply the hash-matched ROM,
inventory, object profiles, template kind and output path. Shared scripts only
produce review candidates: generic scripts can also be used by actors, so this
tool never approves a model automatically. Ambiguous categories are rejected.

Dragonsden has two cut-tree graphics: 82 and 449 share script `082fcbb3` in 33
and 105 map placements respectively. Graphic 449 is the reviewed short Kanto
cut tree, now the 39th live-object profile. Its text interaction was verified on
the Thor. Its template kind byte is +1 and graphics ID is u16 at +2; Modern uses
kind +3 and graphics at +1. The explicit override also fixes offscreen objects.
The batch scan found no additional variants in the other expansion games;
Let's Go and Radical Red still have unapproved script-sharing candidates.

### Ground cells and ledge caps

`tools/scenery_cell_transfer.py` compares individual cells using the existing
layer, transparency, palette, flip and attribute signature. It consumes a
hash-checked local recipe and emits metadata, never automatic profile approval.
This avoids repeating a whole-family investigation when only tree artwork differs.

The reviewed ground registry now contains 289 full land cells across all thirteen
Android games and 43 upper-eight-row ledge caps. `android-ground-review.json`
records the ROM hashes, IDs and review image hashes. The full-cell C1 exclusion
is deliberate: its lower half is a cliff. Gaia reuses D0/D1/D2/D8/D9/DA/E0/E1/E2
for railings or water, and FE/FF/106/107 for props; those are not inherited as
ground. Unbound and Ash Gray use a different 97 ledge, also excluded from the
upper-cap family. Emerald-family water edges 123/125/12B/12C remain excluded.
Map connections use their own primary tileset when selecting ground treatment.
This improves reviewed path coverage; it does not certify every map or asset.

`android-ground-props.json` adds 28 individually reviewed flowers, tall-grass
cells, shrubs and static rocks across eight additional primary tilesets. Grass
D was checked against behavior 2 in each ROM as well as its art. Emerald-family
5 is a planter/window, and Gaia 12 is a tree/cliff fragment: neither inherits a
Kanto shrub or grass model. Flowers use explicit live-palette stem, petal and
center swatches and closed petals. Known prop floors use the same semantic snow
classification as terrain, avoiding bare night-colored patches underneath.

## Exact device evidence across expanded profiles

The Android compositor emits `scenery crc=... rendered=N/300 blocked=...` in
300-call windows. Field, winter and automatic-climate qualification must retain
at least six windows for the expected ROM CRC, with 3D enabled, a known engine,
and actual rendered frames. A static image alone cannot distinguish the shared
renderer from fallback composition. `tools/thor_renderer_evidence.py` parses this
proof; battle/menu fallback is intentional and is not a field-render failure.
The mask records disabled/unknown/centre/battle/overlay/fly/partner/nonfield/
missing-snapshot/missing-previous/text/effect/draw rejection in successive bits.
Counters are diagnostics, not frame cadence or visual-quality approval.

Keep measurement and gallery names keyed to the full candidate identity (a
12-character commit prefix in filenames plus full commit and APK SHA-256 in the
manifest). Never transfer a visual pass from a prior APK. Fixture provenance is
separate: a save loaded successfully may still place its player on water or leave
stale objects. Review source terrain and live movement before using that fixture.
Preserve raw startup logs before process-ID filtering. Verify the same advancing
active audio track at both steady measurement endpoints. Device restoration uses
a dirty marker created on every install/settings mutation; an old restoration
report does not authorize a later release.

Classic frame cadence is measured immediately after synchronized frame begin.
Post-submit background geometry work can vary between frames and distort a rate
sample taken at its completion. Keep the old work-end rate as a diagnostic; do
not clamp, smooth or substitute the target rate. The host test includes a real
stall, and exact-device thresholds remain unchanged. Source pixel review is also
mandatory for snow caps: Classic 0x97, 0xC0, 0xC1, 0xC8 and 0xC9 have land only in the
upper eight rows; lower cliff faces preserve their materials.

Use `python tools/scenery_fixture_candidates.py --game GAME --rom LOCAL_ROM
--inventory LOCAL_INVENTORY --output LOCAL_REPORT` to propose outdoor fixtures.
It verifies ROM CRC (and SHA-256 for prop profiles), reads each map's own tileset,
rejects blocked/non-land starting cells, and ranks nearby reviewed prop families.
Reports contain identifiers and coordinates, never ROM art or save data. These
proposals do not prove walkability, progression state or rebuilt live objects;
review the live target before recording a fixture as usable.


## Binary-hack companion overlays

Patch 0020 adds a reusable hash-locked local-ROM overlay generator and separate
Fakemon FireRed / Better Than Better Emerald 2 configs. A retail engine fingerprint
does not imply retail species, moves or type matchups. Check literal-pool consensus
against the GF header, inspect array ends, then record explicit counts and layouts.
Fakemon has 510 moves and types 23/24/25 (Fairy/Cosmic/Digitl); Better Emerald has
370 moves and a 16-bit effect field in its 12-byte move record. Both retain 411
species slots, with different names and types. Do not copy a base game's labels.

`scripts/gen_binary_hack_overlay.py PROFILE LOCAL_ROM OUTPUT.kt` verifies SHA-256,
table bounds, terminated names, type ranges, growth curves, item IDs (including
explicit reviewed aliases), and terminated type charts. It emits names, types,
move power/PP/accuracy/priority, gender and growth data. Custom move effects remain
UNKNOWN until their routines are mapped; a numerical effect ID is not proof that
retail advice applies. Four synthetic tests cover both move layouts, foreign ROMs,
invalid types and unterminated charts. ROMs stay local.

These profiles are candidates, not device-qualified compatibility claims. Confirm
the complete live-bus hash, party/HP/move/PP and battle state on the Thor, then use
the same exact-APK scenery, audio, pacing, interaction and startup gates as every
other game. A manually selected base profile is diagnostic only.


## Classic shared indoor plant recognition

Classic's active building generator imports `classic_building_specs`, not the
copied generic Emerald furniture list. Its plants occupy two cells: foliage may
be on layer 2 while the pot is on layer 1. Recognize the exact primary-tileset
subtile signatures across layouts instead of enumerating just the first room's
metatile IDs. Reject unrelated upper overlays; group placements by actual plant
and floor pixels so different secondary palettes and wall corners stay intact.
The verified local source contains 165 placements in 40 floor/palette variants.

`classic_botanical.py` adapts the same renderer-neutral 144-triangle plant used
by the other ports. `scenery_plant_mesh.json` is exported from the shared C header;
CI compares the export byte values and checks closed edges, positive volume,
bounds, and source-palette materials. The generator reconstructs each cell's
underlying layers, including flip bits, rather than painting a generic floor.
Botanical redesigns have an explicit geometry check; building pixel-equivalence
checks stay in place. A host preview is not a Thor pass. Check the exact generated
pack hash along with the engine; an unchanged engine does not qualify new art.

Classic's special partner cannot satisfy scripted field-move checks. Disposable
Strength/Smash fixtures must contain an eligible ordinary party member with the
move and badge. Preserve invalid fixture attempts separately; do not misdiagnose
an occluded or immovable target as a geometry defect before testing prerequisites.


For native FireRed/FRLG pacing, inspect `3ds_port/full.mk`: the active menu is
`src/fr_bottom_ui.c`. The copied `3ds_bottom_ui.c` warm-up code is not that port's
battle UI. A retained FireRed f32 active-phase failure had one 17.42 ms work frame
(bottom 5.41 ms, upload 1.70 ms), despite minimum sampled59.7 and zero advancing
track underruns. Do not relax the zero-over-budget gate. The next candidate uses
column-major exact circle spans; 2400 old/new rounded and circle raster cases and
2003 full/dirty menu transitions pass byte equivalence. Thor results must decide
whether that optimization is enough; host correctness alone is not a pacing pass.
