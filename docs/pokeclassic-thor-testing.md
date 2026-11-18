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

The battle replay used `4901b33`. The imported save and Bag check used `ef2926c`. Both used disposable test saves. The upcoming release candidate is checked again before it replaces the tested device build.
