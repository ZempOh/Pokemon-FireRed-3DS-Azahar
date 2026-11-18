#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint8_t bool8;
typedef uint32_t bool32;
#define TRUE 1
#define FALSE 0
#define W 320
#define H 240
#define FONT_SMALL 0
#define FONT_NORMAL 2
#define FONT_MALE 4
#define FONT_FEMALE 5
#define FONTATTR_LETTER_SPACING 2
#define EOS 0xFF
#define CHAR_NEWLINE 0xFE
#define CHAR_EXTRA_SYMBOL 0xF9
#define CHAR_LV_2 5
#define CHAR_LV 0x34
#define EXT_CTRL_CODE_BEGIN 0xFC
#define GLYPHS(base) (base)
#define NELEMS(a) (sizeof(a)/sizeof((a)[0]))

struct GlyphInfo { u8 pixels[128]; u8 width, height; };
static struct GlyphInfo gGlyphInfo;
static u16 sFontHalfRowLookupTable[81];
static u16 sLastTextBgColor, sLastTextFgColor, sLastTextShadowColor;
static u16 *sCanvas;
static u16 sActual[W*H], sReference[W*H];
static unsigned sDecompressCalls, sChecks;
/* Spacing is deliberately variable: the cache must not freeze an attribute. */
static u8 sSpacing[8];
static u8 GetFontAttribute(u8 font, u8 attribute)
{
    assert(attribute == FONTATTR_LETTER_SPACING);
    return sSpacing[font];
}

#include "bottom_glyph_under_test.inc"

static u32 sRandom = 0x53f19b2d;
static u32 Random(void)
{
    sRandom ^= sRandom << 13;
    sRandom ^= sRandom >> 17;
    sRandom ^= sRandom << 5;
    return sRandom;
}

static int Call(bool8 reference, int mode, u8 font, u16 c, const u8 *text,
                int x, int y, u16 fg, u16 shadow)
{
    if (reference)
    {
        switch (mode)
        {
        case 0: return Ref_DrawGlyph(font, c, x, y, fg, shadow, TRUE);
        case 1: return Ref_Text(font, text, x, y, fg, shadow, TRUE);
        case 2: return Ref_TextWidth(font, text);
        case 3: Ref_TextCentered(font, text, x, y, fg, shadow); return 0;
        default: Ref_TextRight(font, text, x, y, fg, shadow); return 0;
        }
    }
    switch (mode)
    {
    case 0: return DrawGlyph(font, c, x, y, fg, shadow, TRUE);
    case 1: return Text(font, text, x, y, fg, shadow, TRUE);
    case 2: return TextWidth(font, text);
    case 3: TextCentered(font, text, x, y, fg, shadow); return 0;
    default: TextRight(font, text, x, y, fg, shadow); return 0;
    }
}

static void Check(int mode, u8 font, u16 c, const u8 *text, int x, int y)
{
    struct GlyphInfo before, expected;
    u16 table[81], expectedColors[3];
    u16 fg = (u16)Random(), shadow = (u16)Random();
    u8 paletteFg = Random() & 15, paletteBg = Random() & 15, paletteShadow = Random() & 15;
    int expectedWidth, actualWidth;
    for (unsigned i = 0; i < NELEMS(sActual); ++i)
        sActual[i] = sReference[i] = (u16)(i ^ (sChecks * 931));
    for (unsigned i = 0; i < sizeof(before); ++i)
        ((u8 *)&before)[i] = (u8)Random();
    sSpacing[font] = sChecks % 4;
    gGlyphInfo = before;
    GenerateFontHalfRowLookupTable(paletteFg, paletteBg, paletteShadow);
    sCanvas = sReference;
    expectedWidth = Call(TRUE, mode, font, c, text, x, y, fg, shadow);
    expected = gGlyphInfo;
    memcpy(table, sFontHalfRowLookupTable, sizeof(table));
    expectedColors[0] = sLastTextFgColor;
    expectedColors[1] = sLastTextBgColor;
    expectedColors[2] = sLastTextShadowColor;
    gGlyphInfo = before;
    GenerateFontHalfRowLookupTable(paletteFg, paletteBg, paletteShadow);
    sCanvas = sActual;
    actualWidth = Call(FALSE, mode, font, c, text, x, y, fg, shadow);
    assert(actualWidth == expectedWidth);
    assert(memcmp(sActual, sReference, sizeof(sActual)) == 0);
    assert(memcmp(&gGlyphInfo, &expected, sizeof(expected)) == 0);
    assert(memcmp(table, sFontHalfRowLookupTable, sizeof(table)) == 0);
    assert(sLastTextFgColor == expectedColors[0] && sLastTextBgColor == expectedColors[1]
           && sLastTextShadowColor == expectedColors[2]);
    ++sChecks;
}

