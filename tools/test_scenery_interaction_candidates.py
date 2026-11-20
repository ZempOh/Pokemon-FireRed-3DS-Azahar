"""Reject unusable script targets without hiding coverage gaps."""
import hashlib,struct,unittest
from scenery_interaction_candidates import propose

class CandidateTests(unittest.TestCase):
    def fixture(self,script):
        rom=bytearray(2048)
        struct.pack_into('<I',rom,0x204,0x08000300)
        rom[0x300]=1
        struct.pack_into('<I',rom,0x304,0x08000400)
        rom[0x400]=1;rom[0x401]=97
        struct.pack_into('<I',rom,0x410,script)
        struct.pack_into('<I',rom,0x50c,0x08000600)
        rom[0x700]=0x6a
        inv=dict(game='fixture',rom_sha256=hashlib.sha256(rom).hexdigest(),tileset_pairs=[dict(maps=[dict(group=1,map=2,header='0x08000200',layout='0x08000500',width=2,height=2)])])
        profiles=[dict(gfx=97,kind=7,asset='rock',reviewed=True)]
        return rom,inv,profiles

    def test_invalid_targets_are_explicitly_excluded(self):
        for ptr,reason in [(0,'no_script'),(0x08000000,'cartridge_header_not_script'),(0x080000a0,'cartridge_header_not_script'),(0x09000000,'script_outside_rom')]:
            with self.subTest(pointer=ptr):
                result=propose(*self.fixture(ptr),2)
                self.assertEqual(result['candidates'],[])
                self.assertEqual(result['excluded'][0]['reason'],reason)
                self.assertFalse(result['qualification'])

    def test_valid_pointer_remains_only_a_proposal(self):
        result=propose(*self.fixture(0x08000700),2)
        self.assertEqual(len(result['candidates']),1)
        self.assertFalse(result['candidates'][0]['qualified'])
        self.assertEqual(result['excluded'],[])

    def test_immediate_end(self):
        rom,inv,profiles=self.fixture(0x08000700);rom[0x700]=2
        inv['rom_sha256']=hashlib.sha256(rom).hexdigest()
        self.assertEqual(propose(rom,inv,profiles,2)['excluded'][0]['reason'],'immediate_end_no_interaction')

if __name__=='__main__':unittest.main()
