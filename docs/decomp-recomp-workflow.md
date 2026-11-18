# Decompilation and native port workflow

Use this workflow for the FireRed, FRLG+ and Pokémon Classic 3DS ports and the PokéDaisy profiles.

## Reproduce and build

1. Record the game revision, input SHA-1, upstream commit, toolchain, and test save. For a matching GBA decompilation, build the baseline and compare its checksum where the project supports it. Replay the same save and inputs in mGBA to establish the original behavior. [Pret build instructions](https://github.com/pret/pokeemerald/blob/master/INSTALL.md)
2. Trace the native failure from the first emulator error. Save a small log excerpt, the faulting PC, and the engine hash. Use the matching linked ELF or symbol table. With only a 3DSX, extract its code segment and disassemble it at the text load address reported by the emulator. Correlate the instructions with the pinned source and test the smallest change.
3. Build the engine and its recipe from the same commit. Record the workflow run, engine and pack SHA-256, and pack ABI. Keep local ROMs and saves out of Git and keep the public builder on the audited engine and recipe. Rebuild the install artifact from the exact input before promoting it.
4. Compare the same test save on the Thor with voxel mode on and off when diagnosing renderer faults. Capture both displays, distinguish game frames from frames drawn, and record the test result for cold start, map transitions, first battle, Party, Bag, Map, and reload. Check PokéDaisy separately inside its GBA emulator. Restore the user's saves after testing.

Use PoryMap or the source map JSON to identify a tile, section, or object before editing it. Keep PC decoding and tile checks in small scripts that can run against new builds. This project has matching GBA sources and builds ARM-native 3DS code with devkitARM. N64Recomp is a separate N64-specific workflow that illustrates the value of retaining symbols. [PoryMap project](https://github.com/huderlem/porymap) · [N64Recomp project](https://github.com/N64Recomp/N64Recomp)

When the Azahar log reports a fault in a homebrew build and gives the text segment base, use [the 3DSX PC helper](../tools/azahar_3dsx_pc.py). It prints the engine hash and instructions around the reported PC. Add `--objdump` with an explicit path if devkitARM is outside `PATH`.

```sh
python tools/azahar_3dsx_pc.py Emerald3DS.3dsx 0x266fe0 --text-base 0x100000
```

## Parallel work

Assign one worktree and one branch or read-only investigation to each agent. Give the connected Thor to one integration owner so inputs and save changes stay attributable. Use the branch or CI commit as the source of truth, with a short handoff that identifies the next thing to verify. [Reddit worktree discussion](https://www.reddit.com/r/codex/comments/1xu5qzc/running_codex_and_claude_code_on_the_same_repo/) · [Git worktree documentation](https://git-scm.com/docs/git-worktree)

For a regression with a repeatable exit condition, use the fixture and a script to drive `git bisect run` in its own worktree. Skip revisions that cannot build with the pinned toolchain. [Git bisect documentation](https://git-scm.com/docs/git-bisect)

### Agent handoff prompts

- **Runtime** — Work in the assigned port worktree. Start from the supplied engine hash, save, and input sequence. Identify the earliest failing callback or invariant, patch the smallest owned surface, and give the coordinator the commit, matched artifact paths, checks, and remaining uncertainty.
- **Verification** — Use the supplied run and fixture. Confirm engine/recipe pairing, reproduce the original behavior, and report the pass or fail for each named test with logs or screenshots. Coordinate with the hardware owner for device work.
- **Builder and release** — Reproduce the local build from the pinned input, check the output manifest and hashes, and prepare the site on its branch. Publish after the coordinator confirms gameplay on the exact device-tested artifacts.
