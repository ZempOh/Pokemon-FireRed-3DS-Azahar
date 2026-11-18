"""The battle HUD's HP and EXP fills (FillWidth, src/3ds_battle_hud.c) over
the art gen_battle_hud.py makes: no pixels draws nothing, any pixel at all
draws some opaque ink (the GBA's one pixel for HP 1), a fill never shrinks
as its pixels grow, and only a full bar is the whole capsule."""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]

# Element ids and the GBA's scale of each fill (gen_battle_hud.py, B_*_PIXELS).
FILLS = {9: 48, 10: 48, 11: 48, 12: 64}


def function(source, signature):
    start = source.index(signature)
    brace = source.index('{', start)
    depth, end = 1, brace + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end] + '\n'


def check_classic_menu_band(cc, directory):
    video = (ROOT / 'src/3ds_video.c').read_text(encoding='utf-8')
    draw = function(video, 'static void DrawBattleText(unsigned bg)')
    centered = draw[draw.index('    if (scrollX == 0'):draw.index('    /* The box from its left cap')]
    source = r'''
#include <assert.h>
static unsigned prompt, menu, draws;
static unsigned MapEntry(unsigned map, unsigned size, unsigned x, unsigned y)
{
    assert(map == 0 && size == 2 && y == 35);
    return x == 1 ? prompt : menu;
}
#define BATTLE_BAND_TOP 112
static void DrawBattleCut(unsigned bg, int x0, int x1, int y0, int y1, int shift)
{
    assert(bg == 0 && x0 == 0 && x1 == 240 && y0 == BATTLE_BAND_TOP && y1 == 160 && shift == 0);
    ++draws;
}
static void TryMenuBand(unsigned scrollX, unsigned scrollY)
{
    unsigned bg = 0, map = 0, size = 2;
''' + centered + r'''
}
int main(void)
{
    TryMenuBand(0, 320);
    assert(draws == 1);
    TryMenuBand(1, 320);
    TryMenuBand(0, 0);
    TryMenuBand(0, 160);
    assert(draws == 1);
    prompt = 0x51c0;
    menu = 0x5190;
    TryMenuBand(0, 160);
    assert(draws == 2);
}
'''
    harness = directory / 'menu_band.c'
    binary = directory / 'menu_band.exe'
    harness.write_text(source, encoding='utf-8')
    subprocess.run([cc, '-std=c99', '-Wall', '-Wextra', '-Werror', str(harness), '-o', str(binary)],
                   check=True)
    subprocess.run([str(binary)], check=True)
    print('PASS Classic battle menu bands: whole action and move panels, default text unchanged')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cc', default='gcc')
    parser.add_argument('--python', default=sys.executable)
    args = parser.parse_args()
    hud = (ROOT / 'src/3ds_battle_hud.c').read_text(encoding='utf-8')
    define = next(line for line in hud.splitlines() if line.startswith('#define FILL_MIN_WIDTH'))
    source = r'''
#include <stdio.h>
#include <stdlib.h>
''' + define + '\n' + function(hud, 'static int FillWidth(') + r'''
/* argv: hud.bin, then id:scale pairs. */
int main(int argc, char **argv)
{
    static unsigned char data[1 << 20];
    FILE *f = fopen(argv[1], "rb");
    size_t size = f ? fread(data, 1, sizeof(data), f) : 0;
    unsigned count = data[8] | (data[9] << 8), seen = 0;
    const unsigned char *p = data + 10;
    int fails = 0;

    for (unsigned i = 0; i < count && p + 10 <= data + size; ++i)
    {
        unsigned id = p[0];
        int w = p[6] | (p[7] << 8), h = p[8] | (p[9] << 8), scale = 0, ink = 0, last = 0;
        const unsigned char *px = p + 10;

        for (int a = 2; a < argc; ++a)
            if ((unsigned)atoi(argv[a]) == id)
                scale = atoi(argv[a] + 3);
        p = px + (size_t)w * h * 4;
        if (!scale)
            continue;
        ++seen;
        for (int k = 0; k < w * h; ++k)
            if (px[k * 4 + 3] && k % w >= ink)
                ink = k % w + 1;
        for (int pixels = 0; pixels <= scale; ++pixels)
        {
            int left, width = FillWidth(ink, h / 2, pixels, scale, &left), opaque = 0;

            for (int r = 0; r < h; ++r)
                for (int c = 0; c < ink; ++c)
                    if ((c < left || c >= ink - (width - left)) && px[(r * w + c) * 4 + 3] == 255)
                        opaque = 1;
            if ((pixels == 0) != (width == 0) || (pixels > 0 && !opaque) || width < last
                || (pixels == scale) != (width == ink))
            {
                printf("FAIL fill %u: %d of %d pixels is width %d (left %d) of ink %d, opaque %d\n",
                       id, pixels, scale, width, left, ink, opaque);
                ++fails;
            }
            last = width;
        }
    }
    if (seen != (unsigned)(argc - 2))
    {
        printf("FAIL: %u of %d fills in hud.bin\n", seen, argc - 2);
        ++fails;
    }
    return fails != 0;
}
'''
    with tempfile.TemporaryDirectory() as tmp:
        art = Path(tmp) / 'hud.bin'
        subprocess.run([args.python, str(ROOT / 'scripts/gen_battle_hud.py'), '--output', str(art)], check=True)
        harness = Path(tmp) / 'harness.c'
        harness.write_text(source)
        exe = Path(tmp) / 'fill_test'
        subprocess.run([args.cc, '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', str(harness), '-o', str(exe)],
                       check=True)
        result = subprocess.run([str(exe), str(art)] + ['%02d:%d' % item for item in FILLS.items()])
        check_classic_menu_band(args.cc, Path(tmp))
    if result.returncode:
        sys.exit('battle_hud_fill_test: failed')
    print('PASS battle hud fill: any pixel shows ink, only a full bar the whole capsule')


if __name__ == '__main__':
    main()
