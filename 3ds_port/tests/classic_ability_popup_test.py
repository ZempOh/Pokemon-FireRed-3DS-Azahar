"""Check the native popup with a one-byte INCBIN symbol and full resolved art."""

import argparse
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--cc", default="gcc")
    args = parser.parse_args()
    battle = (args.tree / "src/battle_interface.c").read_text(encoding="utf-8")
    size = battle[battle.index("#ifdef PORT_BRIDGE\n// Two 64 x 32"):
                  battle.index("static const struct SpriteSheet sSpriteSheet_AbilityPopUp")]
    implementation = battle[battle.index("#define PIXEL_COORDS_TO_OFFSET"):
                            battle.index("void CreateAbilityPopUp(")]
    harness = r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
#define PORT_BRIDGE
#define ARRAY_COUNT(array) (sizeof(array) / sizeof((array)[0]))
#define CpuCopy32(src, dst, bytes) memcpy((dst), (src), (bytes))
static const u8 sAbilityPopUpGfx[1] = {0};
''' + size + r'''
static u8 art[ABILITY_POP_UP_GFX_BYTES], tiles[ABILITY_POP_UP_GFX_BYTES];
static u8 heap[ABILITY_POP_UP_GFX_BYTES + 2];
static u32 assetSize = sizeof(art);
static unsigned allocations, frees;
static int available = 1;
static u32 Port_GetAssetSizeExact(const void *ptr)
{
    assert(ptr == sAbilityPopUpGfx);
    return assetSize;
}
static const void *Port_ResolveAssetPointer(const void *ptr)
{
    assert(ptr == sAbilityPopUpGfx);
    return available ? art : ptr;
}
static void *Alloc(u32 size)
{
    assert(size == sizeof(art));
    ++allocations;
    return heap + 1;
}
static void Free(void *p)
{
    assert(p == heap + 1);
    ++frees;
}
''' + implementation + r'''
int main(void)
{
    u8 expected[sizeof(tiles)];
    assert(sizeof(art) == 2048);
    memset(heap, 0xcd, sizeof(heap));
    memset(tiles, 0x23, sizeof(tiles));
    memset(art, 0xa5, sizeof(art));
    memcpy(expected, tiles, sizeof(tiles));
    for (size_t i = 0; i < ARRAY_COUNT(sOverwrittenPixelsTable); ++i)
    {
        unsigned offset = sOverwrittenPixelsTable[i][0];
        unsigned count = sOverwrittenPixelsTable[i][1];
        assert(offset + (count + 1) / 2 <= sizeof(expected));
        for (unsigned pixel = 0; pixel < count; ++pixel)
        {
            unsigned mask = 0xf << (4 * (pixel & 1));
            unsigned byte = offset + pixel / 2;
            expected[byte] = (expected[byte] & ~mask) | (art[byte] & mask);
        }
    }
    assetSize = 1;
    RestoreOverwrittenPixels(tiles);
    assert(allocations == 0);
    assetSize = sizeof(art);
    available = 0;
    RestoreOverwrittenPixels(tiles);
    assert(allocations == 0);
    available = 1;
    RestoreOverwrittenPixels(tiles);
    assert(allocations == 1 && frees == 1);
    assert(heap[0] == 0xcd && heap[sizeof(heap) - 1] == 0xcd);
    assert(memcmp(tiles, expected, sizeof(tiles)) == 0);
    puts("PASS Classic ability popup: full sheet, bounded pixel restore, missing assets");
}
'''
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        source = root / "popup.c"
        binary = root / "popup.exe"
        source.write_text(harness, encoding="utf-8")
        subprocess.run(
            [args.cc, "-std=c99", "-Wall", "-Wextra", "-Werror", str(source), "-o", str(binary)],
            check=True,
        )
        subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    main()
