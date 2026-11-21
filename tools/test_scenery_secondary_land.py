"""Secondary tile IDs must never recolor another tileset's roofs or furniture."""
import copy,json,shutil,struct,subprocess,tempfile,unittest
from pathlib import Path
from gen_scenery_registry import generate,validate_secondary_land,validate_land_masks
from scenery_material_masks import visible_palette_indices,material_rows
ROOT=Path(__file__).parent/'scenery-profiles'
CAPS=json.loads((ROOT/'android-capabilities.json').read_text())
PROOF=json.loads((ROOT/'android-secondary-land-review.json').read_text())
MASKS=json.loads((ROOT/'android-land-mask-review.json').read_text())

class SecondaryLandTests(unittest.TestCase):
 def test_provenance(self):
  validate_secondary_land(CAPS,PROOF);validate_land_masks(CAPS,MASKS)
 def test_emerald_water_edge_is_never_full_land(self):
  for game in ('modern-emerald','lazarus','seaglass'):
   cap=next(p for p in CAPS if p['game']==game)
   self.assertTrue(all(0x11c not in x['ids'] for x in cap['land']))
   cells=[c for g in cap['secondary_land_masks'] for c in g['cells'] if c['id']==0x11c]
   self.assertTrue(cells,game)
   for cell in cells:
    self.assertNotEqual(cell['rows'][0],65535)
    self.assertEqual(cell['rows'][8],65535)
 def test_mask_cannot_expand_into_structure(self):
  caps=copy.deepcopy(CAPS)
  group=next(p for p in caps if p['game']=='fakemon')['secondary_land_masks'][0]
  cell=next(x for x in group['cells'] if x['id']==0x282)
  cell['rows'][15]=65535
  with self.assertRaises(AssertionError):validate_land_masks(caps,MASKS)
 def test_source_mask_respects_overlay_transparency_and_flips(self):
  class Art:
   primary=0;secondary=24;numbers=dict(metatiles=640,size=16)
   tiledata=bytes(32)+bytes([1])+bytes(31)+bytes([2])+bytes(31)
   def word(self,_):return 0
   def read(self,_,size):return struct.pack('<8H',1,0,0,0,2|1024|2048|0x3000,0,0,0)
  indices=visible_palette_indices(Art(),0)
  self.assertEqual(indices[0],1);self.assertEqual(indices[7*16+7],50);self.assertEqual(indices[1],0)
  rows=material_rows(indices,{1})
  self.assertEqual(rows[0],1);self.assertEqual(rows[7],0)
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
    if p['game'] in ('modern-emerald','lazarus','seaglass'):
     for land in p['land']:
      checks.append(f"assert(!sceneryLand(0x{p['rom_crc32']},{land['primary']},0x11c));")
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
   for p in CAPS:
    for group in p.get('secondary_land_masks',[]):
     crc=int(p['rom_crc32'],16);primary=int(group['primary'],16);secondary=int(group['secondary'],16)
     for cell in group['cells']:
      mid=cell['id']
      for y,bits in enumerate(cell['rows']):checks.append(f'assert(scenerySecondaryLandMask({crc}u,{primary}u,{secondary}u,{mid})[{y}]=={bits});')
      checks.append(f'assert(!scenerySecondaryLandMask({crc}u,{primary}u,{secondary+4}u,{mid}));')
   checks+=['assert(scenerySecondaryLandMask(0x5e704d77,0x082d4a94,0x082d4aac,0x282)[0]==65535);',
            'assert(scenerySecondaryLandMask(0x5e704d77,0x082d4a94,0x082d4aac,0x282)[15]==0);',
            'assert(!(scenerySecondaryLandMask(0x5e704d77,0x082d4a94,0x082d4aac,0x284)[4]&(1<<4)));',
            'assert(!(scenerySecondaryLandMask(0x5e704d77,0x082d4a94,0x082d4aac,0x2a5)[15]&(1<<8)));',
            'assert(!scenerySecondaryLand(0x5e704d77,0x082d4a94,0x082d4aac,0x2b7));']
   source=root/'check.c';source.write_text('#include <assert.h>\n#include "pk_scenery_candidates.h"\nint main(void){'+''.join(checks)+'return 0;}')
   exe=root/'check';subprocess.run([shutil.which('cc') or shutil.which('gcc'),'-std=c99','-Wall','-Werror','-Wno-unused-function',str(source),'-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True)
if __name__=='__main__':unittest.main()
