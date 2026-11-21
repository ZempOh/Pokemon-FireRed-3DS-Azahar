import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scenery_inputs import resolve_input

class RevisionInputs(unittest.TestCase):
 def test_revision_identity_is_required_by_inventory_and_profile(self):
  with tempfile.TemporaryDirectory() as temp:
   w=Path(temp);r=w/'scenery-completion';r.mkdir()
   rom=r/'archive.gba';rom.write_bytes(b'exact local revision')
   digest=hashlib.sha256(rom.read_bytes()).hexdigest()
   inv=r/'inventory.json';inv.write_text(json.dumps({'rom_sha256':digest,'numbers':{}}))
   (r/'rom-inputs.json').write_text(json.dumps({'sample':{'rom':'scenery-completion/archive.gba','inventory':'scenery-completion/inventory.json','sha256':digest}}))
   self.assertEqual(resolve_input(w,'sample',digest)[0],rom)
   with self.assertRaisesRegex(AssertionError,'another ROM revision'):resolve_input(w,'sample','0'*64)
   rom.write_bytes(b'changed revision')
   with self.assertRaisesRegex(AssertionError,'inventory revision differ'):resolve_input(w,'sample',digest)

if __name__=='__main__':unittest.main()
