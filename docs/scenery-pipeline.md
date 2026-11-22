# Reusable scenery pipeline

Start with `tools/scenery_profiles.json`, not a fresh line-by-line code survey.
The rollout covers the original six games and the ten additional games in the
expansion manifest. Actors and battle Pokémon are a separate pass.

## Repeatable sequence

1. Run `python tools/scenery_pipeline.py --workspace WORK inventory --output inventory.json`.
   This records active entrypoints and source hashes for all sixteen games. Coverage
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

Exact68's wider Lazarus Acrisia review exposed ground around the round-tree
base that the earlier color-only review deliberately excluded. Ground and leaf
highlights both use palette index 0x22. The source-reviewed 0x0f mask now uses
explicit per-row protected silhouette spans; recolor only ground outside those
spans. Keep the proof's ROM, tileset pair and RGBA identity. Regression checks
distinguish a ground pixel from a leaf pixel with the same palette index and
preserve the trunk. This source correction is not a Thor pass; exact68 remains
rejected despite its clean showcase timing.

Exact69 showed that this nearby 0x0f correction did not resolve the wider
scene's round trees. Bind the failure to the map layout before choosing cells:
Acrisia map 0,57 trees at 24,4 and 25,6 use the complete 0x1d6/0x1d7/
0x1de/0x1df pattern. Its reviewed exterior-ground masks flood only edge-connected
ground pixels in the complete 32x32 source pattern; enclosed same-color leaf
highlights, trunk and shadow remain untouched. The overlapping alternate tree
proposal was not selected. Preserve exact68 and exact69 failures; the new four
cell correction still requires full-size Thor review at the wider camera.

Frame full structures before approving building captures. Keep camera framing
as per-game data, retain clipped captures, and separately measure wider zoom
settings. Verify ground fixture coordinates: Classic's full 4x2 berry plot needs
the centered Route 1 fixture at map 6,10 position 7,9. The earlier boundary
fixture at 12,1 did not show the whole plot and cannot establish full coverage.
The private preflight gate requires explicit exact-build building and required
ground reviews before the performance queue can begin; captured files alone
never grant approval.

Strength probes must distinguish boulder displacement from player follow-through.
Classic exact66's short upward input moved the rock from 7,18 to 7,17 while
the player stayed at 7,19; native 2D reproduced the same result. A separate
upward step from each retained state reached 7,18 without moving the rock
again. Preserve the failed original assertion and both continuation proofs;
do not rebuild or retry unchanged inputs merely to obtain a pass. The private
`capture_walkthrough.py` helper records explicit continuation inputs and hashes.
Native pilot reports can be adapted into shared building/indoor evidence with
`export_native_scene_evidence.py`: it checks exact APK, ROM, fixture and file
hashes and copies the original log bytes. It grants no visual approval.

Ash Gray's map 3,32 local object 6 (graphics 97) is a scripted thrown rock,
not a retail Strength puzzle. Its coordinate trigger at y=32 spawns the
three children, moves the rock, removes it, then releases player control.
Use the disposable Dark City seed at 13,33 and replay the actual script in
both modes. Exact66 paired state checks returned the player to 13,34 with
objects 3 through 6 inactive. This proves scene completion, not a Strength
push or full-game qualification. Retain the original failed static-object
probe and inspect dense motion frames for appearance before changing scope.
The other candidate rock at map 3,80 lies on water; a forced standing warp
there is not a valid walking interaction fixture. The QA preference helper
supports ORIGINAL as well as WIDE through the existing atomic recovery path.

Classic's Route 1 berry plot reuses rocky edge cells. Exact64 passed selected
Pallet and southern Route 1 winter views, but the full-size boundary view exposed
brown soil beneath the berry plants. Keep that build rejected. Reused material
needs a complete source-reviewed neighborhood, not a global cell/color rule.
`android-ground-patterns.json` and `gen_scenery_ground_patterns.py` recognize
all eight plot cells with both tileset identities; partial patterns and neighboring
cliff uses stay unchanged. Actor berry plants are separate from this ground fix.
Review boundary footage as well as stationary scenes before long timing runs.
Exact65's initial 3x2 pattern missed the right-edge 0x7f/0x7e cells: the full
plot is 4x2. Keep the partial-coverage failure, review a source neighborhood
with a one-cell margin, and bind fixture coordinates to every pattern cell.

Classic's Android Pallet retest exposed thin ground strips in fence/sign cells
after its pure path corners were corrected. Mixed-material cells need reviewed
pixel masks, not whole-cell land registration. Four own-source masks (3, 0x284,
0x287, 0x2ad; palette 13/14) preserve fence/sign pixels. The map-wide ground
inventory and source preview supply repeatable evidence; the frozen exact62
APK remains rejected until a replacement passes full-size Thor review.

Archived Better Emerald 2's exact52 Thor pilot corrected Route 212 and rendered
the reviewed town houses, but full-size winter review exposed colored earth
pixels at the edges of pale paths. That APK is rejected. Four source-reviewed
secondary cells (`2f8`, `2f9`, `308`, `309`) in tileset `083df734` are entirely
land; patch52 registers them without touching roofs, foliage or water. The
source comparison found no eligible transfers to other tilesets and explicitly
held two truncated source-art pairs. No new Thor pass is implied.

Use `tools/scenery_material_transfer.py` for future exact artwork comparisons
across a game's inventory. It uses the revision resolver and each map's declared
layer layout, compares RGBA identities instead of numeric cell IDs, and emits
unapproved metadata. Source-material review and full-size device review remain
separate requirements. The private `inspect_map_ground.py` helper records map
coordinates, palette indices and source-art hashes for diagnosing edge gaps.

Exact53 corrected those horizontal edges but exposed the same unregistered
material on the vertical path at the viewport edge. It is also rejected.
Patch53 completes the source-reviewed nine-cell path family and one identical
center cell in another tileset. Review the entire material family before
building, including both axes and corners; a narrow screenshot can hide a
partial registration. The regression check requires all nine path cells and
excludes neighboring decorative walls. Private `inspect_tileset_cells.py`
produces a revision-bound family atlas for this review.

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

