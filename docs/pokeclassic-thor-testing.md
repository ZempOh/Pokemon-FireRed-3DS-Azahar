# Pokémon Classic on AYN Thor

## November 18 followup — passed

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
