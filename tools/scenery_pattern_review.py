"""Review an exact map pattern with a one-cell margin before registering its footprint."""
import argparse, hashlib, json, struct
from pathlib import Path
from PIL import Image, ImageDraw
from scenery_inputs import resolve_input
from scenery_inventory import MapArt

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--workspace',type=Path,required=True)
p.add_argument('--game',required=True)
for name in ('group','map','x','y','width','height'):p.add_argument('--'+name,type=int,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();rom,inv=resolve_input(a.workspace,a.game);art=MapArt(rom)
m=next(m for pair in inv['tileset_pairs'] for m in pair['maps'] if (m['group'],m['map'])==(a.group,a.map))
assert 1<=a.width<=4 and 1<=a.height<=4
assert a.x>0 and a.y>0 and a.x+a.width<m['width'] and a.y+a.height<m['height']
layout=int(m['layout'],16);primary=art.word(layout+16);secondary=art.word(layout+20)
art.setup(inv['numbers'],primary,secondary)
raw=art.read(art.word(layout+12),m['width']*m['height']*2)
grid=struct.unpack('<'+'H'*(m['width']*m['height']),raw)
scale=80;sheet=Image.new('RGB',((a.width+2)*scale,(a.height+2)*scale));draw=ImageDraw.Draw(sheet)
cells=[];neighbors=[]
for y in range(a.y-1,a.y+a.height+1):
    for x in range(a.x-1,a.x+a.width+1):
        mid=grid[y*m['width']+x]&inv['numbers']['mask'];im=art.image(mid).convert('RGBA')
        dx=(x-a.x+1)*scale;dy=(y-a.y+1)*scale
        sheet.paste(im.resize((scale,scale),Image.Resampling.NEAREST),(dx,dy))
        selected=a.x<=x<a.x+a.width and a.y<=y<a.y+a.height
        draw.rectangle((dx,dy,dx+scale-1,dy+scale-1),outline='red' if selected else 'white',width=2)
        draw.text((dx+3,dy+3),f'{x},{y} {mid:x}',fill='white',stroke_width=1,stroke_fill='black')
        row=dict(x=x,y=y,id=mid,rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest())
        (cells if selected else neighbors).append(row)
assert not a.output.with_suffix('.json').exists()
a.output.parent.mkdir(parents=True,exist_ok=True);sheet.save(a.output.with_suffix('.png'))
a.output.with_suffix('.json').write_text(json.dumps(dict(game=a.game,rom_sha256=inv['rom_sha256'],primary=hex(primary),secondary=hex(secondary),group=a.group,map=a.map,x=a.x,y=a.y,width=a.width,height=a.height,cells=cells,margin=neighbors,reviewed=False,thor_qualified=False),indent=2))
print(a.output.with_suffix('.png'))