- Better Emerald 2's accepted archive is CRC32 `2be557a3`, SHA-256
  `8025d00d96a801387fe7c234475c9662b6bcf771ffaa55a29502c919238b039b`.
  It is a distinct older revision, not the current creator patch output.
  All 74 reviewed tileset pairs match the rejected input's tile, palette and
  metatile bytes; 37 live sprite/template checks also match. See
  `tools/scenery-profiles/better-archive-source-proof.json`. Recognition profiles
  can reuse those verified assets, but maps, gameplay and Thor qualification
  cannot inherit a pass. Regenerate the exact-version companion overlay: gender
  ratios and growth rates differ. The invalid `70823957` patch output remains
  rejected in historical evidence and is no longer the active supported identity.
  Exact candidate `7fdff4a` connected and defeated a wild Lumitel on the Thor,
  but its companion still labeled the archive's Route 212 as retail Route 115.
  The generator now accepts an explicit map-section table (213 entries at
  `0x085a147c` for this archive), with pointer and string-boundary checks.
  Entry 211 points into unrelated dialogue and is explicitly shown as unknown.
  The own-source town-house profile also excludes grass from its wall texture;
  full-size device review remains required. These changes do not certify the
  game or supersede the last passing public build.
- `tools/scenery_inputs.py` resolves optional private revision overrides from
  `WORK/scenery-completion/rom-inputs.json`, verifies the ROM against both its
  inventory and requested profile, and leaves historical inputs intact. Use
  this resolver for revision-specific source audits instead of renaming ROMs
  or rewriting old evidence to match a new version.
- Missing companion support is part of the expanded rollout, together with
  per-game 2D/3D scenery, calendar seasons and naturally changing weather.
  Platform-specific adapters and exact-version profiles are required; generic
  ROM playback is not evidence of companion or 3D support. Keep the original
  sixteen in regression coverage while prioritizing popular compatible hacks
  across GB/GBC/GBA/DS and original-151-focused games.
- Ash Gray's retail party Strength entry at `0x081be16e` branches to
  `0x081be179`, where this verified ROM contains erased `FF` bytes instead of
  FireRed's `setflag 0x805` script. Both inventoried graphics-97 boulders also
  have cartridge-header talk pointers. The synthetic party-move fixture cannot
  qualify Strength; do not patch RAM to manufacture a gameplay pass. Local
  `all16-thor/ash-strength-script-audit50.json` records the ROM identity and bytes.
- Reapplying Better Emerald 2's creator patch to the newly supplied clean Emerald
  with validation deliberately disabled produces exactly the previously held
  SHA-256 `2503ed1832224d280d73c2e7e6ffc4b3dc90b58b1df2cfce70d587bed3b5dca3`.
  A fresh host single-attack replay again reset to the Game Freak intro. This
  diagnostic exception does not relax publication checksum validation. The
  first game's checksum has not been established.
- The consolidated Android app retains the existing package/signing identity
  so preview saves remain available. Graphics and aspect choices are keyed by
  ROM identity. Before hiding duplicate launchers, back up all readable data;
  retain inaccessible regular-app private data in place. Never uninstall it
  merely because external saves were copied.

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

## Encounter grass is separate from decorative foliage

Do not infer encounter grass from an inherited renderer's foliage IDs. Own-ROM
art and attributes show metatile 0x0D has tall-grass behavior 2 in Let's Go,
Radical Red, Fakemon, Rocket, Unbound and Dragonsden's Kanto tileset. Unbound
also uses 0x12 with behavior 2. The other reviewed Kanto 0x12/0x1A images are
tree fragments, not encounter grass. Patch 0021 adds seven hash-locked source
profiles using the shared solid grass mesh and each game's own material pixels.
These are candidates until their exact APK passes Thor tests.

All fifteen registered encounter-grass entries have now been checked against
their own ROM's behavior 2 attributes. The registry generator requires this
reviewed semantic field for kind 1, so decorative tree fragments cannot silently
be added as encounter grass by copying an earlier profile. This validation-only
addition leaves every generated runtime header byte-identical to patch 0021.

QA grass-route proposals must use reviewed kind-1 profiles and walkable map
cells. A patch of grass alone does not prove wild encounters are enabled there.
Retain failed route attempts; phone calls, defeated trainers, story state and
held encounter-reducing items can prevent a battle without a renderer defect.
Keep manual input notes with any subsequently captured battle fixture.

The broader used-cell audit found 68 unregistered behavior-2 primary cells,
many of which are tree fragments or mixed-ground edges. Behavior alone is not
a safe geometry classifier. Lazarus's starting region uses full grass tuft 61;
patch 0022 registers that reviewed image and removes Radical's old 0x12/0x1a
tree-as-grass fallback. Mixed ground variants need separate floor-preservation
review. The new registry has 36 ground profiles, with 16 verified grass entries.

Before preparing disposable interaction seeds, inspect each party's actual
format and sector checksums. Gaia and Odyssey use documented plaintext GAEM
parties; the other ten-game seeds validated encrypted substruct checksums.
Lazarus and Seaglass's current save files already contain their acquired starters.
Synthetic HM moves and engine-family badge flags are only test setup: verify
the game's own move names, PP, eligibility and actual scripts on the device.
Never convert successful seed generation into an interaction pass.

## Emerald-derived indoor plants

Do not scan an assumed full primary metatile range for indoor furniture.
Emerald's Building primary can contain only a few shared floor entries; furniture
belongs to the secondary tileset. Review actually used map IDs and match the
reviewed plant layers across real vertical pairs. Key secondary-owned profiles
by both tilesets, so an unrelated room cannot reuse the same metatile numbers.

Patch 0023 adds 85 exact-layer profiles: Better Emerald 12, Modern Emerald 15,
Lazarus 15, Dragonsden 33, and Seaglass 10. Together with the original 19,
all thirteen Android games now have recognized indoor plant profiles. Their
own colors feed the shared closed botanical/topiary meshes. This is recognized
family coverage, not a claim that every decorative plant or room was remodeled.

Lazarus and Dragonsden can put foliage on raw layer 2 and the pot on layer 1.
The runtime composites all other layers, preserving each cell's floor and wall
pixels, transparency and flips. The actual C sampler matches independent
own-ROM composites for 170 cells / 43,520 pixels; all 104 models pass the solid
geometry checks. These host checks do not qualify the new APK on the Thor.

`tools/scenery_snapshot.py LOCAL_RESUME.companion` reads the versioned location
and party-count header without touching the device. Check this before calling
a fixture a field or battle scene: the retained Rocket seed is a partyless
hideout, not an outdoor field. Preserve it, then prepare and review a separate
disposable scene. Never expose these snapshots or saves in public artifacts.

`tools/scenery_gallery.py --media RELEASE_MEDIA_DIR --output gallery.html`
checks every selected image hash and requires build references before rendering
the shared 2D/3D, season, weather, motion and battle sections. Run it only after
the release gate selects passing media; it is a media integrity check, not an
independent device qualification. It preserves published games in the manifest
and replaces stale candidate panels with their actual selected-build references.

