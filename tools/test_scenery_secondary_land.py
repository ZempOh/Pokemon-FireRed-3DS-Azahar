"""Secondary tile IDs must never recolor another tileset's roofs or furniture."""
import copy,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
from gen_scenery_registry import generate,validate_secondary_land
ROOT=Path(__file__).parent/'scenery-profiles'
CAPS=json.loads((ROOT/'android-capabilities.json').read_text())
PROOF=json.loads((ROOT/'android-secondary-land-review.json').read_text())

class SecondaryLandTests(unittest.TestCase):
 def test_provenance(self):validate_secondary_land(CAPS,PROOF)
 def test_missing_evidence_rejected(self):
  proof=copy.deepcopy(PROOF);proof['targets'][0]['cells'].pop()
  with self.assertRaises(AssertionError):validate_secondary_land(CAPS,proof)
 def test_wrong_tileset_rejected(self):
  proof=copy.deepcopy(PROOF);proof['targets'][0]['secondary']='0x08000000'
  with self.assertRaises(AssertionError):validate_secondary_land(CAPS,proof)
 def test_unreviewed_rejected(self):
  caps=copy.deepcopy(CAPS)
  next(p for p in caps if p.get('secondary_land'))['secondary_land'][0]['reviewed']=False
  with self.assertRaises(AssertionError):validate_secondary_land(caps,PROOF)
 @unittest.skipUnless(shutil.which('cc') or shutil.which('gcc'),'Host C compiler unavailable; CI runs this test')
 def test_generated_lookup_is_identity_scoped(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);generate(CAPS,[],root)
   checks=[]
   for p in CAPS:
    for land in p.get('secondary_land',[]):
     crc=int(p['rom_crc32'],16);primary=int(land['primary'],16);secondary=int(land['secondary'],16)
     for mid in land['ids']:
      checks.append(f'assert(scenerySecondaryLand({crc}u,{primary}u,{secondary}u,{mid}));')
      for a,b,c in ((crc+1,primary,secondary),(crc,primary+4,secondary),(crc,primary,secondary+4)):
       checks.append(f'assert(!scenerySecondaryLand({a}u,{b}u,{c}u,{mid}));')
   # Explicit Fakemon roof, fence, mailbox, water and unallocated cells.
   for mid in (0x281,0x282,0x284,0x2a5,0x2d2,0x2ff):
    checks.append(f'assert(!scenerySecondaryLand(0x5e704d77,0x082d4a94,0x082d4aac,{mid}));')
   source=root/'check.c';source.write_text('#include <assert.h>\n#include "pk_scenery_candidates.h"\nint main(void){'+''.join(checks)+'return 0;}')
   exe=root/'check';subprocess.run([shutil.which('cc') or shutil.which('gcc'),'-std=c99','-Wall','-Werror','-Wno-unused-function',str(source),'-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True)
if __name__=='__main__':unittest.main()
