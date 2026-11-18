# Pokémon Classic on AYN Thor

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
