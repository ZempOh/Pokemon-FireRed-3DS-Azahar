import hashlib,struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scenery_object_variants import discover

class ObjectVariantsTest(unittest.TestCase):
    def fixture(self,ambiguous=False):
        rom=bytearray(1024);base=0x08000000
        struct.pack_into('<I',rom,4,base+32);rom[32]=3;struct.pack_into('<I',rom,36,base+64)
        for i,gfx in enumerate((82,449,86)):
            t=64+i*24;rom[t]=i+1;struct.pack_into('<H',rom,t+2,gfx)
            struct.pack_into('<I',rom,t+16,base+(300 if i<2 or ambiguous else 320))
        rom[300]=rom[320]=0x6a
        inv=dict(game='synthetic',rom_sha256=hashlib.sha256(rom).hexdigest(),tileset_pairs=[dict(maps=[dict(group=1,map=6,header=hex(base))])])
        profiles=[dict(gfx=82,kind=9,reviewed=True),dict(gfx=86,kind=8,reviewed=True)]
        return bytes(rom),inv,profiles
    def test_kind_one_graphics_and_unapproved_variant(self):
        rom,inv,p=self.fixture();r=discover(rom,inv,p,1)
        self.assertEqual([(x['gfx'],x['kind'],x['reviewed']) for x in r['candidates']],[(449,9,False)])
        self.assertFalse(r['failures'])
        self.assertFalse(discover(rom,inv,p,3)['candidates'])
    def test_ambiguous_scripts_do_not_classify(self):
        self.assertFalse(discover(*self.fixture(True),1)['candidates'])
    def test_revision_mismatch_rejected(self):
        rom,inv,p=self.fixture()
        with self.assertRaises(ValueError):discover(rom+b'changed',inv,p,1)

if __name__=='__main__':unittest.main()
