# PokéDaisy voxel overworld preview

This Android build uses PokéDaisy 1.6.1 and accepts your existing GBA ROMs.
It adds a per-game **Voxel 3D** switch under **Settings → Screen**. Turning
it on selects Expand and activates the live projection in eligible overworld
scenes. The camera uses the game's tiles, elevation and sprite layers.
Menus, battles and unsupported display effects use the standard view.
Party, Bag and Map use the GBA session's existing companion profiles.

| ROM | CRC32 | SHA-1 |
| --- | --- | --- |
| Let’s Go Pikachu | `25c3d89f` | `62bb900925118796fb963b7df92d02cb548c404e` |
| Radical Red | `fba55dd8` | `964f951a0fdaf209e4ea1344883ef0d557bb3a80` |
| Unbound | `4b3d4957` | `b4776b82a4c7915d0fadeaa27e013523f99dfd94` |
| Modern Emerald | `263a1187` | `ab3bc012598d73dce965450df79893aeff97c834` |
| Fakemon FireRed | `5e704d77` | `5ff7d12dd135b6ee6d288f32655cc4ce016077d5` |
| Lazarus | `558ae42f` | `7dcdc7e280bc4631487e13dd37e6e0cea04adea6` |
| Dragonsden | `cec21496` | `40780347d0b4df6bf491eaf12603e5422caee677` |
| Gaia | `b9465c5a` | `d5b1e77975fcda831e0e9a7b527906bf3f40ecd0` |
| FireRed Rocket Edition | `f2d16ebd` | `033d05374ae34eb84fae62c693ca8f3da23dd1bd` |
| Emerald Seaglass | `14465a33` | `b9f4d332d30fc88c379f9e037f9eae3b2755ead4` |
| Odyssey | `6c5ee1b2` | `8745ddbdbfadf6abaf66de4e9055923b62eb4668` |


## Install the test build

1. Download the [tested Android APK](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/releases/tag/graphics-upgrade-2026-11-18).
   The package ID is `com.pokedaisy.app.voxelpreview`, with its own library
   and save directory.
2. Install and open **PokéDaisy Voxel Preview**. Import your ROM and, if
   desired, a copy of your battery save. Turn on **Voxel 3D** in Settings.
3. Walk a few tiles to activate the companion. On the lower screen, check
   the starter in Party, a known item in Bag, and the location in Map.
   Enter a building and a battle, then return to the overworld. Toggle the
   setting off to compare the original Expand view.

If Android reports a signing mismatch with an earlier preview, export/back up
its battery saves and desired states before replacing that preview package.
This tested APK uses an explicit debug signing identity cached by the build
workflow. Cache retention is not a permanent production-key guarantee.
Do not uninstall an old preview before making a usable backup.

## Graphics controls

Settings → Screen exposes Voxel 3D, Visual Climate (Original, Automatic,
Manual), four seasons, Original/Clear/Rain/Snow/Fog and Reduced/Full detail.
Original and Reduced are the defaults. Settings are stored separately for
each ROM CRC. Indoor maps and native weather take precedence; these are
cosmetic effects and do not change battle weather, encounters or saves.

<!-- CURRENT ANDROID SCENERY -->
## Current 11-game scenery build

[Download the passing APK](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/releases/download/graphics-upgrade-2026-11-18/PokeDaisy-3D-Scenery-11-Games-v4-2026-11-21.apk). All 11 listed profiles passed the recorded field, winter, automatic-weather, idle/active battle, interaction, indoor and startup checks. Use **Visual Climate → Automatic** for calendar seasons and season-weighted weather fronts every fifteen minutes. Tests used Reduced detail and native 1× speed. Coverage is limited to recognized environmental assets and reviewed scenes; original actor and battle artwork is retained.

Native-speed frames publish on cartridge-clock deadlines. Early frames can wait up to 16.74 ms; every frame is retained and audio is queued before waiting.

The shared registry contains 103 indoor plant profiles and ten framed bamboo-screen profiles. Camera resets now serialize with frame calculation, fixing a reproduced invalid-coordinate race.

