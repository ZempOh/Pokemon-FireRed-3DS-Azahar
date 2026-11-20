"""Synthetic closed-mesh/material regression; no game data required."""
from pathlib import Path
import sys,types,json,unittest
from PIL import Image
sys.modules['voxel_building']=types.SimpleNamespace()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import classic_botanical as cb
class Mesh:
 def __init__(self):self.tris=[]
 def poly(self,p,shade,tag):self.tris.append((p,shade,tag))
class Tests(unittest.TestCase):
 def test_closed_volume_and_gray_pot(self):
  art=Image.new('RGBA',(16,32))
  for y in range(32):
   for x in range(2,14):art.putpixel((x,y),(40,180,60,255) if y<24 else (130,130,140,255))
  art.putpixel((8,25),(220,190,30,255))
  tri=json.loads(Path(cb.__file__).with_name('scenery_plant_mesh.json').read_text())
  plant=cb.BotanicalPlant(art,tri);mesh=Mesh();plant.emit(mesh)
  self.assertEqual(plant.inks[3][2],(130,130,140,255))
  self.assertTrue(cb.verify(types.SimpleNamespace(mesh=mesh,art=art)))
  mesh.tris.pop()
  with self.assertRaises(AssertionError):cb.verify(types.SimpleNamespace(mesh=mesh,art=art))
if __name__=='__main__':unittest.main()