static void CheckCacheWork(void)
{
    /* A repeated twelve-character name: width and draw each used to rebuild
     * and restore the lookup for every character. Count decompressions, not
     * host elapsed time or a claimed Thor performance percentage. */
    const u8 name[] = {0xBD,0xC2,0xBB,0xCC,0xC7,0xBB,0xC8,0xBE,0xBF,0xCC,0xBB,0xBB,EOS};
    unsigned oldCalls, coldCalls;
    sCanvas = sActual;
    ResetGlyphCache();
    sDecompressCalls = 0;
    Ref_TextCentered(FONT_NORMAL, name, 160, 10, 0xFFFF, 0x2000);
    oldCalls = sDecompressCalls;
    sDecompressCalls = 0;
    TextCentered(FONT_NORMAL, name, 160, 10, 0xFFFF, 0x2000);
    coldCalls = sDecompressCalls;
    assert(oldCalls == 24 && coldCalls > 0 && coldCalls < oldCalls);
    sDecompressCalls = 0;
    for (int i = 0; i < 100; ++i)
        TextCentered(FONT_NORMAL, name, 160, 10, (u16)i, (u16)(i + 1));
    assert(sDecompressCalls == 0);
    /* Same slot, distinct character and font keys must cause fresh loads. */
    ResetGlyphCache();
    sDecompressCalls = 0;
    CacheGlyph(FONT_NORMAL, 5);
    CacheGlyph(FONT_NORMAL, 5);
    assert(sDecompressCalls == 1);
    CacheGlyph(FONT_NORMAL, 133);
    CacheGlyph(FONT_NORMAL, 5);
    CacheGlyph(FONT_SMALL, 69);
    assert(sDecompressCalls == 4);
    ResetGlyphCache();
    CacheGlyph(FONT_SMALL, 69);
    assert(sDecompressCalls == 5);
    printf("Twelve-character centered name: %u uncached calls, %u cold cached, zero for 100 warm repeats\n",
           oldCalls, coldCalls);
}

int main(void)
{
    static const u8 fonts[] = {FONT_SMALL, FONT_NORMAL, FONT_MALE, FONT_FEMALE};
    static const int positions[][2] = {{4,4},{-4,-3},{316,233},{325,247}};
    static const u8 controls[] = {0xBB,CHAR_EXTRA_SYMBOL,CHAR_LV_2,0xA1,
        EXT_CTRL_CODE_BEGIN,4,1,2,3,0xBC,CHAR_EXTRA_SYMBOL,2,0xBD,CHAR_NEWLINE,0xBE,EOS};
    static const u8 empty[] = {EOS};
    u8 text[48];
    InitFontData();
    ResetGlyphCache();
    /* All 256 byte glyph values in each supported bottom font, each cold
     * then warm with independently changed scratch bytes, colors and spacing. */
    for (unsigned f = 0; f < NELEMS(fonts); ++f)
        for (unsigned c = 0; c < 256; ++c)
            for (unsigned pos = 0; pos < NELEMS(positions); ++pos)
            {
                Check(0, fonts[f], c, NULL, positions[pos][0], positions[pos][1]);
                Check(0, fonts[f], c, NULL, positions[pos][0], positions[pos][1]);
            }
    for (int i = 0; i < 1200; ++i)
    {
        unsigned length = Random() % 40;
        for (unsigned j = 0; j < length; ++j) text[j] = (u8)(Random() % 0xF9);
        text[length] = EOS;
        if (i % 37 == 0) ResetGlyphCache();
        Check(1 + i % 4, fonts[i % NELEMS(fonts)], 0,
              i % 11 == 0 ? controls : i % 13 == 0 ? empty : text,
              (int)(Random() % 380) - 30, (int)(Random() % 280) - 20);
    }
    /* Explicit colliding cache entries with different preexisting scratch. */
    for (int i = 0; i < 60; ++i)
    {
        Check(0, FONT_NORMAL, 5, NULL, 10, 10);
        Check(0, FONT_NORMAL, 133, NULL, 10, 10);
        Check(0, FONT_SMALL, 69, NULL, 10, 10);
    }
    CheckCacheWork();
    printf("%u full-canvas/width/glyph-scratch/palette comparisons passed using real Latin font PNGs and production decompression\n", sChecks);
    return 0;
}
