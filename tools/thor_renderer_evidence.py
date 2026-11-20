"""Validate logged renderer activity independently of visual approval."""
import re
PATTERN=re.compile(r'scenery crc=([0-9a-f]+) rendered=(\d+)/(\d+) blocked=([0-9a-f]+) scene=(-?\d+) score=(-?\d+) view=(\d+)x(\d+) enabled=(\d+) known=(\d+)')
def summarize(text, crc):
 rows=[m.groups() for m in PATTERN.finditer(text)]
 expected=[r for r in rows if r[0].lower()==crc.lower()]
 return dict(windows=len(expected),rendered=sum(int(r[1]) for r in expected),frames=sum(int(r[2]) for r in expected),blocked_masks=sorted(set(int(r[3],16) for r in expected)),foreign_crcs=sorted(set(r[0] for r in rows if r[0].lower()!=crc.lower())),enabled=bool(expected) and all(r[8]=='1' for r in expected),known=bool(expected) and all(r[9]=='1' for r in expected))
def require_field(report):
 assert report['windows']>=6 and report['frames']>0,('Missing renderer evidence',report)
 assert report['rendered']>0 and report['enabled'] and report['known'] and not report['foreign_crcs'],('No verified 3D field draw',report)
 return report
if __name__=='__main__':
 import unittest
 class Tests(unittest.TestCase):
  def test_active(self):
   line='scenery crc=1234 rendered=300/300 blocked=0 scene=1 score=5 view=480x320 enabled=1 known=1\n'
   self.assertEqual(require_field(summarize(line*6,'1234'))['rendered'],1800)
  def test_fallback_rejected(self):
   line='scenery crc=1234 rendered=0/300 blocked=100 scene=1 score=5 view=480x320 enabled=1 known=1\n'
   with self.assertRaises(AssertionError):require_field(summarize(line*6,'1234'))
  def test_missing_rejected(self):
   with self.assertRaises(AssertionError):require_field(summarize('','1234'))
 unittest.main()
