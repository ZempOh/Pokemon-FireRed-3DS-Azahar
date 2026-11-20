import unittest
from scenery_battle_observation import progress
ON='telemetry connected=true party=1 inBattle=true\n'
OFF='telemetry connected=true party=1 inBattle=false\n'
FIELD='scenery crc=25c3d89f rendered=120/300 blocked=0 scene=0\n'
TEXT='scenery crc=25c3d89f rendered=0/300 blocked=1 scene=1\n'
class BattleReturn(unittest.TestCase):
 def test_reset_then_continue_cannot_qualify(self):
  self.assertEqual(progress(ON+'telemetry connected=true party=0 inBattle=false\n'+OFF+FIELD+FIELD),(True,False))
 def test_end_flag_and_dialogue_are_not_field(self):
  self.assertEqual(progress(ON+OFF+TEXT),(True,False))
 def test_earlier_field_cannot_qualify_return(self):
  self.assertEqual(progress(FIELD+ON+OFF),(True,False))
 def test_later_rendered_field_qualifies(self):
  self.assertEqual(progress(ON+OFF+FIELD+OFF+FIELD),(True,True))
 def test_transient_field_before_story_dialogue_does_not_qualify(self):
  self.assertEqual(progress(ON+OFF+FIELD+TEXT),(True,False))
  self.assertEqual(progress(ON+OFF+FIELD+FIELD+TEXT),(True,False))
 def test_one_field_sample_is_not_settled(self):
  self.assertEqual(progress(ON+OFF+FIELD),(True,False))
 def test_new_battle_requires_its_own_return(self):
  self.assertEqual(progress(ON+OFF+FIELD+ON+OFF),(True,False))
if __name__=='__main__':unittest.main()
