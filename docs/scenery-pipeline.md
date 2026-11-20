# Reusable scenery pipeline

Start with `tools/scenery_profiles.json`, not a fresh line-by-line code survey.
The current rollout covers environmental scenery in Classic, FireRed, FRLG+,
Let’s Go, Radical Red and Unbound. Actors and battle Pokémon are a separate pass.

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

- Leaves, stems and pots can share a silhouette-volume kernel. Equal down/back
  extrusion preserves the original 45-degree projection while adding visible sides.
- Use opaque neighboring texels on silhouette edges. Horizontal runs reduce triangles.
- Preserve source backgrounds separately: grass, water, cliffs, walls and floors
  are different materials. Snow must not turn water or indoor flooring white.
- Movable/breakable objects follow live object position and visibility. Never bake
  them into static terrain or change their collision/interaction rules.
- Keep geometry and recognition separate. New games normally add profiles and
  fixtures, not another renderer implementation.

## Findings that must not be rediscovered

- Classic uses `classic_building_specs.py`; the imported Emerald definitions are
  not its active model list. Its outdoor renderer and indoor path differ from FireRed.
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

Required fields: `game`, `build_commit`, `source_sha256`, `artifact_sha256`,
`device: "AYN Thor"`, `claim`, `coverage`, and `checks`. Every check named in the
profile file needs `passed: true` and nonempty `evidence`, each with a path relative
to the report and SHA-256. Use `partial_environment_update` until all families have
passed; `all_environment_assets` additionally requires every family in `coverage`
to be `passed`. Never construct a passing record from unobserved results.
