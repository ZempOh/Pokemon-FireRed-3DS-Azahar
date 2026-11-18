"""Run the actual presenter/upload functions against an asynchronous GPU queue.

The fake queue keeps source pointers until the next FrameBegin, detecting
buffer reuse before GPU completion. Conversion is compared with independent
RGB565/RGBA5551 reference images, including the unused texture padding.
Sparse updates also assert the coalesced flush ranges while comparing the
entire persistent image after transparency clears and source-buffer changes.
"""
from pathlib import Path
import argparse
import re
import subprocess
import tempfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--cc', default='gcc')
a = p.parse_args()
port = Path(__file__).resolve().parents[1]
source = (port/'src/3ds_soft_video.c').read_text(encoding='utf-8')

def function(name):
    match = re.search(r'static (?:inline )?void ' + name + r'\([^)]*\)\s*\{', source)
    assert match, name
    end, depth = match.end(), 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end]

present = function('GpuPresent')
assert (present.index('C3D_FrameBegin(') < present.index('GpuUploadUi(')
        < present.index('GPUCMD_AddMaskedWrite(')), 'Initial upload must precede texture cache invalidation'

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    (tmp/'soft_video_under_test.inc').write_text('\n\n'.join(
        function(name) for name in ('DoubleRow', 'GpuUpload', 'GpuUploadUi', 'GpuPresent')))
    exe = tmp/'soft-video-upload-test.exe'
    subprocess.run([a.cc, '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-I'+str(tmp), '-I'+str(port), str(Path(__file__).with_suffix('.c')),
                    '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
