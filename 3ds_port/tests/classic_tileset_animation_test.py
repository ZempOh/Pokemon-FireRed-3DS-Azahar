"""Exercise Classic's actual tileset queue/transfer with external frame markers."""

import argparse
from pathlib import Path
import re
import subprocess
import tempfile


def function(source, signature):
    start = source.index(signature + "\n{")
    body = source.index("{", start)
    depth = 1
    end = body + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", required=True, type=Path)
    parser.add_argument("--cc", default="gcc")
    args = parser.parse_args()
    source = (args.tree / "src/tileset_anims.c").read_text(encoding="utf-8")
    declarations = []
    for pattern in [
        r"static EWRAM_DATA u16 sTilesetAnimData\[[^;]+;",
        r"static u16 sTilesetAnimDataSize;",
        r"static EWRAM_DATA struct \{.*?\} sTilesetDMA3TransferBuffer\[[^;]+;",
        r"static u8 sTilesetDMA3TransferBufferSize;",
    ]:
        match = re.search(pattern, source, re.S)
        assert match, "Native tileset staging declaration missing: " + pattern
        declarations.append(match[0])
    functions = [function(source, name) for name in [
        "static void ResetTilesetAnimBuffer(void)",
        "static void AppendTilesetAnimToBuffer(const u16 *src, u16 *dest, u16 size)",
        "void TransferTilesetAnimsBuffer(void)",
    ]]
    harness = r'''
#include <assert.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
typedef uint8_t u8;
typedef uint16_t u16;
#define PORT_BRIDGE
#define PLATFORM_3DS
#define EWRAM_DATA
#define ARRAY_COUNT(array) (sizeof(array) / sizeof((array)[0]))
#define CpuFill32(value, dest, size) memset(dest, value, size)
static const u16 markers[2] = {0xDEAD, 0xBEEF};
static u8 assets[2][4608];
static u16 vram[4096];
static unsigned reads, notices, available = 1, requested;
static void *notified[20];
static unsigned notifiedBytes[20];
static bool Port_IsAssetStub(const void *ptr)
{
    return ptr == &markers[0] || ptr == &markers[1];
}
static bool Port_LoadAssetPointerToBufferSized(const void *ptr, void *dest, unsigned size)
{
    assert(Port_IsAssetStub(ptr));
    assert(size <= sizeof(assets[0]));
    ++reads;
    requested += size;
    if (!available) return false;
    memcpy(dest, assets[ptr == &markers[1]], size);
    return true;
}
static void CtrVideo_NotifyTilesetAnimWrite(void *dest, unsigned size)
{
    assert(notices < ARRAY_COUNT(notified));
    notified[notices] = dest;
    notifiedBytes[notices++] = size;
}
''' + "\n".join(declarations + functions) + r'''
int main(void)
{
    for (unsigned i = 0; i < sizeof(assets[0]); ++i)
    {
        assets[0][i] = (u8)(i * 3u + 1u);
        assets[1][i] = (u8)(i * 7u + 5u);
    }
    memset(vram, 0x55, sizeof(vram));
    ResetTilesetAnimBuffer();
    AppendTilesetAnimToBuffer(&markers[0], vram, 128);
    AppendTilesetAnimToBuffer(&markers[1], vram + 64, 128);
    assert(reads == 2 && requested == 256 && notices == 0);
    assert(vram[0] == 0x5555); /* no VRAM writes before transfer */
    TransferTilesetAnimsBuffer();
    assert(reads == 2); /* no file I/O during VBlank */
    assert(memcmp(vram, assets[0], 128) == 0);
    assert(memcmp(vram + 64, assets[1], 128) == 0);
    assert(notices == 2 && notified[0] == vram && notifiedBytes[0] == 128);
    assert(notified[1] == vram + 64 && notifiedBytes[1] == 128);
    TransferTilesetAnimsBuffer();
    assert(notices == 2); /* drained */

    /* A later animation frame replaces the pixels and issues a fresh notice. */
    notices = 0;
    ResetTilesetAnimBuffer();
    AppendTilesetAnimToBuffer(&markers[1], vram, 128);
    TransferTilesetAnimsBuffer();
    assert(memcmp(vram, assets[1], 128) == 0 && notices == 1);

    /* Missing assets retain the previous frame, with no stale queued write. */
    notices = 0;
    available = 0;
    ResetTilesetAnimBuffer();
    AppendTilesetAnimToBuffer(&markers[0], vram, 128);
    TransferTilesetAnimsBuffer();
    assert(memcmp(vram, assets[1], 128) == 0 && notices == 0);
    available = 1;

    /* Kanto's 48-tile update and largest 96-tile secondary fit together. */
    ResetTilesetAnimBuffer();
    AppendTilesetAnimToBuffer(&markers[0], vram, 48 * 32);
    AppendTilesetAnimToBuffer(&markers[1], vram + 48 * 16, 96 * 32);
    unsigned before = reads;
    AppendTilesetAnimToBuffer(&markers[0], vram, 2); /* full staging budget */
    assert(reads == before && sTilesetDMA3TransferBufferSize == 2);
    TransferTilesetAnimsBuffer();
    assert(memcmp(vram, assets[0], 48 * 32) == 0);
    assert(memcmp(vram + 48 * 16, assets[1], 96 * 32) == 0);
    assert(notices == 2);

    /* Ordinary RAM sources retain their existing behavior and bounded queue. */
    notices = 0;
    ResetTilesetAnimBuffer();
    for (unsigned i = 0; i < 21; ++i)
        AppendTilesetAnimToBuffer((const u16 *)assets[0], vram + i, 2);
    assert(sTilesetDMA3TransferBufferSize == 20);
    TransferTilesetAnimsBuffer();
    assert(notices == 20 && reads == before);
    for (unsigned i = 0; i < 20; ++i)
        assert(memcmp(vram + i, assets[0], 2) == 0);

    notices = 0;
    ResetTilesetAnimBuffer();
    AppendTilesetAnimToBuffer(&markers[0], vram, 128);
    ResetTilesetAnimBuffer();
    TransferTilesetAnimsBuffer();
    assert(notices == 0 && sTilesetAnimDataSize == 0);
    puts("PASS Classic tileset frames: resolved bytes, VBlank staging, dirty notices, frame changes, failures and limits");
}
'''
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        test = directory / "tileset_animation.c"
        binary = directory / "tileset_animation.exe"
        test.write_text(harness, encoding="utf-8")
        subprocess.run([args.cc, "-std=c99", "-Wall", "-Wextra", "-Werror", str(test),
                        "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    main()
