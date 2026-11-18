# Pokémon Classic on AYN Thor

## Animated ground correction — Thor-qualified

Build `8f42117a6c4be56608f0733aa21765e3c427b6a1` resolves the remaining native animated ground speckles. The Classic port had omitted the native tileset-animation bridge: its DMA queue still contained INCBIN asset markers, so the copy read neighboring native data instead of the packed image. The new queue stages complete image frames before VBlank, preserves the previous frame on a failed read, and marks only the affected VRAM tiles for the existing 2D/voxel texture update paths. It does not rebuild map geometry; tile-animation work is dropped during battles.

The new strict C99 regression compiles the actual patched queue and transfer functions. It checks two distinct frame assets, successive frames, no file I/O during VBlank, dirty notifications, missing-frame handling, queue limits, and space for the largest simultaneous 48-tile primary plus 96-tile secondary update. All jobs in [CI run 44376321112](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44376321112) passed. A full uncached build from the staged web archive regenerated all four scenery outputs and verified the pack; 19 complete flower/water-edge frames were also checked in that pack.

### Thor field checks

Route 1's previously speckled flowers now form the correct flower clusters and change animation frames in both 2D and voxel 3D. A Route 1 → Pallet walk passed; Pallet water edges also animated correctly in both views. Screens were captured several seconds apart in each mode. The earlier forest and PP fixes remain included, and PP was clean in the new battle.

| Route 1 field measurement | Before | New build |
| --- | --- | --- |
| Complete profiler windows | 8 × 300 game frames | 8 × 300 game frames |
| Median of window-average work | 2.68 ms | 2.82 ms |
| Peak work within retained windows | 3.63 ms | 3.90 ms |
| Minimum sampled renderer FPS | 59.8 | 59.8 |
| Logged work over 16.715 ms in retained windows | 0 | 0 |

The first potentially partial profiler window was excluded. The same save, Route 1 scene and voxel settings were used. The extra animation updates have a small measured field cost; this is not a performance improvement claim. Classic's FPS line samples the latest roughly one-second renderer-frame-rate estimate every 600 presented frames; it is not the average over those 600 frames, a separate game-FPS measurement, or a dropped-frame count. The work figures are 300-frame window averages, not individual-frame medians. Slow-work logs have a 4,000-line launch cap; it was not reached in these retained samples.

### Battle check

The battle-selection check passed the compatibility/no-regression criteria. The baseline uses Pikachu level 6 against Rattata level 6, and the new build uses Pikachu level 6 against Pidgey level 3. Both are Route 1 battle-selection scenes, but the opponents differ, so these results are not a controlled battle-performance improvement measurement.

| Battle-selection measurement | Before | New build |
| --- | --- | --- |
| Complete profiler windows | 12 × 300 game frames | 12 × 300 game frames |
| Median of window-average work | 5.345 ms | 5.42 ms |
| Peak work within retained windows | 5.98 ms | 6.13 ms |
| Minimum sampled renderer FPS | 59.8 | 59.8 |
| Logged work over 16.715 ms in retained windows | 0 | 0 |

Pikachu defeated Pidgey with ThunderShock and returned to the overworld. Active audio-track underrun counters remained zero across the sampled checks. The engine and pack were pulled back from the Thor and matched the local candidates' SHA-256 hashes below. These checks qualify this build for publication; they do not assert a locked frame rate throughout the game.

| Tested artifact | SHA-256 |
| --- | --- |
| Engine | `358c05d6c7e1df1ff54155a1872c874809b499295acc291a26e37b3eb67a1dc1` |
| Public web payload | `21db566ad6d8c7d0b72f086530e29bdef55f997341d191766170954ac674f103` |
| Private pack, comparison hash only | `5fd3cef2ee74fbba352c0fb0f44c71db11f27266086036bab14076865d086371` |

The matching recipe/engine ABI is `545036a0`. No ROM, save or generated game-data pack is included in public artifacts. This focused follow-up does not repeat the full climate survey, tutorial, rival battle or every map. Use the [ground and pacing fixes bundle](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/releases/download/graphics-upgrade-2026-11-18/VoxelGraphics-Ground-Pacing-Fixes-2026-11-18.zip) and [release report](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/releases/download/graphics-upgrade-2026-11-18/native-ground-pacing-report-2026-11-18.md) for this qualified build; the previous Classic payloads remain historical release assets.