Source: `3d1950843c86899d2b555f8b9427a9fade04a0f2`. APK SHA-256: `130b62f1ce29fad5a63cc5d9821b8c8319e1d38b6275c181118d3aa1cfdc39bc`. [Measurements, exact scope and all-game screenshots](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/android-climate.html).
Native audio fills its real-audio buffer before playback to withstand initial UI work. Native-speed audio production uses Android’s audio-thread priority; optional ROM scans use background priority. 10 additional Rocket Edition cold starts passed with zero underruns. The shared ROM scanner now reuses its read window to reduce startup allocation pauses; 10 additional Fakemon building-scene cold starts passed with zero underruns. After priming the existing buffer, startup holds the core and queued sound for at least three seconds and waits for one continuous second of responsive UI frames. The eight-second timeout is bounded and disqualifies a test run. This adds a short loading pause; steady-state pacing and audio counters are unchanged.

Winter ground recognition now uses exact ROM and tileset identities plus source-reviewed pixel masks. This fixes the reproduced sunset-colored town-ground gaps, Modern Emerald’s hedge edges and Unbound’s ground around conifers and the statue, including ground beside roofs, fences and mailboxes, while preserving those structures. The exact qualified source includes 97 full secondary cells and 2372 mixed-cell masks; only the games listed as passing are device-qualified. Buildings now use solid walls and shaped roofs from 19 reviewed source patterns across 11 passing games. Hip, flat and front-gabled roof families retain each game’s original textures, with shaded sides and contact shadows. The linked gallery includes matching 2D, 3D and winter screenshots. Coverage is limited to recognized patterns; unrecognized buildings and small roof details retain their source art. Source-reviewed facade bounds on 9 patterns keep original grass padding off walls and bases, with roof texture bounds handled separately. Wider showcase camera views received separate 65-second pacing and audio checks for: lazarus.

Rocket tree clearing was verified through its own Leto NPC sequence; the unused retail HM route is not certified. Its Rock Tunnel probe uses a disposable Flash-lit setup; normal darkness remains preserved. Odyssey boulder testing uses its Magna Vis key item. Its cut-object check is a legacy-map/script compatibility probe, not proof of normal story access or Cut acquisition; the original ROM names that move slot Memento.



**Held from this release:** **better-emerald-2** — The local Better Emerald 2 ROM was produced from a base that fails the official BPS input checksum, and its output checksum also differs. Attack probes reset. No compatibility, scenery or performance pass is claimed for this invalid input; a correct patch/base and full retest are required. **ash-gray** — The current disposable movable-rock fixture does not produce a push in either 3D or native 2D on the Thor. The required interaction remains unverified, so Ash Gray is excluded pending a legitimate working fixture; no renderer defect or author-game bug is inferred.

<!-- CURRENT ANDROID SCENERY END -->

## Previous native-clock validation (historical)

The [native-clock follow-up](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/actions/runs/44421988072)
passed fresh Thor checks with all three listed ROMs. Patch 0009 corrects the
Let’s Go settings title, uses the native GBA clock at normal speed, keeps audio
writes nonblocking with bounded buffer rate control, and waits at most one
cartridge frame before reusing a pending video frame. Fast-forward retains its
existing refresh grouping and overwrite behavior.

Across nine final field, battle, and active-battle phases, the measured
120-frame windows held 59.6–59.8 FPS with zero unshown frames, dropped audio
samples, or audio underruns. Field and steady battle phases were 65 seconds;
active phases were 90 seconds. Battles and overworld returns were verified.
These are targeted early-game checks, not a full-playthrough guarantee.

- APK SHA-256: `2467e8063f73030ac745e2e449fb6f34c67a60503cffb242ad22dc785065a68a`
- Patch/workflow commit: `18259de0421456a50ed695ec94da50dab30b3d5f`
- [Measured results, rejected candidates, method and limits](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/android-pacing.html)
- [Six-game lossless screenshots and gameplay GIFs](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/gallery.html)

The earlier [initial validation](graphics-upgrade.md) remains historical context.
The shared [voxel builder](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/voxel.html)
also provides the three separately tested native Azahar titles.
