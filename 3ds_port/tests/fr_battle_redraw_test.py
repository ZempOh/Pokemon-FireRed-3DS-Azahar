"""Compare production battle dirty rendering with the previous full repaint.

Raster shapes and battle layout are production code; fonts and icons are
deterministic host stand-ins. Also compares old/new rounded raster primitives
byte for byte, including clipping, independently of dirty-region decisions.
"""
from pathlib import Path
import argparse, subprocess, tempfile
from voxel_runtime_test import function, ROOT

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cc',default='gcc')
    args=parser.parse_args()
    text=(ROOT/'src/fr_bottom_ui.c').read_text(encoding='utf-8')
    constants='\n'.join(line for line in text.splitlines() if line.startswith('#define ') and
        (line.split()[1].startswith('C_') or line.split()[1].startswith('C8(')))
    types=text[text.index('typedef struct {'):text.index('static u16 sCanvas')]
    names=['Put','FillRect','Mix','Lighter','Darker','CornerInset','RoundRect','RoundBox','RoundGradient',
           'Disc','Ring','Header','Arrow','Footer','BackKey','MegaKey','HpBar','TypeColour',
           'ActionRect','MoveRect','BigKey','DrawPartyBalls','DrawActions','DrawMoves','DrawFighter',
           'BattleHeaderChanged','BattleBodyChanged','BattleFooterChanged','RenderBattle']
    funcs=''
    import re
    for name in names:
        match=re.search(r'static (?:inline )?\w+ '+name+r'\(',text)
        assert match,name
        funcs+=function(text,match[0])
    table=text[text.index('static const u8 sTypeRgb'):text.index('static u16 TypeColour')]
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp)
        (tmp/'battle_types.h').write_text(constants+'\n'+types)
        (tmp/'battle_functions.h').write_text(table+'\n'+funcs)
        exe=tmp/'battle-test.exe'
        subprocess.run([args.cc,'-std=gnu99','-O2','-Wall','-Wextra','-I'+str(tmp),
                        str(Path(__file__).with_suffix('.c')),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)

if __name__=='__main__':main()