`tools/scenery_interaction_candidates.py` combines the hash-locked map inventory
with reviewed live-object graphics. Supply the engine's actual template-kind
and banking settings. It proposes a walkable cell below each target, retaining
the local object ID, visibility flag, interaction-script pointer and nearby
same-kind count. It does not edit saves or grant an interaction pass. Check the
game's own HM/item/badge requirements before testing removal or movement, and
keep unreadable-map failures visible. This avoids repeating object-layout and
coordinate discovery for every new game.

For winter boundary probes, inspect each own-ROM map's connection list and
require walkable source, approach and destination cells. Prefer the already
reviewed field map; unused vanilla maps can survive inside a hack and are poor
default test scenes. Retain unreadable connection pointers in the local report.
Verify the actual post-walk map from the versioned companion snapshot before
reviewing snow continuity. Fixture generation alone proves neither traversal
nor visible coverage. Capture summer again to check that winter coverage clears.

Active battle qualification must retain both a connected battle and a return
to the field in the measured log. An immune first move or a status-only first
slot can make a valid encounter unsuitable for an A-only replay. Preserve the
idle encounter, then prepare a separate active fixture through normal in-game
party or move selection. Never count a stable but unfinished battle as a return.

The first Emerald-family room pass exposed an important scope trap: Lazarus
retains old Emerald rooms, but Acrisia's actual doors lead to custom rooms.
Resolve the reviewed town's warp events before selecting an indoor fixture.
Patch 0025 adds nine exact-layer palm, topiary and laboratory-plant profiles
from those rooms (113 total); the independent floor check now covers 188 cells,
48,128 pixels. Distinct source foliage midtones keep the brightest leaf sample
from washing out the model. These host checks still require device review.

For an intermittently black scene with a live HUD, retain native output-pixel,
camera and palette diagnostics; renderer activity and FPS alone do not prove
visibility. Exclude the HUD from screenshot visibility checks. Camera reset
(UI thread) and frame calculation (emulator thread) must share a transaction:
an interleaved tween reset can produce a zero denominator and persistent NaN
coordinates. Patch 0026 serializes reset, mode changes and frame calculation;
the concurrent-reset test requires finite, nonempty windows throughout.
This fixes the identified race; exact-build Thor startup/scene testing remains
necessary before attributing or closing the observed black-screen failure.

The local Kotlin before/after harness reproduced invalid coordinates in the
old camera (zero scale and NaN offsets), then completed two million concurrent
reset/frame calculations with the fixed class and no invalid window. Keep this
host result separate from the exact-APK Thor visibility and performance gates.

Disposable save loaders must stop advancing buttons once connected field
telemetry and actual field rendering appear. A fixed sequence of extra A
presses can remove the facing Cut tree before the "before" capture, invalidating
the interaction setup. Preserve each load capture under a unique name.
Select indoor and HM evidence explicitly after review; verify their exact build
and file hashes before copying room comparisons or interaction GIFs into the
shared website/repository gallery. A generated seed is never an interaction pass.

The gallery command also accepts `--repository --output README.md`; both HTML
and Markdown use the same hash-verified media manifest. Replace obsolete status
and download sections when publishing, including the builder's supported-game
list and its linked ROM-identity instructions. For seasonal comparisons, use
naturally green terrain rather than a map whose original art is permanently snow.

Seaglass reuses Emerald plant metatile numbers for framed bamboo room screens.
The Thor 2D comparison exposed this semantic mismatch despite exact layer hashes.
Patch 0027 assigns those ten profiles shape 2: closed shallow furniture retaining
the full source motif on its faces and frame colors on its sides. Shapes 0/1
remain botanical geometry. Match artwork identity, not just inherited slot IDs;
require a 2D/3D room comparison before approving any new asset family.
Patch 0028 crops the eight transparent rows above the 24-pixel screen rather
than sampling the wall underneath them. A contrasting-color render regression
ensures no face samples that padding.

Reuse checksum-linked disposable HM starting states after their target is visibly
confirmed. Stop dialogue inputs when fresh native scene telemetry returns to the
field; repeated A presses can reopen Strength's completion text. Rock Smash may
start a wild encounter: capture normal escape and return to the cleared path.
Retain failed probes separately. The sequential QA queue records job failures,
resumes only under the same APK hash, and never grants visual approvals itself.
Winter-boundary evidence must hash the clip and summer restoration, and the
actual destination must match the planned neighboring map before publication.

Select interaction fixtures from the game's connected world when possible,
not simply the lowest inherited map number containing that graphics slot.
The QA map-graph audit follows own-ROM door warps and map connections from
the reviewed field. It found better targets in Lazarus's actual starting town,
Dragonsden's connected region, and Fakemon/Rocket's active Kanto towns. Keep
seed-set overrides separate and checksum-linked so old probes remain auditable.
Missing graph paths are unknown, not proof of an unused map: Odyssey uses
scripted travel that the structural graph does not resolve. Malformed legacy
edges must also remain explicit unknowns instead of invented connections.

A collision-clear connection can still be water. Unbound's first proposed
boundary started beside its bridge and produced water-heavy footage. Probe
neighboring connection coordinates, preserve the native offset, and inspect
source artwork before creating a replacement fixture. A color filter can reject
obvious water for this fixture search; it is not an asset-recognition rule or a
visual pass. Require the actual land crossing and the same destination restored
to summer, retaining the rejected attempt separately.

Dragon's Den uses map type zero for both outdoor routes and some interiors.
The Celadon-only override lost winter on entering Route 16. Patch 0029 uses
140 explicit outdoor entries from a local visual review of all 176 type-zero
maps; 36 interiors, caves or ambiguous scenes remain excluded. The metadata-only
`android-outdoor-review.json` retains ROM and source-map hashes. The generator
requires exact agreement between approved entries and capability overrides.
The climate regression crosses Celadon to Route 16, then enters an excluded
room; winter persists outdoors and clears inside. These source reviews are not
140 Thor passes. Keep the exact-build boundary and indoor checks mandatory.

Live grass effects are separate sprites from the terrain underneath. Rocket's
short-grass effect remained green in a winter boundary replay because the old
sprite whitelist covered only the original three Android games. Patch 0030 adds
48 exact ROM/template/image matches across the ten additional hacks, using the
existing seasonal leaf shader and preserving live position and alpha. Two Ash
Gray white ground-like replacements remain excluded from foliage treatment.
`tools/scenery_effect_inventory.py --manifest MANIFEST --rom-directory ROMS
--output REPORT` locates candidate field-effect tables after validating ROM hashes.
It emits metadata, never approvals or ROM art. Review each effect's frame artwork,
including changed palette tags (Gaia), before adding it to
`android-grass-effects.json`. The registry rejects unreviewed profiles; tests
reject mismatched ROM, template or image pointers. Exact Thor grass movement
and actor-color checks remain required.

