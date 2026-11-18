<p align="center">
  <img src="3ds_port/assets/artwork/FireRed%203DS.png" alt="FireRed 3DS" width="560">
</p>

# Pokémon FireRed 3DS for Azahar

**Proudly vibe coded.** This fork brings FireRed 3DS to Azahar on Android, with
the AYN Thor as the target handheld. Choose your 3DS games folder and your
FireRed ROM to build and install one standalone cartridge.

The game is a native Nintendo 3DS port with a dual-screen interface and a
voxel-styled 3D world. The builder uses this fork's cartridge engine and a
matching data recipe based on upstream v0.5.1. You supply your own FireRed
cartridge dump.

**[Project website](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/)**
· **[Game builder](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/build.html)**

## Ports and companion builds

| Project | Source and build instructions |
| --- | --- |
| FireRed 3DS | This branch contains the AYN Thor rendering fixes and the [FireRed cartridge workflow](.github/workflows/cartridge.yml). |
| FireRed & LeafGreen+ v1.5.1 | [Native port, cartridge assembly, and Thor tests](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/tree/voxel-frlg-plus). |
| Pokémon Classic v1.5.1 | [Native port and build status](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/tree/voxel-pokeclassic). |
| PokéDaisy | [GBA companion development builds](https://github.com/ZempOh/Pokemon-FireRed-3DS-Azahar/tree/pokedaisy-hack-profiles). |

[Decompilation and native port workflow](docs/decomp-recomp-workflow.md)

The Azahar ports have their own touchscreen Party, Bag, and Map. PokéDaisy
uses those games' GBA ROMs in its own emulator.

## Install and update

### One-file cartridge for Azahar

1. Open the [game builder](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/build.html)
   in Chrome and choose the 3DS games folder that Azahar already scans.
2. Select your own Pokémon FireRed (USA, Rev 1) ROM. The builder generates
   and saves `FireRed3DS.3ds` in that folder.

Launch FireRed from your Azahar library. If your browser cannot write to the
folder, download the built cartridge and move it there manually.
To update, fully close the game, pick the same folder and ROM, and let the
builder replace `FireRed3DS.3ds`. After installation it removes the old
FireRed homebrew launcher and FireRed cartridge temporary files from the
selected games folder. Saves stay in Azahar's virtual SD folder.

The browser generates the game data on your device and embeds it in the
cartridge. The standalone build uses the same virtual SD save location
as the homebrew edition. Optional follower sprites are available in the
homebrew edition.

Azahar on Android defaults to HLE audio. The cartridge header maps the
DSP memory used by FireRed. `debug.txt` only enables diagnostics.

### Map, 3D, and controller navigation

- Voxel 3D starts enabled with fresh settings. Tap **3D ON** or **3D OFF** on
  the lower-screen map while standing in the overworld to switch between
  voxel 3D and the classic view. Your saved preference carries over.
- Press **Start** in the overworld to focus the lower-screen dock. Use the
  **D-pad** to select Pokédex, Pokémon, Bag, your trainer card, Save, or Options,
  and press **A** to open it. Press **B** or **Start** to leave dock navigation.
- Opening **Options** with the controller starts on **3D WORLD**. Use **A** to
  toggle it, **Up/Down** to select another row, and **Left/Right** to adjust a
  setting. **L/R** change pages, **X/Y** change tabs, and **B** goes back. You can
  also use the touch gear and page arrows. The settings include audio, camera
  angle, zoom, battle presentation, and running.
- If the overlay Start works and the Thor's physical Start does not, check
  that the Thor button is bound to **Start** under Azahar's **Settings → Gamepad**.

### Compare 2D and 3D performance

1. Tap the bottom-screen gear, open **Settings**, and go to page 2. Turn on
   **Show FPS**, then go back to the map. The counter appears in the map's
   upper-right corner. Your choice persists across launches.
2. Walk the same route in each mode at normal speed. Use the map's **3D ON /
   3D OFF** switch and allow a few seconds for the scene and counter to settle.
3. The in-game counter counts presented frames using the emulated 3DS clock.
   To see how fast emulation is running on your Thor, use Azahar's
   [performance overlay](https://github.com/azahar-emu/azahar/discussions/1149)
   under **Layout** and enable **Speed**.

### Azahar on Android (including AYN Thor)

1. In Chrome 132 or later on the handheld, open the [Azahar game builder](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/build.html).
   In Azahar, check **Options → Select User Folder**, then close Azahar. Tap
   **Connect Azahar folder** in the builder, choose that folder or its `sdmc`
   subfolder, and allow write access. Chrome may ask you to reconnect later.
2. Select your Pokémon FireRed (USA, Rev 1) ROM as a `.gba` file or a ZIP
   containing it. The build starts automatically. Keep the tab open until
   the builder reports that installation is complete.
3. To launch alongside your other games, choose your existing **3DS games
   folder** in the builder before selecting your ROM. Open
   `FireRed3DS.3dsx` from there in Azahar. You can also move an existing
   `FireRed3DS.3dsx` there yourself. The game data stays in
   `sdmc/3ds/firered3ds/`.

Azahar on Android defaults to **HLE** audio emulation. Direct installation sets up the
emulated DSP automatically when `sdmc/3ds/dspfirm.cdc` is absent. For an
existing install, connect the Azahar folder and tap **Set up sound for an
existing install**, then fully restart the game. Physical 3DS consoles
require their own DSP firmware dump.

For later updates, close the game and pick the ROM again. The builder generates
`firered3ds.pak` locally in your browser and installs it with the matching
`FireRed3DS.3dsx` and icon. It removes recognized duplicates, incomplete
temporary files, and obsolete follower assets in the FireRed install folder.
It preserves saves and settings and attempts to restore the previous game files
if a write fails. Cleanup is limited to `sdmc/3ds/firered3ds/`.

If installation fails after the build, reconnect the Azahar folder from the
results screen to retry without rebuilding.

**ZIP fallback.** Choose **Build ZIP only** and then **Download the ZIP**.
Extract it and merge its `3ds` folder into Azahar's `sdmc` folder. Replace
both the executable and the data pack and keep your existing save.

### Compatibility and troubleshooting

The browser installer's cleanup and rollback are covered by automated tests.
The installed standalone cartridge was tested on an AYN Thor running Azahar
2126.2 (Google Play) with the stock Adreno driver. The title rendered in the
correct orientation, an existing save loaded into Pallet Town, and the
lower-screen map responded to touch when switching between 2D and voxel 3D.

On this setup, use Vulkan, 3× internal resolution, and nearest display
filtering. Keep the disk shader cache enabled and async shader compilation
disabled. Nearest filtering sharpens the pixel art and lower-screen text,
and the higher internal resolution sharpens voxel geometry. Changes made
in Azahar's global graphics settings also apply to other games.

During short Pallet Town walks, Android's main-display presentation intervals
averaged about 16.7 ms at both 1× with linear filtering and 3× with nearest
filtering. The 95th percentile was about 25 ms at 1× and 17 ms on two 3× voxel
passes. Enabling async shaders at 3× produced more intervals over 25 ms in
one pass.

The renderer reuses the uploaded texture when consecutive classic frames
match. When opening a menu over the voxel world, it displays the captured
scene and its matching overlay from the first held frame.

The rebuilt cartridge was tested on the same Thor through Pallet Town,
Oak's Lab, and Route 1, including crossing back to Pallet Town in 2D.
The party menu opened on the lower screen with the voxel scene held above.
A classic Poochyena battle and a voxel Sentret battle both completed and
returned to the field.

Two cold launches of each build used a fresh Azahar process and empty
FireRed Vulkan disk caches. Both builds averaged about 16.7 ms between
main-display presentations with a 95th percentile of about 25.4 ms.
The counts of intervals over 25 ms varied between runs, and the samples
showed no repeatable cold-start improvement.

If the title screen appears mirrored, fully close the game, switch Azahar
between Vulkan and OpenGL ES, and compare the same screen. To collect the
port's startup log, create an empty file named `debug.txt` in
`sdmc/3ds/firered3ds/` before launching. Reproduce the issue, then collect
`port.log` from that folder and note the Azahar version and graphics backend.

### Nintendo 3DS hardware

**In your browser (any system).** Open the
[web builder](https://zempoh.github.io/Pokemon-FireRed-3DS-Azahar/build.html),
choose your ROM - Pokémon FireRed (USA, Rev 1), SHA-1
`dd5945db9b930750cb39d00c84da8571feebf417` - and it makes a ZIP with the
`3ds` folder to copy to the root of the SD card. The ROM is read on your
device and never uploaded; the first build takes a few minutes.

**On Windows**, the same builder as a program that installs straight to the
SD card:

1. Download `FireRed3DS-v<version>-Windows.zip` from the
   [upstream releases](https://github.com/NachoGonzalez2001/Pokemon-FireRed-3DS/releases)
   page and extract it.
2. Run `FireRed3DS-Builder.exe`, choose your ROM - Pokémon FireRed (USA,
   Rev 1), SHA-1 `dd5945db9b930750cb39d00c84da8571feebf417` - and your 3DS's SD
   card. The builder generates the game's data from your ROM on your computer
   and installs it in `/3ds/firered3ds/`. The ROM is never uploaded or copied.
3. Start the game from the Homebrew Launcher, or install
   `FireRed3DS-Forwarder.cia` once with FBI for a HOME Menu icon (it starts
   the installed game, so updates don't need a new CIA).

Needs a 3DS / 2DS family console with custom firmware (Luma3DS). Saves are in
`/3ds/firered3ds/firered3ds.sav`, in the GBA's format: the same 128 KB file
moves between the 3DS, GBA emulators and a cartridge dump. (v0.2.3 converts a
save from an earlier version once, keeping the original as
`firered3ds.sav.bak`.)

**Linux, macOS or a Chromebook (Linux).** The builder is plain Python: with
Python 3.11+ and Pillow, use the `payload` folder from the release ZIP and the
builder's sources from the same version:

```
git clone --branch v<version> https://github.com/NachoGonzalez2001/Pokemon-FireRed-3DS
cd Pokemon-FireRed-3DS/builder
python3 -m firered3ds_builder --payload /path/to/FireRed3DS-v<version>-Windows/payload     build --rom /path/to/firered.gba --output out
```

then copy `out/3ds` to the root of the SD card.

**The Pokémon that follows you.** Its sprites come from
[PMD SpriteCollab](https://github.com/PMDCollab/SpriteCollab), most of them Spike
Chunsoft's own from the Pokémon Mystery Dungeon games, so this repository and
its releases do not include them: the builder downloads them while it installs
(it needs an internet connection for that, once) and writes `followers.bin`
and `followers-credits.txt`, every artist credited, next to the game. Without
them the game works the same, without its follower; it can be turned off in
OPTIONS (3D FOLLOWER).

## Game features from upstream

- **The whole game, native on the 3DS**, at the console's own frame rate.
- **A 3D overworld**: towns, routes, caves and interiors rebuilt in 3D from
  the game's own drawing - buildings, trees, relief, furniture - with lighting,
  shadows, a day/night cycle and an adjustable camera. The classic 2D field
  is one option away.
- **3D battles** (optional): the battle in front of the voxel world.
- **A bottom screen made for touch**: region map, party and quick menu keys in
  the field, with their own touch screens for the battle, the party, the bag,
  the summary, the trainer card, the Pokédex, the PC's boxes and the fly map,
  while the top screen keeps the world. Other menus show the game's own
  picture there and use the console's buttons.
- **Free movement** (optional): walk any way the circle pad points.
- **A Pokémon that follows you** in the 3D world: the first of your party
  walks behind you, in eight directions, in Mystery Dungeon style (see below).
- **Renewed wild Pokémon**: every non-legendary Pokémon of the first three
  generations lives somewhere in Kanto or the Sevii Islands, by level and
  habitat, and the National Pokédex is open from the start.
- **Visible wild Pokémon** (optional, OPTIONS > VISIBLE WILD): instead of
  random encounters, up to 2, 4 or 6 wild Pokémon wander the grass, caves and
  water in Mystery Dungeon style; touch one to battle it.
- **Mega Evolution**: 48 Mega Evolutions of the first three generations and
  of Pokémon Legends: Z-A, with the MEGA RING and MEGA STONES found in the
  story, and renewed Gym Leaders and Elite Four that use them.
- **Physical/special split** (optional, OPTIONS > MOVE SPLIT): each move is
  physical or special by itself, as in the later games, instead of by its
  type; the move pages show its category.
- **Options**: settings, quality-of-life enhancements (game speed, exp share,
  reusable TMs, HMs without the move...) and cheats, from the bottom screen.

## Screenshots

<p align="center">
  <img src="docs/screenshots/dual-screen.png" alt="Cerulean City with Charmeleon following on the top screen, the region map, party and menu on the bottom screen" width="400">
</p>

<table>
  <tr>
    <td><img src="docs/screenshots/route-25.png" alt="Route 25 with Eevee following"><br><sub>Route 25</sub></td>
    <td><img src="docs/screenshots/vermilion.png" alt="Vermilion City harbour with Squirtle following"><br><sub>Vermilion City, morning</sub></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/cerulean-dusk.png" alt="Cerulean City at dusk with Psyduck following"><br><sub>Cerulean City, dusk</sub></td>
    <td><img src="docs/screenshots/lavender-night.png" alt="Lavender Town at night with Gengar following"><br><sub>Lavender Town, night</sub></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/cinnabar-dusk.png" alt="Cinnabar Island at dusk with Arcanine following"><br><sub>Cinnabar Island, dusk</sub></td>
    <td><img src="docs/screenshots/fuchsia.png" alt="Fuchsia City with Snorlax following"><br><sub>Fuchsia City</sub></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/viridian-forest.png" alt="Viridian Forest with Butterfree following"><br><sub>Viridian Forest</sub></td>
    <td><img src="docs/screenshots/mt-moon.png" alt="Mt. Moon with Clefairy following"><br><sub>Mt. Moon</sub></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/silph-co.png" alt="Silph Co. with Porygon following"><br><sub>Silph Co.</sub></td>
    <td><img src="docs/screenshots/pokemon-mansion.png" alt="Pokémon Mansion with Growlithe following"><br><sub>Pokémon Mansion</sub></td>
  </tr>
</table>

**Day and night.** Outdoors the light follows the console's clock (or a day
that passes in 24 minutes, or stays off - OPTIONS > DAY/NIGHT):

<table>
  <tr>
    <td><img src="docs/screenshots/pallet-dawn.png" alt="Pallet Town at dawn"><br><sub>Dawn</sub></td>
    <td><img src="docs/screenshots/pallet-day.png" alt="Pallet Town by day"><br><sub>Day</sub></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/pallet-dusk.png" alt="Pallet Town at dusk"><br><sub>Dusk</sub></td>
    <td><img src="docs/screenshots/pallet-night.png" alt="Pallet Town at night"><br><sub>Night</sub></td>
  </tr>
</table>

## Development

### Web installer

The browser UI lives in `site/`. The worker runs the Python builder in
Pyodide so the ROM stays on the player’s device. The direct installer uses
Chrome's File System Access API and remembers the chosen folder in IndexedDB.

```sh
node --test tools/tests/azahar.test.mjs
python -m unittest discover -s builder/tests
python tools/build_site.py --windows-zip FireRed3DS-v0.5.1-Windows.zip --tag v0.5.1 --cia --out build/site
python tools/release_audit.py --zip build/site/payload/FireRed3DS-WebPayload.zip --web-payload --strict
```

The site build requires Pillow and the matching upstream Windows release ZIP.
The fork serves the assembled site from the `gh-pages` branch.

### Native 3DS port

#### Standalone cartridge image for Azahar

Build locally with devkitARM, libctru, citro2d, citro3d, the host tools
required by the decompilation, and Project CTR's `makerom` on PATH.

```sh
python tools/bootstrap.py --dir build/upstream
make -C build/upstream tools generated
make -C build/upstream/3ds_port standalone
```

The target writes `build/upstream/3ds_port/dist/FireRed3DS.3ds`. Its RomFS
contains the game data, so no SD data pack is needed. Select **HLE** audio
emulation in Azahar. The image supplies its own HLE DSP component and uses
Azahar's virtual SD card for saves and settings. Build the cartridge image
locally for personal use. To refresh the browser cartridge, the cartridge
workflow compiles a template with an empty RomFS data slot and generates
the extraction recipe for that exact engine. Run
`tools/build_cartridge_payload.py` on the resulting template and release
ZIP to assemble the assets under `cartridge-audio/payload/` on the site.

The source tree is the pinned decomp plus this project's patches and port:

```sh
python tools/bootstrap.py --dir C:/fr3ds/upstream     # pret/pokefirered + patches/ + 3ds_port/
make -C C:/fr3ds/upstream/3ds_port all                 # devkitARM, libctru, citro2d/3d
```

`make all` embeds the game data built from the decomp (a development build);
`make release` builds the executable alone. `tools/build_release.py` makes a
release: the recipe the builder rebuilds the data from (`tools/gen_recipe.py`),
the payload, the standalone builder and an audit that nothing from the game
is inside (`tools/release_audit.py`).

| Path | What |
|---|---|
| `patches/pokefirered/` | the changes to the decomp, one patch per topic |
| `3ds_port/` | the 3DS platform layer, renderer, voxel world and bottom screen |
| `3ds_port/scripts/` | generators of the 3D world from the game's art |
| `builder/` | the player's builder: ROM to data pack |
| `tools/` | bootstrap, patch export, release tools |

## Support upstream development

If you want to support development of the original port, the upstream project
accepts voluntary donations through PayPal.

[![Donate with PayPal](https://img.shields.io/badge/Donate-PayPal-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/donate/?hosted_button_id=YRCM45GNZ59XW)

## Acknowledgements

This project is a fork of
[NachoGonzalez2001/Pokémon FireRed 3DS](https://github.com/NachoGonzalez2001/Pokemon-FireRed-3DS).
The original port, game features, and screenshots come from upstream.

Special thanks to **[ZallaxDev](https://github.com/ZallaxDev)**, creator of
[Pokémon Emerald 3Ds Dual Screen](https://github.com/ZallaxDev/pokeemerald-3Ds-dualscreen).
This project stands on that port: its 3DS platform layer, audio, bottom-screen
design, voxel renderer and tooling are where this one started, and its
approach to bringing a GBA Pokémon game to both screens of the 3DS made this
port possible.

Thanks as well to the [pret](https://github.com/pret) team for the
pokefirered decompilation.

See [NOTICE.md](NOTICE.md) for credits and licences. Pokémon FireRed 3DS is an
unofficial fan project, not affiliated with or endorsed by Nintendo, Game
Freak, Creatures or The Pokémon Company.

## Graphics upgrade candidate

See [rendering paths, controls and validation status](docs/graphics-upgrade.md). The climate effects remain opt-in; candidate builds are not releases until their Thor checks pass.
