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
if __name__=='__main__':unittest.main()