HM eligibility differs even between related engines. Lazarus and Seaglass
object scripts check bag possession of HM01/HM04/HM06 (682/685/687), so adding
moves and badges alone is insufficient. Before repairing a disposable test save,
read its own script prerequisites and corroborate pocket offsets in two live
snapshots. Their TM pockets differ (1776 versus 1936), as do SaveBlock2 quantity
keys (+0xB0 versus +0xAC). Preserve both bank checksums, original probes and
personal saves. Shared fixture preparation still requires actual use, movement
or removal, and return-to-field review on the final APK.

Ash Gray uses tools instead: its Cut script checks Hatchet (269), and its
breakable-rock script checks Pickaxe (278). Two live snapshots corroborate the
key-item pocket at 952 (30 slots), with quantity key at SaveBlock2 +0xF20.
Preserve existing key items when adding prerequisites to disposable fixtures.
Its two inventoried movable-rock entries point to the ROM header rather than a
valid talk script. A live snapshot confirms the selected rock is active, visible,
and uses the reviewed image table; it is partly occluded by the actor. Test the
legitimate party-menu Strength activation instead of calling that placeholder.
This remains unresolved coverage until the actual push is reviewed.
The shared interaction-candidate tool now excludes null, cartridge-header,
out-of-ROM and immediate-end pointers into an explicit metadata list, while
retaining unreadable maps as unknowns. Synthetic regression tests cover these
cases and ensure valid pointers remain proposals requiring gameplay review.

Rock Smash can start a wild encounter after its animation. Wait for that delayed
transition before asserting a cleared field. Let’s Go's directional command-menu
inputs selected Pokémon instead of Run; the observed companion Run button
successfully escaped. Use the shared companion control for the current Thor
layout, validate display geometry, and retain both the encounter and subsequent
field/walkthrough footage. A battle-start clip alone is not a Smash pass.

Push probes need a free destination, not merely a nearby boulder. Unbound's
initial position had a cliff north of one rock and an NPC beside another.
`scenery_push_routes.find_push_routes` accepts normalized live object positions
and collision cells, then proposes reachable approaches with unoccupied push
destinations. It does not grant eligibility or a gameplay pass. Also verify the
actual starting tile: short stick taps can turn without stepping. The reviewed
Unbound setup uses down/left 0.18-second inputs and a captured snapshot confirming
(60,8) before pushing the rock at (60,7) north. Preserve blocked attempts, and
approve only observed rock displacement plus normal field movement.

Native-clock frames must be presented on cartridge deadlines, not as soon as
scene-dependent work ends. Radical Red's battle-to-field transition changed
work from roughly 2 ms to 12–14 ms; immediate publication produced a retained
59.4 fps window despite no dropped audio or overwritten frames. Patch 0031
defers native-speed publication until its existing frame deadline, writes audio
before waiting, and excludes that intentional wait from CPU-work telemetry.
An inexpensive frame can wait up to one cartridge frame (16.74 ms) before
publication; this bounds the extra presentation latency.
Late frames remain visible and are never skipped; other pacing modes retain
their original path. Deterministic clock tests exercise battle/field work changes,
early wakes and overdue frames. The unchanged Thor timing/audio gates must pass
on the resulting APK before publication; a host clock test is not a Thor pass.

An active battle probe can lose and enter lengthy healer dialogue. Preserve that
outcome rather than assuming victory. Use B to dismiss post-battle text and allow
enough inputs for all pages; A can reopen the conversation. Require positive
scene-0 rendering in the latest two consecutive samples after connected
non-battle telemetry. Unbound briefly returns to the field before another story
dialogue; an earlier field sample cannot qualify the final state. Regression
tests in `tools/test_scenery_battle_observation.py` reject this transient return.
The reusable parser is `tools/scenery_battle_observation.py`.
Record each probe's duration in provenance
(Unbound needs a longer story-completion replay), preserving the same timing
and audio thresholds. Keep failed attempts and
select any corrected replay explicitly with its reason; recheck every original
timing/audio gate on that replay instead of accepting a screenshot alone.

Reject any post-battle connected telemetry with a zero-sized party: resetting
to the title and choosing Continue can otherwise mimic a successful return.
The battle parser has a regression for that sequence. Better Emerald 2 exposed
this during exact-candidate testing; its attack reset also reproduced on an
earlier APK and in standalone mGBA. Retain the failed evidence and investigate
the cartridge and disposable party/save compatibility before changing rendering
or accepting another fixture. A clean timing measurement does not qualify a
resetting battle.

Audit patch inputs before generating profiles or starting device tests.
RomPatcher JS uses `requireValidation`, not `validateChecksum`; unrecognized
options are silently ignored. Independently verify all three embedded BPS/UPS
checksums (source, target and patch) with `scenery_patch_audit.py`. IPS lacks these
checksums and needs separately reviewed base/patch hashes and deterministic
output verification. Do not mark `embedded_checksums: true` as validation.
The earlier Better Emerald 2 preparation used a source CRC of `1f1c08fb` where
its BPS requires `b7aca3ff`; its resulting `70823957` also differs from the
expected `5b5e4ecb`. This invalid input is held from qualification. Its retained
screenshots and failed attack probes do not establish compatibility or a bug
in the author's correctly patched game. The other six BPS/UPS expansion inputs
and outputs matched their embedded checksums in the independent audit.

Run `python tools/scenery_patch_audit.py BASE PATCH OUTPUT` as a reusable
preflight. It prints only hashes/checksum results and exits unsuccessfully for
a mismatch or an IPS patch without separate provenance. For IPS, verify the
known clean-base hash and compare a fresh deterministic patch application with
the candidate bytes. Keep invalid inputs explicitly held, preserve their failed
evidence, and list only independently qualified games in release counts. A held
game must appear in the report and public release scope; it must not inherit a
pass or disappear from the requested-game accounting.

Rocket Edition exposed a cold-start audio deficit after the steady-state pacing
checks were clean. Retained startup logs show UI/JIT work and blocking GC, two
underruns before measurement, and no further endpoint underruns during the
65-second field run. Keep that run failed: startup counters must not be reset
or ignored to manufacture a pass. Patch 0032 fills the actual AudioTrack buffer
with real PCM before native playback starts, replacing the three-quarter start
reserve. On the Thor this adds at most about 40 ms to startup priming, using
the same 7,688-frame capacity. Short writes remain queued; audio samples are
not fabricated or discarded. The existing half-buffer restart threshold still
applies once playback advances. Steady-state pacing and buffer capacity are
unchanged. Recheck repeated cold starts and every exact-APK gate; earlier APK
results cannot qualify this change.

