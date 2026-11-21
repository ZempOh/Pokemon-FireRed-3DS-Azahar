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
 def test_lazarus_acrisia_ground_preserves_posts_and_facade(self):
  cap=next(p for p in CAPS if p['game']=='lazarus')
  group=next(g for g in cap['secondary_land_masks'] if int(g['secondary'],16)==0x8e3e92c)
  cells={c['id']:c['rows'] for c in group['cells']}
  self.assertTrue(cells[0x248][8]&(1<<8))
  self.assertFalse(cells[0x248][8]&(1<<2))
  self.assertTrue(cells[0x249][8]&(1<<2))
  self.assertFalse(cells[0x249][8]&(1<<13))
  self.assertEqual(cells[0x216][0],0) # Overhanging facade trim.
  self.assertEqual(cells[0x216][15],65535)
  self.assertTrue(any(0x26c in g['ids'] for g in cap['secondary_land']))
  self.assertNotIn(0x240,cells);self.assertNotIn(0x241,cells)
 def test_odyssey_paving_excludes_adjacent_walls_and_stairs(self):
  cap=next(p for p in CAPS if p['game']=='odyssey')
  ids=set(next(g for g in cap['land'] if int(g['primary'],16)==0x82d4a94)['ids'])
  self.assertTrue({0x162,0x163,0x164,0x16a,0x16b,0x16c,0x172,0x173,0x174}<=ids)
  self.assertFalse(ids&{0x161,0x165,0x169,0x16d,0x171,0x175})
 def test_letsgo_diagonal_ground_excludes_adjacent_water_and_rock(self):
  cap=next(p for p in CAPS if p['game']=='letsgo')
  ids=set(next(g for g in cap['land'] if int(g['primary'],16)==0x82d4a94)['ids'])
  self.assertTrue({0x1d5,0x1d6,0x1d7,0x1dc,0x1dd,0x1de,0x1df}<=ids)
  self.assertFalse(ids&{0x1d0,0x1d1,0x1d2,0x1d3,0x1d4,0x1d8,0x1d9,0x1da,0x1db})
 def test_lazarus_footprints_preserve_lamp_and_sign(self):
  cap=next(p for p in CAPS if p['game']=='lazarus')
  cells={c['id']:c['rows'] for g in cap['secondary_land_masks'] if int(g['secondary'],16)==0x8e3e92c for c in g['cells']}
  self.assertTrue(cells[0x1b][0]&1)
  self.assertFalse(cells[0x1b][8]&(1<<8))
  self.assertTrue(cells[0x66][15]&1)
  self.assertFalse(cells[0x66][8]&(1<<8))
 def test_better_plaza_preserves_lamps_fountain_water_and_sign(self):
  cap=next(p for p in CAPS if p['game']=='better-emerald-2')
  land=next(g for g in cap['secondary_land'] if int(g['secondary'],16)==0x83df734)
  self.assertTrue({0x2bb,0x2e0,0x2e1,0x2e2,0x2e8,0x2ea,0x2f0,0x2f1,0x2f2}<=set(land['ids']))
  group=next(g for g in cap['secondary_land_masks'] if int(g['secondary'],16)==0x83df734)
  cells={c['id']:c['rows'] for c in group['cells']}
  self.assertTrue(cells[0x212][0]&1) # Ground left of the lamp.
  self.assertFalse(cells[0x212][8]&(1<<8)) # Lamp remains visible.
  self.assertTrue(cells[0x338][0]&1) # Ground outside fountain corner.
  self.assertFalse(cells[0x338][15]&(1<<15)) # Fountain basin stays water/stone.
  for mid in (0x2e9,0x341):
   self.assertNotIn(mid,land['ids']);self.assertNotIn(mid,cells)
 def test_better_town_path_covers_every_edge_without_decorative_walls(self):
  cap=next(p for p in CAPS if p['game']=='better-emerald-2')
  land=next(g for g in cap['secondary_land'] if int(g['secondary'],16)==0x83df734)
  ids=set(land['ids'])
  self.assertTrue({0x2f8+x+y*8 for x in range(3) for y in range(3)}<=ids)
  self.assertFalse(ids&{0x2fb,0x2fc,0x303,0x304,0x305,0x30b,0x30c}) # Pillars/walls beside the path atlas.
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
 def test_unbound_dresco_ground_preserves_plants_and_roofs(self):
  cap=next(p for p in CAPS if p['game']=='unbound')
  group=next(g for g in cap['secondary_land_masks'] if int(g['secondary'],16)==0x82d4af4)
  cells={c['id']:c['rows'] for c in group['cells']}
  self.assertTrue(cells[0x2f8][15]&1) # ground beside the plant base
  self.assertFalse(cells[0x2f8][8]&(1<<8)) # plant body
  self.assertTrue(cells[0x2d1][0]&1) # grass above the roof slope
  self.assertFalse(cells[0x2d1][15]&(1<<8)) # roof itself
  self.assertFalse(cells[3][8]&(1<<8)) # wooden sign
  self.assertNotIn(0x348,cells) # ambiguous material is not guessed
  land=next(g for g in cap['secondary_land'] if int(g['secondary'],16)==0x82d4af4)
  self.assertEqual(set(land['ids']),{0x298,0x29f,0x2ca,0x303,0x304,0x305})
  self.assertEqual(cells[0x133][3],65535) # duplicate grass palette31 below cliff
  self.assertEqual(cells[0x133][0],0) # cliff face remains stone
  self.assertTrue(cells[0x342][0]&1) # paving behind the statue wing
  self.assertFalse(cells[0x342][15]&(1<<15)) # statue body stays unchanged
  self.assertTrue(any(8 in g['ids'] for g in cap['land'])) # conifer's replacement ground
 def test_emerald_hedge_ground_preserves_hedge_surface(self):
  cap=next(p for p in CAPS if p['game']=='modern-emerald')
  group=next(g for g in cap['secondary_land_masks'] if int(g['secondary'],16)==0x8bb3ae0)
  cells={c['id']:c['rows'] for c in group['cells']}
  for mid in (0x23c,0x23d,0x23e):
   self.assertEqual(cells[mid][0],65535) # exposed grass above the hedge
   self.assertFalse(cells[mid][15]&(1<<8)) # hedge itself keeps its artwork
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
 def test_tree_edge_mask_preserves_canopy(self):
  cap=next(p for p in CAPS if p['game']=='fakemon')
  cell=next(c for g in cap['secondary_land_masks'] if int(g['secondary'],16)==0x82d4aac for c in g['cells'] if c['id']==0xe)
  self.assertTrue(cell['rows'][0]&1)
  self.assertFalse(cell['rows'][15]&(1<<15))
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
   checks+=['assert(sceneryLand(0x5e704d77,0x082d4a94,8));',
            'assert(sceneryLand(0x5e704d77,0x082d4a94,9));',
            'assert(!sceneryLand(0x5e704d77,0x082d4a94,3));',
            'assert(!(scenerySecondaryLandMask(0x5e704d77,0x082d4a94,0x082d4aac,3)[5]&(1<<8)));',
            'assert(scenerySecondaryLandMask(0x5e704d77,0x082d4a94,0x082d4aac,3)[15]&1);']
   source=root/'check.c';source.write_text('#include <assert.h>\n#include "pk_scenery_candidates.h"\nint main(void){'+''.join(checks)+'return 0;}')
   exe=root/'check';subprocess.run([shutil.which('cc') or shutil.which('gcc'),'-std=c99','-Wall','-Werror','-Wno-unused-function',str(source),'-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True)
if __name__=='__main__':unittest.main()
