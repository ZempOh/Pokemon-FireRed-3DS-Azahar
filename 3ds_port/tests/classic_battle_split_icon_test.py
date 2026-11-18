"""Blit Classic's three battle categories from resolved art, not an INCBIN marker."""

import argparse
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--cc", default="gcc")
    args = parser.parse_args()
    source = (args.tree / "src/battle_controller_player.c").read_text(encoding="utf-8")
    start = source.index("static void MoveSelectionDisplaySplitIcon(void){")
    implementation = source[start:source.index("\n}", start) + 2]
    harness = r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint8_t u8;
typedef uint16_t u16;
#define PORT_BRIDGE
#define INCBIN_U8(path) {0}
#define INCBIN_U16(path) {0}
#define B_WIN_DUMMY 7
#define PIXEL_FILL(value) ((value) | ((value) << 4))
struct ChooseMoveStruct { u16 moves[4]; };
static struct { u8 bufferA[1][12]; } resources, *gBattleResources = &resources;
static u8 gActiveBattler, gMoveSelectionCursor[1];
static u8 art[3 * 0x80], copied[0x80];
static unsigned assetSize = sizeof(art), resolves, blits, clears, tilemaps, copies;
static int available = 1, selected;
static const void *marker;
static int GetBattleMoveSplit(u16 move) { assert(move == 42); return selected; }
static unsigned Port_GetAssetSizeExact(const void *ptr) { marker = ptr; return assetSize; }
static const void *Port_ResolveAssetPointer(const void *ptr)
{
    assert(ptr == marker);
    ++resolves;
    return available ? art : ptr;
}
static void LoadPalette(const void *ptr, unsigned at, unsigned size)
{
    assert(ptr && at == 160 && size == 32);
}
static void BlitBitmapToWindow(unsigned win, const u8 *pixels, unsigned x, unsigned y,
                               unsigned width, unsigned height)
{
    assert(win == B_WIN_DUMMY && x == 0 && y == 0 && width == 16 && height == 16);
    assert(pixels == art + selected * 0x80);
    memcpy(copied, pixels, sizeof(copied));
    ++blits;
}
static void FillWindowPixelBuffer(unsigned win, unsigned fill)
{
    assert(win == B_WIN_DUMMY && fill == 0x77);
    memset(copied, fill, sizeof(copied));
    ++clears;
}
static void PutWindowTilemap(unsigned win) { assert(win == B_WIN_DUMMY); ++tilemaps; }
static void CopyWindowToVram(unsigned win, unsigned mode)
{
    assert(win == B_WIN_DUMMY && mode == 3);
    ++copies;
}
''' + implementation + r'''
int main(void)
{
    u16 move = 42;
    memcpy(resources.bufferA[0] + 4, &move, sizeof(move));
    for (unsigned i = 0; i < sizeof(art); ++i)
        art[i] = (u8)(i * 7 + i / 0x80);
    for (selected = 0; selected < 3; ++selected)
    {
        MoveSelectionDisplaySplitIcon();
        assert(memcmp(copied, art + selected * 0x80, sizeof(copied)) == 0);
    }
    assert(blits == 3 && resolves == 3 && clears == 0);
    assetSize = 1;
    MoveSelectionDisplaySplitIcon();
    assert(resolves == 3 && blits == 3 && clears == 1);
    assetSize = sizeof(art);
    available = 0;
    selected = 1;
    MoveSelectionDisplaySplitIcon();
    assert(blits == 3 && clears == 2);
    available = 1;
    selected = 3;
    MoveSelectionDisplaySplitIcon();
    assert(blits == 3 && clears == 3);
    assert(tilemaps == 6 && copies == 6);
    for (unsigned i = 0; i < sizeof(copied); ++i)
        assert(copied[i] == 0x77);
    puts("PASS Classic split icons: all three resolved bitmaps, missing assets, bounded category");
}
'''
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "split_icon.c"
        binary = root / "split_icon.exe"
        source.write_text(harness, encoding="utf-8")
        subprocess.run([args.cc, "-std=c99", "-Wall", "-Wextra", "-Werror", str(source),
                        "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    main()