Do not rely on the live green-hue mask for town ground at sunset. Fakemon's
Pallet Town boundary exposed secondary grass/path cells that stayed dark while
the primary terrain became snowy. Patch 0033 adds full-land recognition scoped
to ROM CRC, primary tileset, secondary tileset and metatile ID. The reviewed
source atlas excludes mixed roofs, walls, fences, mailboxes and water. Exact
RGBA plus native-behavior matches transfer only explicitly reviewed art across
Radical Red, Fakemon, Dragon's Den, Ash Gray and Rocket Edition; this is source
recognition, not device qualification. Evidence is in
`android-secondary-land-review.json`.
The registry generator rejects missing or mismatched proof, and the compiled
lookup test rejects another ROM/tileset and explicit roof/water IDs. Current
and connected-map tilesets both participate. Every resulting APK still needs
fresh Thor timing, night-boundary and media checks.

The patch33 pilot fixed the broad gap but exposed rectangular remnants in mixed
roof/fence cells. Patch34 supersedes its coarse list: 90 full secondary cells,
70 visible-ground masks and five matching primary-ground registrations. Derive
mask candidates from the visible source palette indices of unambiguous ground,
including tile flips and overlay transparency; then review the masked pixels
against the original artwork. Matching RGB colors alone can confuse structural
highlights with land. Store only reviewed row bitmasks and source hashes, scoped
to both tilesets. Preserve roof faces, fence posts, mailbox pixels and water.
The source helper is `tools/scenery_material_masks.py`; provenance lives in
`android-land-mask-review.json`. Tests reject a mask expanded into a roof and
check compiled lookups against explicit roof/fence/mailbox pixels. Do a targeted
night-boundary pilot before another full device suite; neither pilot APK is
qualified by its successful compilation or timing results on an earlier build.

Never infer a movable-rock pass from a menu accepting Strength. The retained
Ash Gray fixture left the target at (13,31), rather than (13,30), in both 3D and
native 2D on the Thor. Its injected move produced the same stuck field pose.
That fixture cannot qualify the interaction; keep the game explicitly held
until a legitimate working fixture is established. This observation does not
establish a renderer defect or a bug in the author's normal game progression.

Use the approved native FireRed 3D build as the visual benchmark across games,
per the user's November 20 request. Compare actual device captures for plant
volume, rock silhouettes, building depth, contact shadows and seasonal ground
continuity. Shared geometry does not establish equal visual quality: the native
GPU renderer and Android software projection have different camera and raster
characteristics. Keep remaining differences explicit and require exact-build
pacing and interaction checks after renderer changes.

Patch35 follows the full-primary-ground atlas audit. Modern Emerald's path/tree
join and doorstep exposed missed secondary ground, while Lazarus's custom paving
was only partly covered by generic Emerald IDs. Add its 30 reviewed paving cells
and the exact Modern mixed-cell masks. Metatile 0x11c contains water-edge pixels
in Modern Emerald, Lazarus and Seaglass; remove it from full-land recognition and
mask its ground pixels only. Metatile 0x124 is plain sand and remains valid land.
The same proof-checked lookup supports primary mixed cells, retaining both
tileset identities. Coverage is now 91 full secondary cells, 89 mixed masks and
35 explicit primary registration proofs. Keep source atlases private; retain
hashes and row masks in the registry. The earlier candidate's timing passes do
not qualify these changes. Review targeted Modern/Lazarus winter captures and
the water-edge mask before starting another complete device suite.

Patch36 extends the reviewed source-material lookup to Kanto primary ground
behind signs and fence ends. The boundary pilot alone missed these in Fakemon's
central town scene at night. Exact artwork/native-behavior matching adds 42
full-primary registrations and 671 mixed-primary masks, for 77 primary proofs
and 760 mixed masks overall. Vegetation candidates in the private atlas are
excluded from this transfer; modeled plants keep their own rendering path.
Merge cells into an existing tileset mask group: its default case returns null,
so a second group with the same identity would otherwise be unreachable.

Before long exact-build timing runs, capture 2D, 3D and winter views of every
eligible game's reviewed scene, plus targeted boundary/interior regressions.
Review those actual device images first. A successful boundary or host atlas
does not qualify the rest of a town; the 2a6 candidate's central Fakemon and
Modern/Lazarus winter gaps remain rejected despite clean timing. This visual
preflight prevents repeated full timing suites for a known asset defect.

Building volume pilot (patch37): the native FireRed benchmark exposed Android
building artwork still lying on the terrain plane. `scenery_building_geometry.h`
emits closed hip-roof or flat-roof meshes through a renderer callback; the Android
adapter samples each live ROM's original facade and roof, with shaded sides and
contact shadows. `scenery_buildings.py` generates exact CRC/tileset/full-pattern
identities from reviewed references, with source hashes rather than bitmap data.
The first pilot covers Fakemon's two identical Pallet houses with one pattern,
plus its laboratory. It is not an all-game building rollout or a device pass.
Unknown/partial patterns retain original artwork. Verify the rendered-building
telemetry, camera-edge behavior, actor occlusion, door alignment, winter and
native-clock pacing before transferring families to other games. The closed-mesh
test checks nondegenerate faces, shared edges, height and UV bounds; the software
raster test checks clipping guards and foreground occlusion.

The exact patch37 Thor pilot rendered all three Fakemon Pallet buildings and
held 59.7 FPS in all 32 field samples, with zero application/endpoint underruns
or unshown frames. Actual movement captures confirmed stable house volume.
This is a targeted pilot, not an all-game qualification. Central-town winter
ground was continuous, but the northern dense tree rows exposed ground pixels
around unmatched canopy edges. Patch38 adds source-reviewed tree-edge masks:
1,866 mixed masks overall. Preserve foliage and trunks; flowers and shrubs are
not included in that transfer. Tests check ground and canopy pixels separately.

Patch39 extends the shared mesh to front gables, including offset peaks and
different front/back ridge heights. Eighteen exact building patterns cover
reviewed families in the eleven eligible Android games. Lazarus's cathedral is
three adjoining source rectangles, retaining its two wings and sloping central
entry roof. These are source identities, not eighteen device passes or full-map
coverage claims. The larger source capture margin needs fresh timing tests.
Keep flat-roof machinery, roof trim and unrecognized architecture limitations
explicit. Test doors, camera edges, actors, winter and battle returns before
publication. The private extraction pipeline retains source rectangles and
hashes; the public registry contains geometry, IDs and hashes, never ROM pixels.

