"""Compare the actual bottom glyph cache against uncached Latin rendering.

Requires a bootstrapped FireRed source tree, GCC and Pillow, but no ROM or
generated game assets. Upstream PNGs are packed as indexed two-bit rows and
converted by the extracted upstream gbagfx Latin-font converters. Actual
palette lookup/decompression and bottom text functions run on both paths.
Japanese branches are not exercised: Port_DecompressGlyph selects Latin.
"""
from pathlib import Path
import argparse
import re
import subprocess
import tempfile
from PIL import Image

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--tree', required=True, type=Path)
p.add_argument('--cc', default='gcc')
a = p.parse_args()
port = Path(__file__).resolve().parents[1]
bottom = (port/'src/fr_bottom_ui.c').read_text()
text = (a.tree/'src/text.c').read_text()
printer = (a.tree/'src/text_printer.c').read_text()
converter = (a.tree/'tools/gbagfx/font.c').read_text()


def function(source, name):
    match = re.search(r'^(?:(?:static|inline)\s+)*(?:void|int|u8|u16)\s+'
                      + name + r'\([^)]*\)\s*\{', source, re.M)
    assert match, name
    end, depth = match.end(), 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end]


def array(source, name):
    match = re.search(r'static const (?:u8|u16) ' + name
                      + r'\[\]\s*=\s*\{.*?\};', source, re.S)
    assert match, name
    return match[0]


parts = [array(printer, 'sFontHalfRowOffsets')]
for name in ['GenerateFontHalfRowLookupTable', 'DecompressGlyphTile', 'GetLastTextColor']:
    source = function(printer, name)
    # The upstream signed left-shift tests the low bit on its 32-bit target.
    # Use the equivalent defined expression for host optimization/sanitizers.
    if name == 'DecompressGlyphTile':
        assert '(i << 31)' in source
        source = source.replace('(i << 31)', '(i & 1)')
    parts.append(source)
for name in ['ConvertToHalfWidthLatinFont', 'ConvertToFullWidthLatinFont']:
    parts.append(function(converter, name))
initializers = []
for short, stem in [('Small', 'small'), ('Normal', 'normal'), ('Male', 'male'), ('Female', 'female')]:
    image = Image.open(a.tree/f'graphics/fonts/latin_{stem}.png')
    assert image.mode == 'P' and image.width == 256 and image.height % 16 == 0
    pixels = image.tobytes()
    assert max(pixels) <= 3
    packed = [sum(pixels[i+j] << (6-2*j) for j in range(4)) for i in range(0, len(pixels), 4)]
    parts.append(f'static u8 png{short}[] = {{' + ','.join(map(str, packed)) + '};')
    parts.append(f'static u16 sFont{short}LatinGlyphs[{len(packed)//2}];')
    parts.append(array(text, f'sFont{short}LatinGlyphWidths'))
    # These declarations satisfy the uncalled Japanese branches. The wrapper
    # under test always passes FALSE and no Japanese data is manufactured.
    parts.append(f'static const u16 sFont{short}JapaneseGlyphs[1] = {{0}};')
    if short != 'Small':
        parts.append(f'static const u8 sFont{short}JapaneseGlyphWidths[1] = {{0}};')
    conversion = 'Half' if short == 'Small' else 'Full'
    initializers.append(f'ConvertTo{conversion}WidthLatinFont(png{short}, (u8 *)sFont{short}LatinGlyphs, {image.height//16});')
    parts.append(function(text, 'DecompressGlyph_' + short))
parts.append(function(text, 'Port_DecompressGlyph').replace('{', '{\n    ++sDecompressCalls;', 1))
parts.append(function((a.tree/'src/string_util.c').read_text(), 'GetExtCtrlCodeLength'))
cache = bottom[bottom.index('typedef struct {\n    struct GlyphInfo info;'):bottom.index('static u16 NextChar')]
parts.append(cache)
parts += [function(bottom, name) for name in ['Put', 'NextChar']]
names = ['DrawGlyph', 'Text', 'TextWidth', 'TextCentered', 'TextRight']
production = '\n\n'.join(function(bottom, name) for name in names)
parts.append(production)
reference = production.replace('CacheGlyph(font, c)', 'Port_DecompressGlyph(font, c)')
for name in sorted(names, key=len, reverse=True):
    reference = re.sub(r'\b' + name + r'\b', 'Ref_' + name, reference)
parts.append(reference)
parts.append('static void InitFontData(void) {\n' + '\n'.join(initializers) + '\n}')
assert 'ResetGlyphCache();' in function(bottom, 'CtrBottom_Init')
reset = bottom.index('if (CtrGame_Resets() != sResetsSeen)')
assert 'ResetGlyphCache();' in bottom[reset:bottom.index('if (!sInGame', reset)]

with tempfile.TemporaryDirectory() as folder:
    folder = Path(folder)
    (folder/'bottom_glyph_under_test.inc').write_text('\n\n'.join(parts))
    exe = folder/'bottom-glyph-cache-test.exe'
    subprocess.run([a.cc, '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-I'+str(folder), str(Path(__file__).with_suffix('.c')), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