## Earlier forest/PP correction — historical

Build `e6531b540784832d074cf444a2dfb37e0d8dc172` passed the focused AYN Thor retest in Azahar using Pokémon Classic v1.5.1. Its [CI run 44364733602](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44364733602) passed all jobs, including the native build, extraction recipe, host tests, and link audit.

| Check | Observed result |
| --- | --- |
| Cold launch and Continue | Loaded the Route 1 test save. |
| Repeated forest | East, west, and south edges retained continuous ground and canopy while walking. The old black gaps and sign-textured trunks were absent. |
| Special move and PP | ThunderShock showed the blue special-category icon and readable `PP 30/30` without corruption or overlap. |
| Status move and PP | Tail Whip showed its status-category icon and readable `PP 30/30` without corruption or overlap. |
| Voxel battle and return | Level 6 Pikachu defeated level 3 Rattata with ThunderShock, gained 23 EXP, and returned to Route 1. |
| Live Party panel | Showed Pikachu at level 6 with 21/21 HP. |

Classic's Kanto forest quadrants now form complete paired trees; the inherited Emerald mapping treated one border quadrant as grass. The move-category sheet is resolved before applying its icon offset, and both the sheet and its palette are included in the native asset index. Host regressions cover repeated cells and chunk boundaries, all three category images, and missing assets. The physical category was host-tested only because the test Pokémon had no physical move.

The staged web archive was extracted and used for a complete local rebuild from the matching ROM, with followers disabled and no reused scenery cache. Regions, signs, buildings, and terrain relief regenerated successfully. Pack verification passed with 7,906 entries and ABI `abc4bc53`; the web payload passed the strict publication audit and ROM scan.

| Artifact | SHA-256 |
| --- | --- |
| Public `Emerald3DS.3dsx` | `0984e9581a4683bbdcae170d62a6335e4dde05f194b7e8ae54d0c1bb6111ed02` |
| Public web payload | `d4901996de839248abeb9038a428f09acb218d8c503f13eb2f976b01bfcb370a` |
| Private rebuilt pack, comparison hash only | `8286f09d248e6268325302b70c97fdb773d6c4d7f16e093964241da484abf432` |

This retest did not repeat the full climate survey, tutorial, rival battle, or every touchscreen panel. The earlier observations of occasional 2D ground speckles and the inherited save portrait were outside the fixes. No full-map or locked-60-FPS claim is made.

## Earlier tests — historical

The results below describe earlier builds and are retained as the original test record. Their forest-gap and PP-overlap observations were corrected by the followup above.

The tests used Pokémon Classic v1.5.1 with the local extraction recipe and a matching Azahar engine. Voxel mode and voxel battle scenery were enabled.

| Check | Result |
| --- | --- |
| Cold launch and Continue | A readable menu appeared after the original title. A pre-Oak save loaded in Pallet Town. |
| Pallet Town and Route 1 | The player crossed both ways, and the linked Pallet tileset supplied the paths. |
| Oak’s capture | The tutorial rendered the encounter with Pikachu in voxel 3D, completed the capture, and returned the player to Oak’s lab. |
| Rival battle | The player received partner Pikachu, fought Blue’s Eevee in voxel 3D, and returned to the lab after the loss. |
| Touchscreen Party and Map | A separate Route 1 test save showed partner Pikachu at level 6 with 21/21 HP and the Kanto map with the player marker. |
| Touchscreen Bag | The same imported save showed Potion ×1 in Medicine with its icon and description after the ARM11 save alignment correction. |

The first full replay used `4901b33` and the save alignment check used `ef2926c`. On `f004920`, partner Pikachu defeated Eevee, reached level 6, and saved after returning to the lab. The Static ability popup correction passed a focused host test that reproduces the original allocation mismatch.

The release build `e06c5d2` cold-launched, loaded a pre-rival save, and played a full rival battle through the return to the lab. The move menu showed PP and Type after centering. A separate post-rival save verified live Party, Bag and Map on the same executable. The browser-built ZIP contained the exact installed executable and matching data pack. [Release build](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44235864513)

Small black gaps can appear in the repeated forest outside Route 1. The 2D fallback showed occasional speckled ground details, a small overlap remains beside the PP count, and the save screen still uses the inherited trainer portrait. The tested route and menus remained playable. Static did not activate during the recorded release replay. The host regression covers its popup allocation.
