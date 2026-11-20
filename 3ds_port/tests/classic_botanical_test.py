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
 def test_signature_recognition_preserves_distinct_floors_and_rejects_overlays(self):
  class Tiles:
   def subtile(self,tile,palette):
    rgb={0:(0,0,0),2:(90,60,30),3:(50,80,110),40:(40,180,60),41:(130,130,140),99:(200,0,0)}[tile]
    return [(rgb,int(tile!=0))]*64
  class Layout:
   def __init__(self,lid):
    self.id=lid;self.primary='Building';self.w=1;self.h=2;self.blocks=[0x47,0x4f];self.ts=Tiles()
   def metatile(self,x,y):return self.blocks[y]
   def entries(self,mid):
    floor=3 if self.id=='alternate' else 2
    if mid==0x47:return [0]*4+[floor]*4+[40]*4
    return [floor]*4+[41]*4+([99]*4 if self.id=='unrelated_overlay' else [0]*4)
  cb.vb.Image=Image;cb.vb.LayoutArt=Layout
  cb.vb._layouts_json=lambda:[dict(id=x,primary_tileset='Building',blockdata_filepath='fixture') for x in ('reference','alternate','unrelated_overlay')]
  specs=cb.specs()
  self.assertEqual(sum(len(s['at']) for s in specs),2)
  self.assertEqual({s['patches'][0][2].getpixel((0,0)) for s in specs},{(90,60,30,255),(50,80,110,255)})
  self.assertEqual({s['patches'][1][2].getpixel((0,0)) for s in specs},{(90,60,30,255),(50,80,110,255)})
if __name__=='__main__':unittest.main()