Patch39's first all-game visual preflight exposed gable-face pixels stretched
onto Let's Go's roof slopes. Patch40 separates roof-only UV rows from the vertical
gable triangle and source-reviews the corresponding roof bands in Let's Go,
Unbound and Odyssey. Geometry tests reject facade-row UVs on either slope.
Modern Emerald's Petalburg Center is an additional reviewed pattern, bringing
the building registry to nineteen patterns. None inherits patch37's timing pass.

The latest user preference is matching 2D/3D screenshots and full-size 3D views,
not new GIF deliverables. Preserve timing, audio, battle, weather and interaction
checks. The private publication gate requires reviewed, hash-bound building
screenshots and current-process mesh telemetry for every eligible game. Device
videos can remain test evidence; public galleries and builder cards emphasize
paired stills. Use shared profile registration and reversible patch export tools
instead of repeatedly hand-editing generated headers for another game.

Patch40's Fakemon building-scene probe held 59.7 FPS after startup but retained
three audio underruns from its first two seconds. The process log also recorded
allocation GC blocking the emulation thread while parallel ROM scanners ran.
`FileLittleEndian` was allocating and copying a fresh 64 KiB temporary array on
every window refill. Patch41 reads directly into its existing window, preserving
look-behind and short-read semantics. A host allocation-budget regression scans
16 MiB after warmup and rejects the former cart-sized allocation churn. This is
a shared scanner fix, not a game-specific timing exception. Keep the failed
device evidence, test cold starts on the exact new APK, then rerun qualification;
do not reset counters, increase allowed underruns or inherit patch40 passes.

