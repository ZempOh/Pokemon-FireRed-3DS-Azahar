import copy,json,unittest
from pathlib import Path
from scenery_buildings import validate
ROWS=json.loads((Path(__file__).parent/'scenery-profiles/android-buildings.json').read_text())
class BuildingsTest(unittest.TestCase):
 def test_reviewed_profiles(self):validate(ROWS)
 def test_incomplete_or_unreviewed_pattern_rejected(self):
  for change in ('cells','reviewed'):
   rows=copy.deepcopy(ROWS)
   if change=='cells':rows[0]['cells'].pop()
   else:rows[0]['reviewed']=False
   with self.assertRaises(AssertionError):validate(rows)
 def test_impossible_roof_rejected(self):
  rows=copy.deepcopy(ROWS);rows[0]['shape']['ridge_height']=0
  with self.assertRaises(AssertionError):validate(rows)
 def test_duplicate_identity_rejected(self):
  with self.assertRaises(AssertionError):validate(ROWS+copy.deepcopy(ROWS))
 def test_wall_crops_cannot_leave_source_or_erase_facade(self):
  for key,value in [('wall_left',-1),('wall_right',999),('wall_bottom',999),('wall_bottom',0),('wall_left',79)]:
   rows=copy.deepcopy(ROWS);rows[0]['shape'][key]=value
   with self.assertRaises(AssertionError):validate(rows)
 def test_gable_and_flat_roofs_reject_invalid_shapes(self):
  for key,value in [('gable_x',0),('gable_row',999),('ridge_back_height',0),('ridge_back_height',float('nan'))]:
   rows=copy.deepcopy(ROWS);row=next(r for r in rows if r['shape'].get('roof_kind')==2)
   row['shape'][key]=value
   with self.assertRaises(AssertionError):validate(rows)
  rows=copy.deepcopy(ROWS);row=next(r for r in rows if r['shape'].get('flat_roof') or r['shape'].get('roof_kind')==1)
  row['shape']['ridge_height']+=1
  with self.assertRaises(AssertionError):validate(rows)
 def test_roof_crop_requires_review_and_valid_bounds(self):
  for key,value in [('roof_left',-1),('roof_right',999),('roof_right',1)]:
   rows=copy.deepcopy(ROWS);row=next(r for r in rows if r.get('roof_crop_review'))
   row['shape'][key]=value
   with self.assertRaises(AssertionError):validate(rows)
  rows=copy.deepcopy(ROWS);row=next(r for r in rows if r.get('roof_crop_review'))
  row['roof_crop_review']['source_art_sha256']='0'*64
  with self.assertRaises(AssertionError):validate(rows)
if __name__=='__main__':unittest.main()
