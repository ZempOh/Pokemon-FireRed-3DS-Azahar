"""Pixel-differential regression for the actual software scanline compositor.

Reverse only the optimization patch into a temporary reference copy, then
compile both complete renderers against identical emulated GBA memory. No ROM
or game asset is used. Includes a repeatable synthetic battle-window benchmark.
"""
from pathlib import Path
import argparse, subprocess, tempfile, shutil

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--tree',required=True,type=Path)
ap.add_argument('--cc',default='gcc')
args=ap.parse_args()
root=Path(__file__).resolve().parents[2]
patches=list((root/'patches').rglob('*scanline-window-pacing.patch'))
assert len(patches)==1
source=args.tree.resolve()/'src/platform/gba_fast_draw.c'
exports='DrawFrame memsetu16 frameskipcounter spriteSizes gPortUiPixels gPortUiLayers gPortUiTrim gPortUiObjInWindows gPortUiScreenObj gPortDrawLines'.split()
with tempfile.TemporaryDirectory() as tmp:
    tmp=Path(tmp)
    (tmp/'src/platform').mkdir(parents=True)
    (tmp/'src/platform/gba_fast_draw.c').write_bytes(source.read_bytes())
    subprocess.run(['git','apply','--reverse',str(patches[0].resolve())],cwd=tmp,check=True)
    shutil.copytree(args.tree.resolve()/'include/gba',tmp/'gba')
    (tmp/'platform').mkdir()
    shutil.copyfile(args.tree.resolve()/'include/platform/dma.h',tmp/'platform/dma.h')
    (tmp/'global.h').write_text('''#ifndef TEST_GLOBAL_H
#define TEST_GLOBAL_H
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "gba/types.h"
#include "gba/defines.h"
#include "gba/io_reg.h"
#undef VRAM
#define VRAM ((uintptr_t)VRAM_)
#define DBGPRINTF(...) ((void)0)
#endif
''')
    flags=['-std=gnu99','-O2','-fno-strict-aliasing','-fsigned-char','-DPORTABLE','-DPORT_BRIDGE','-DRENDERER_FAST_DRAW','-I'+str(tmp)]
    for prefix,path in [('Ref',tmp/'src/platform/gba_fast_draw.c'),('New',source)]:
        subprocess.run([args.cc,*flags,*['-D'+e+'='+prefix+e for e in exports],'-c',str(path),'-o',str(tmp/(prefix+'.o'))],check=True)
    harness=Path(__file__).with_suffix('.c')
    exe=tmp/('scanline-test.exe')
    subprocess.run([args.cc,*flags,str(harness),str(tmp/'Ref.o'),str(tmp/'New.o'),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
