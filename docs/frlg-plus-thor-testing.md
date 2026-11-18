# FireRed & LeafGreen+ on AYN Thor

The native cartridge build from commit `b85c5fc` was assembled locally using the v1.5.1 recipe and ROM, then tested on Azahar 2126.2 for Android. The port uses title ID `000400000F4ED500` and the save directory `sdmc:/3ds/frlg-plus-voxel/`.

- Cold-launched the cartridge, started a new FireRed-mode game and completed naming using the bottom screen.
- Walked through the player's bedroom and downstairs, Pallet Town and Oak's lab with voxel rendering enabled.
- Selected Bulbasaur and won the first rival battle against Charmander. The battle returned to the voxel lab.
- Checked the Kanto map and opened the party and bag on the lower screen.
- Saved in Oak's lab, force-stopped Azahar and confirmed Continue loaded the save after restart.

The Oak encounter at Pallet Town's north grass had rendered the player's exclamation mark as a block of multicolored pixels. The 3DS engine replaces the original graphics sheet with a placeholder, so the icon frames now use the asset's base symbol and a byte offset. This preserves all 15 emoticon frames and their original order.

I replayed the same cutscene from the same pre-Oak save in voxel 3D with the original and fixed cartridges. The fixed build from `616e507` displays the exclamation mark cleanly through the animation, and Oak approaches on cue. The original save was restored after the comparison.

The guarded cartridge from `fec71e8` cold-launched on the Thor and passed the Pallet Town and Oak’s lab transitions from the pre-Oak save. Both Bulbasaur and Squirtle rendered inside their starter portrait frames. Squirtle defeated the rival’s Bulbasaur with voxel battle scenery enabled and returned to the lab at level 6. The lower touchscreen showed the correct party and HP, opened the bag, and displayed the Pallet Town map with 3D enabled. A yellow patch briefly appeared over the end of the first battle action prompt. The user’s original save was restored and its SHA-256 matched the pre-test copy. [Matching build and recipe](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44219927386)

Loading the existing post-rival save also worked. The player walked from the lab through Pallet Town to Route 1, triggered a wild Pidgey encounter in the grass, and used the touchscreen Run button. The game returned to the field. The debug log sampled 59.8 game frames per second, with 59.7–59.8 drawn across most field intervals and 57.2–58.9 drawn during the sampled wild battle. Those samples cover one Route 1 encounter.

The follow-up cartridge from `eafbe5d` restores the active printer’s palette when a second printer has changed it. Bulbasaur defeated the rival’s Charmander on the Thor, and the action prompt rendered with a uniform background and text color. The replay also confirmed that accepting a starter nickname opens the lower-screen keyboard and that the touchscreen OK button restores the lab scene. [Matching build and recipe](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44224733220)