Patch41 passed ten Fakemon cold starts, but Rocket's third retained start still
reported one audio underrun without the earlier allocation-GC stalls. Patch42
gives the native 1x audio-producing emulation worker the same Android audio-thread
priority already used by `FfMusicPlayer`, restoring default priority outside that
mode. Optional ROM-feature, level-cap and player-look scans use background
priority. See [Android thread priority definitions](https://developer.android.com/reference/android/os/Process).
No buffer enlargement, frame skipping, clock change or relaxed audio gate is
used. Verify the actual worker priority in cold-start logs, repeat startup tests
and retain presentation/UI checks to catch scheduling regressions. Patch41 stays
blocked; its ten clean Fakemon starts do not qualify another game or build.

Patch42 passed ten Rocket starts but Fakemon's seventh start still underrran
during initial UI/JIT loading. Patch43 holds the core once the existing audio
buffer is primed, preserving every queued PCM sample, while the UI settles.
It requires a three-second loading reserve and a continuous second of UI
callbacks without a gap above 40 ms. The wait is cancellable and bounded at
eight seconds; a timeout remains visible and does not qualify a release.
The game timeline resumes after this explicitly logged loading pause without
catch-up frames. Audio counters are never reset, buffers are not enlarged and
steady-gameplay thresholds remain unchanged. Unit tests cover a late first UI
callback and the reserve/quiet-window boundaries. This is a startup latency
tradeoff requiring fresh cold-start, input, UI and sustained Thor checks, not
an inherited pass or a fix for an unrelated gameplay pacing failure.

Patch43 passed ten Fakemon and ten Rocket cold starts without application or
endpoint underruns, and Radical Red passed all five timing phases, including
the 180-second active battle/return test. Full-size winter review then exposed
Unbound's custom plant-base ground still green in Dresco. Candidate43 remains
blocked despite those timing results. Inspect full-size mixed-material edges,
not just the building silhouette or reduced contact sheets, before long tests.

Patch44 reuses the source-palette mask pipeline for 90 reviewed Unbound cells.
Grass palette indices 2/3/4 are traced from its own source ground cell; explicit
masks preserve water, plant bodies, bark, roofs, fences and signs. Exact source
artwork matching registers 437 mixed cells across that ROM's tileset pairs,
plus three full secondary ground cells and three full primary ground cells.
Two ambiguous source cells stay excluded. Tests protect a plant body, roof
slope and wooden sign against recoloring. Atlas images and ROM pixels remain
private; public data contains identities, masks and evidence hashes. Verify
Dresco winter at full size and the bridge boundary on the new exact APK before
repeating all-game qualification. Startup and timing passes are not inherited.

Patch44's full-size targeted capture removed the large gaps but exposed narrow
grass strips and the statue's paving background. Patch45 includes the duplicate
grass palette31 and reviewed path materials, protecting cliff faces and statue
pixels with explicit masks. It also routes the conifer's replacement ground
through the same verified-land climate mode as other ground props; the old
hardcoded color-only mode could repaint night-tinted green after the climate
pass. Eighty reviewed edge references update 118 registrations. The combined
registry now has 2,369 mixed masks and 97 full secondary ground cells. Two
ambiguous roof details remain excluded. Tests separate cliff/grass and
statue/paving pixels. Candidate44 remains blocked; retest the corrected full-size
scene before a fresh exact-build suite. Do not hide source-material gaps with
weather particles, zoom changes or smaller gallery images.

Patch45 passed all twenty targeted Fakemon/Rocket cold starts with zero audio
underruns and corrected the reviewed Unbound winter edges. A full-size Modern
Emerald review exposed grass above three hedge cells in the night palette, so
that exact APK remains blocked. Patch46 registers source-reviewed ground masks
for 0x23c/0x23d/0x23e only in the matching Petalburg tileset. Hedge pixels remain
untouched. RGBA-identity checks found no eligible Lazarus or Seaglass transfers;
no masks were guessed for them. The registry now contains 2,372 mixed masks.
Tests protect hedge surfaces; a new exact-APK full-size Modern Emerald pilot
and fresh startup, scenery, gameplay and restoration gates remain required.

Before testing patch46, diagnostic stills on blocked45 exposed source grass
padding stretched onto Let Go house side walls and bases, with narrower edges
in other profiles. Patch47 adds reusable, validated facade texture bounds and
source-hash-bound crop reviews for nine building profiles. Roof UVs keep their
independently reviewed span; geometry, collision and actor artwork are unchanged.
The closed-mesh C test now rejects any wall UV entering synthetic grass padding.
This is a source-texture correction, not a climate repaint of building walls.
Patch46 is superseded without device qualification. Review full-size summer
and winter facade edges on patch47 before all exact-build timing/media checks.

A source-palette audit of all nine cropped facades caught fourteen grass
pixels beneath Unbound's doorway on source row62. Patch48 excludes both
bottom grass rows62/63. The audited cropped facades now contain no pixels
from their explicit source ground materials. The intermediate APK remains
unqualified; this pre-device correction avoids another long rejected retest.

Exact54 fixed the archived Better Emerald town's pale path family, but the wider
north/south Thor pilots exposed a separate beige plaza around its fountain. That
APK is rejected and its captures are retained. Patch54 adds nine reviewed full
plaza cells and ten pixel masks for paving around lamps and the fountain. The
sign at 0x2e9 lies inside the apparent path atlas rectangle and is explicitly
excluded; 0x341 contains fountain water and is excluded too. Never infer a whole
rectangular tile family from its corners. Review every source cell and adjacent
material family before device timing, including mixed-material footprints.
The source preview and exact-ROM hashes are recorded in
`tools/scenery-profiles/better-archive-plaza-proof.json`. Regression checks protect
lamp and fountain pixels. This correction has no Thor qualification yet.

The private QA queue now routes Rocket Cut through its actual Leto NPC sequence,
not the unused retail HM script. The helper checks its queue ownership before
device input; earlier diagnostic probes remain retained. Public media remains
paired screenshots only; private interaction recordings contain no new GIFs.

Exact55 passed the archived Better town's three full-size ground pilots and five
pacing phases, but is rejected: Let Go's Pallet diagonal path corners remained
yellow in winter. Wider full-size reviews also found Lazarus lamp/shrub/sign
footprints and Odyssey paving outside the ground registry. Patch55 registers
seven Let Go ground cells, seven Lazarus mixed masks scoped to Acrisia's tileset,
and nine Odyssey paving cells. Adjacent water, rocks, walls and stairs stay
excluded. The three source-proof JSON files record exact ROM and cell hashes;
these corrections still require new exact-APK Thor reviews. Earlier captures
and failures remain intact; Better's timing success does not override rejection.

For future source reviews, use `tools/scenery_cell_review.py --workspace work
--game GAME --primary ADDRESS --secondary ADDRESS --ids ID ... --output PREFIX`.
Optional `--ground-reference ID` proposes pixel masks from the reference cell's
visible palette. Review every cell and preview manually before registration;
shared palette colors can belong to structures. Output PNGs stay private, and
the tool never sets approval or Thor qualification. Fixture map atlases now keep
coordinates in a JSON sidecar and show only tile IDs on each cell, avoiding
ambiguous overlapping labels. They honor the game's configured metatile mask.

Exact56 corrected Let Go's path corners and Odyssey's paving. Lazarus's lamp,
shrub and sign footprints improved, but its facade-post cells0x248/0x249 still
showed ground in winter, so that APK is also rejected. A map-wide review now
registers17 additional mixed masks and one full ground cell in Acrisia. The
overhanging trim on0x216 and posts on0x248/0x249 stay untouched. Twelve foliage
cells share the reference palette and were explicitly excluded from this ground
approval. See `lazarus-acrisia-ground-proof.json`; fresh Thor review is required.

Use `scenery_ground_coverage.py` with `--workspace`, `--game`, `--group`, `--map`,
`--reference` and `--output` to inspect all used cells around a failure in one
pass. It subtracts already registered full ground and masks, then produces
unapproved source/preview pairs with exact ROM and map hashes. It deliberately
does not treat shared palette colors as semantic proof. Review structures and
foliage separately, preserve exclusions, and still check the final Thor image.


Exact57 passed the Lazarus post-ground and Let Go corner pilots, but a full-size
Odyssey review exposed an olive ground-shadow ring around tree bases0x40/0x41.
Patch57 masks source ground palette52/53/5e/5f while preserving trunk54/58/59.
The mask transfers to11 tileset pairs only after both rendered artwork and mask
rows match the reviewed source. Ordinary green-ground heuristics missed the
gray outer shadow; include shaded ground materials in winter audits. Exact57
is rejected, all captures remain retained, and new device review is required.

Missing Android adapters remain isolated under the private native-three-android
work area. Classic needs40-byte objects and connected-template marker255; the
nine existing families retain36-byte records and marker1. FRLG+ has19 addresses
bound to literal references inside exact-matching local-ROM functions; its
rebuilt whole ROM differs, so unmatched symbols are not authoritative. Save
offsets8e0/ee0/1000 are independently instruction-checked. Own-map extraction,
source-cell review and facade audits now prepare Classic/FRLG+ building drafts.
Own-material flower/shrub profiles are separate from failed exact-art transfers.
FireRed's verified local base has425 map headers and60 tileset pairs inventoried.
These drafts have no Android device qualification and remain outside release
scope. Reuse the shared input resolver, map/cell/building review tools and
recorded proofs instead of repeating source discovery. Runtime source stays
frozen during device capture; later fixes are prepared in isolated staging.

Native adapter60 compiled but could not update the Thor installation: its
isolated branch generated a different signing key. GitHub Actions caches are
branch-scoped; sibling branches cannot restore the established upgrade branch's
key. Integrate reviewed adapters into `graphics/pokedaisy-upgrade` for installable
diagnostics. The workflow now fails if its signing key is absent instead of
creating an incompatible replacement. Preserve both APK identities and failed
installation evidence; never uninstall user data to bypass a signing mismatch.

Exact61 installed with the established signer and booted all three native games
in Android. Its full-size Classic winter pilot exposed uncovered path-corner
ground. Patch60 adds six individually source-reviewed ground cells (8,288,28f,
290,29f,2b6 in hexadecimal) while excluding signs, fences, mailboxes and trees.
Own-source hashes are in `classic-android-path-corner-proof.json`; exact61 remains
rejected, and the correction needs a new Thor test. FRLG+ and FireRed Pallet
pilots showed 2D/3D changes and covered winter ground, but are partial checks.
CI now checks the signing certificate fingerprint before compiling, preventing
another branch's cached key from wasting a full build or blocking an update.

Native Android indoor proposals now reuse reviewed geometry only after exact
foreground RGBA matches and full source/foreground review. Twelve observed plant
pairs across Classic, FireRed and FRLG+ preserve their own floor layers. Classic's
top foreground is layer2; record `top_layer`/`bottom_layer` explicitly. The
generator rejects camelCase aliases to prevent silently reading background art.
Patch59 adds these profiles to the isolated adapter branch; no Android Thor pass
is implied. Wider indoor recognition and all device gates remain pending.

The graphics/native-android-adapters branch assembles an initial diagnostic
Android adapter for Classic, FRLG+ and retail FireRed. It adds own-source Pallet
ground/buildings, flowers/shrubs, complete tree patterns and interactive-object
art identities. Classic uses its distinct40-byte object layout and clone marker.
FRLG+ addresses are bound to independently matched code ranges, not blanket
trust in a nonmatching source rebuild. Shared season/weather rendering is enabled
for these diagnostic profiles. This is partial environmental recognition, not
whole-game coverage or a Thor pass. Interiors, wider terrain, authentic HM script
tests and per-game UI persistence still require qualification before publication.

### Disposable fixtures: save layout, obedience and occlusion

Exact63 selected native Pallet winter and indoor scenes passed full-size review;
Cut/Smash/Strength pilots retain separate visual and live-object evidence. These
partial checks are not full qualification. Keep the tested source frozen and
record further findings in the private `native63-findings.md` before integration.

Read each native ROM's own 14-entry save-slot table before editing a fixture.
Classic uses a4084-byte save-block stride; FireRed/FRLG+ use3968. Zero padding can
make the wrong full-payload checksum appear valid until a flag crosses a section
boundary. `native_save_layout.py` verifies exact section lengths and all populated
banks; `warp_fixture.py` and HM preparation share it. Preserve erased banks and
old failed seeds. Corrected FRLG+/FireRed interaction seeds use `native63r2`.
The plan generator now defaults to a fresh output label and validates inputs.

Transferred high-level parties can disobey a new trainer even when their party
checksums and moves are valid. Record player and original-trainer IDs, verify
the game's actual obedience prerequisites, and observe an attack and return to
the field before a long active run. Better Emerald2's corrected badge-only seed
passed that sequence and its exact63 active run; earlier failures remain failed.
`prepare_obedience_seed.py` preserves the party while changing explicit fixture
flags. A reviewed replacement fixture binds setup deltas, old failed inputs,
new attack/return evidence, ROM, APK and fixture hashes.

A rock hidden behind the player is not proof of missing geometry. Classic's
initial Smash framing required a native2D control and one-step side view. After
removal, `record_native_removal.py` checks absence of the target object and player
entry into its tile. Strength checks separately record the push and subsequent
walkthrough; retain an incomplete first position proof instead of overwriting it.
`native_qa.py` reuses shared runners through process-local pilot registration;
it does not enable a game's publication scope. `qa_progress.py` lists retained
timing phases without promoting them to visual or full-game passes.

Rock Smash may trigger wild encounters far above a disposable starter's level.
Treat fainting or failed escape as an incomplete interaction, never a removal
pass. If correcting the fixture, verify a guaranteed-escape held item against
that ROM's own item record, preserve party identity/moves/HP and all other data,
and recompute its encrypted party and exact save-section checksums. Retain the
failed probe and use a new seed namespace. FireRed's exact66 correction uses
Smoke Ball194 (held effect37); the live escape, object absence and walkthrough
must still pass independently. This is test setup, not an APK workaround.

Custom interactions need their own source-bound capability profile. Ash Gray's
retail party Strength entry jumps into erased bytes; its recognized rock is used
by a coordinate-triggered story scene. `interaction-scope-profiles.json` records
its actual Hatchet269/Pickaxe278 scripts and paired Dark City scene requirement.
`custom_interaction_gate.py` rechecks exact source, media, live object removal,
player movement and both story-scene outcomes. It explicitly retains native2D
cutscene fallback and never claims a Strength push or 3D cutscene-rock coverage.
The old failed probes stay in the hold archive. A malformed map and unreviewed
secondary water-map object remain outside the reviewed scope. Eligibility for
these corrected tests is not release qualification.

`native_interaction_gate.py` independently rechecks retained push/follow-through
chains and Cut/Smash object states. Negative checks reject failed original proofs,
wrong APKs, cross-game evidence and mismatched operations. `adopt_qa_evidence.py`
can register exact completed manual captures in the queue after rechecking their
files and timing gates; it cannot replace a prior queue result or approve visuals.
Completion accounting includes native profiles still disabled for publication,
and permanent app consolidation requires all requested profiles to qualify.

Exact63 subsequently failed Route1 winter review in all three native adapters:
yellow paths remained uncovered and the live grass effect beneath the player
stayed green. Its nine successful Pallet timing phases remain partial evidence,
and cannot override this rejection. Check route grass and path families before
long qualification runs; a town-only winter scene misses these asset classes.

Patch62 adds 36 reviewed full-ground variants per native game and 199 mixed
ground masks across 52 exact matching tileset pairs. Ledge faces remain stone;
stairs, solid rock caps, fences, hedges and water are excluded from this family.
Each transfer checks rendered source art and mask identity, and each primary
full-ground registration retains its own source hash. Fifteen own-ROM foliage
effect profiles cover tall/long grass and movement rustles. New Thor review is
mandatory. `scenery_effect_inventory.py --workspace ... --games ...` and
`scenery_effect_review.py` now reuse private input resolution for future games.
Cell review accepts multiple explicit ground references; palette coincidences
still require visual exclusion of structure materials before registration.

Exact66 failed full-size Ash Gray Route12 winter review despite native timing
passes. Ground-detail cells8/9 and mixed sign/ledge/fence backgrounds were not
covered. The same preflight sweep found Rocket forest path pixels below walls.
Patch65 adds two full cells and285 exact-art mixed masks for Ash Gray; patch66
adds nine Rocket forest masks. Both preserve source structure pixels and require
fresh Thor tests. Unsupported Ash tileset compression remains explicitly excluded
from transfer. Source proof JSON records selected cells, hashes and exclusions.

Run the full game winter preflight sweep before long timing queues. A town-only
sample misses route-specific ground and secondary building-footprint materials.
The reusable cell review supports several ground references because alternate
path palettes can differ even when their colors look similar. Review masks at
full size; never treat a palette coincidence as proof that an object is ground.
Tests now pin the preserved sign face, ledge face and Rocket wall/ground split.

The all16 coverage audit also found Ash Gray had no registered building model.
Patch67 adds its own Route12 gatehouse (map3,38; source rectangle24,6,4,3)
through the existing hip-roof geometry. Explicit facade bounds exclude source
ground corners; the private source audit passes. Use the disposable viewpoint
26,10 to review the whole model and winter footprint. This is one recognized
building pattern, not all-map building coverage, and needs exact-build Thor QA.

Exact70 passed the reviewed Lazarus round-tree winter footprint, but the all-game
preflight exposed six grass pixels at Odyssey Pokemon Center facade corners.
Patch70 uses reviewed wall bounds x2..78, y48..80 on its own source-art identity;
roof UVs are unchanged. Run the facade material audit after each new crop.
A successful earlier audit covers only profiles with wall_crop_review, not every
registered building. Review full-size winter captures for all remaining profiles
before timing. No exact70 qualification or publication is inherited.
