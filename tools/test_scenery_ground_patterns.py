"""Reused cliff tiles become winter soil only inside a complete reviewed plot."""
import copy, json, shutil, subprocess, tempfile, unittest
from pathlib import Path
from gen_scenery_ground_patterns import generate_ground_patterns

PROFILES=json.loads(Path(__file__).with_name('scenery-profiles').joinpath('android-ground-patterns.json').read_text())

class GroundPatterns(unittest.TestCase):
    def test_reject_incomplete_or_unreviewed_patterns(self):
        for mutate in (lambda p:p['cells'].pop(), lambda p:p.update(reviewed=False), lambda p:p.update(width=5), lambda p:p['cells'][0].update(rgba_sha256='')):
            rows=copy.deepcopy(PROFILES);mutate(rows[0])
            with tempfile.TemporaryDirectory() as tmp, self.assertRaises(AssertionError):
                generate_ground_patterns(rows,Path(tmp))

    def test_berry_ground_does_not_register_individual_cliff_cells(self):
        caps=json.loads(Path(__file__).with_name('scenery-profiles').joinpath('android-capabilities.json').read_text())
        cap=next(p for p in caps if p['game']=='classic')
        ids={x['id'] for x in PROFILES[0]['cells']}
        self.assertEqual(ids,{0xa5,0xa6,0x2d5,0x7f,0xad,0xae,0x2d6,0x7e})
        self.assertEqual((PROFILES[0]['width'],PROFILES[0]['height']),(4,2))
        self.assertFalse(any(ids & set(p['ids']) for p in cap['land']))

    @unittest.skipUnless(shutil.which('cc') or shutil.which('gcc'),'C compiler unavailable locally; required in CI')
    def test_real_lookup_requires_complete_identity_and_neighbors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);generate_ground_patterns(PROFILES,root)
            source=root/'test.c'
            source.write_text('''#include <assert.h>
#include "pk_scenery_ground_patterns.h"
static int cells[]={0xa5,0xa6,0x2d5,0x7f,0xad,0xae,0x2d6,0x7e};
static int wrong_pair=0;
static int read_cell(const void *ctx,int x,int y,uint32_t *a,uint32_t *b) {
 (void)ctx;*a=0x84ad600;*b=0x84add10;
 if(x<0 || x>=4 || y<0 || y>=2)return -1;
 if(wrong_pair && x==3 && y==1)*b+=4;
 return cells[y*4+x];
}
int main(void) {
 for(int i=0;i<8;i++)assert(sceneryPatternLand(0xe4deb9be,0x84ad600,0x84add10,cells[i],i%4,i/4,0,read_cell));
 for(int i=0;i<8;i++) {
  int old=cells[i];cells[i]=8;
  for(int j=0;j<8;j++)assert(!sceneryPatternLand(0xe4deb9be,0x84ad600,0x84add10,cells[j],j%4,j/4,0,read_cell));
  cells[i]=old;
 }
 assert(!sceneryPatternLand(0xe4deb9bf,0x84ad600,0x84add10,cells[0],0,0,0,read_cell));
 assert(!sceneryPatternLand(0xe4deb9be,0x84ad604,0x84add10,cells[0],0,0,0,read_cell));
 assert(!sceneryPatternLand(0xe4deb9be,0x84ad600,0x84add14,cells[0],0,0,0,read_cell));
 wrong_pair=1;
 for(int i=0;i<8;i++)assert(!sceneryPatternLand(0xe4deb9be,0x84ad600,0x84add10,cells[i],i%4,i/4,0,read_cell));
 return 0;
}
''')
            exe=root/'test'
            subprocess.run([shutil.which('cc') or shutil.which('gcc'),'-std=c99','-Wall','-Wextra','-Werror',str(source),'-o',str(exe)],check=True)
            subprocess.run([str(exe)],check=True)

if __name__=='__main__':unittest.main()
