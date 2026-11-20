"""Classic's reviewed indoor plant family, using the shared closed botanical mesh.

Recognition requires exact source subtile signatures and primary tileset. Ground is
reconstructed from each cell's actual lower layers, not a guessed floor color.
"""
from pathlib import Path
from collections import Counter
import json, math
import voxel_building as vb

class BotanicalPlant:
    def __init__(self, art, triangles):
        self.art,self.triangles=art,triangles
        pixels=[(x,y,art.getpixel((x,y))) for y in range(32) for x in range(16) if art.getpixel((x,y))[3]]
        green=[p for p in pixels if p[2][1]>p[2][0]*1.12 and p[2][1]>p[2][2]*1.12]
        pot=[p for p in pixels if p[1]>=24 and max(p[2][:3])>65 and p not in green]
        if not green or not pot:raise ValueError('Unreviewed plant palette')
        counts=Counter(p[2][:3] for p in pot)
        leaf=max(green,key=lambda p:p[2][1]-(p[2][0]+p[2][2])/2)
        light=max(green,key=lambda p:sum(p[2][:3]))
        stem=min(green,key=lambda p:sum(p[2][:3]))
        body=max(pot,key=lambda p:(counts[p[2][:3]],sum(p[2][:3])))
        rim=min(pot,key=lambda p:abs(sum(p[2][:3])/3-130))
        soil=min(pot,key=lambda p:sum(p[2][:3]))
        self.inks=[leaf,light,stem,body,rim,soil]

    def emit(self,mesh):
        for tri in self.triangles:
            pts=[]
            for x,y,z,ink,shade in tri:
                u,v,_=self.inks[ink]
                pts.append((8+x*15,y*29,30+z*15,u+.5,v+.5))
            mesh.poly(pts,tri[0][4]/255.,'botanical_palette~clamp')

def specs():
    reference=vb.LayoutArt('LAYOUT_PALLET_TOWN_PLAYERS_HOUSE_1F')
    triangles=json.loads((Path(__file__).with_name('scenery_plant_mesh.json')).read_text(encoding='utf-8'))
    signatures=(reference.entries(0x47)[8:12],reference.entries(0x4f)[4:8])
    groups={}
    for entry in vb._layouts_json():
        if entry.get('primary_tileset')!=reference.primary or 'blockdata_filepath' not in entry:continue
        layout=vb.LayoutArt(entry['id']);matches={}
        for mid in set(v&1023 for v in layout.blocks):
            words=layout.entries(mid)
            for layer in (1,2):
                for part,signature in enumerate(signatures):
                    if words[layer*4:layer*4+4]==signature:
                        # A distinct upper overlay is not part of this family.
                        if any(e&1023 for e in words[(layer+1)*4:]):continue
                        matches[mid]=(part,layer)
        for y in range(layout.h-1):
            for x in range(layout.w):
                mids=(layout.metatile(x,y),layout.metatile(x,y+1))
                if any(m not in matches or matches[m][0]!=j for j,m in enumerate(mids)):continue
                art=vb.Image.new('RGBA',(16,32));patches=[]
                for j,mid in enumerate(mids):
                    words=layout.entries(mid);layer=matches[mid][1]
                    floor=vb.Image.new('RGBA',(16,16))
                    for source_layer in range(3):
                        for q,e in enumerate(words[source_layer*4:source_layer*4+4]):
                            data=layout.ts.subtile(e&1023,e>>12)
                            for py in range(8):
                                for px in range(8):
                                    k=(7-py if e&0x800 else py)*8+(7-px if e&0x400 else px)
                                    rgb,index=data[k];u=(q&1)*8+px;v=(q>>1)*8+py
                                    if source_layer==layer:
                                        if index:art.putpixel((u,j*16+v),rgb+(255,))
                                    elif source_layer==0 or index:floor.putpixel((u,v),rgb+(255,))
                    patches.append((0,j,floor))
                key=(art.tobytes(),*(p[2].tobytes() for p in patches))
                if key not in groups:
                    plant=BotanicalPlant(art,triangles)
                    groups[key]=dict(name=f'classic_botanical_{len(groups):03d}',layout=layout.id,rect=(x,y,1,2),ground=[1],art=art,
                        parts=lambda p=plant:[p],at=[],patches=patches,quads={(0,0):15,(0,1):15},botanical=True,exact=[])
                groups[key]['at'].append((layout.id,x,y))
    return list(groups.values())

def verify(model):
    """A redesigned volume is verified as geometry, not pixel-identical art."""
    edges=Counter();volume=0
    assert len(model.mesh.tris)==144
    for tri,shade,tag in model.mesh.tris:
        pts=[tuple(round(v,5) for v in p[:3]) for p in tri]
        for p in tri:
            assert all(math.isfinite(v) for v in p)
            assert model.art.getpixel((int(p[3]),int(p[4])))[3]==255
            assert 0<=p[0]<=16 and 0<=p[1]<=31 and 22<=p[2]<=38
        a,b,c=pts
        for p,q in ((a,b),(b,c),(c,a)):edges[tuple(sorted((p,q)))]+=1
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    assert all(n==2 for n in edges.values()) and volume>0
    return True
