"""Propose missing source-material coverage; never approve pixels automatically.

Atlas and report contain private ROM-derived data. Keep them out of releases.
"""
import argparse, hashlib, json, struct
from pathlib import Path
from PIL import Image, ImageDraw
from scenery_inputs import resolve_input
from scenery_inventory import MapArt
from scenery_material_masks import visible_palette_indices, material_rows

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--workspace',type=Path,required=True)
p.add_argument('--game',required=True)
p.add_argument('--group',type=int,required=True)
p.add_argument('--map',type=int,required=True)
p.add_argument('--ground-refs',nargs='+',type=lambda s:int(s,0),required=True)
p.add_argument('--report',type=Path,required=True)
a=p.parse_args()
rom,inv=resolve_input(a.workspace,a.game)
pair=next(p for p in inv['tileset_pairs'] if any(m['group']==a.group and m['map']==a.map for m in p['maps']))
m=next(m for m in pair['maps'] if m['group']==a.group and m['map']==a.map)
art=MapArt(rom);primary=int(pair['primary'],16);secondary=int(pair['secondary'],16)
art.setup(inv['numbers'],primary,secondary)
raw=art.read(art.word(int(m['layout'],16)+12),m['width']*m['height']*2)
ids=sorted(set(x&inv['numbers']['mask'] for x in struct.unpack('<'+'H'*(len(raw)//2),raw)))
palette=set(v for mid in a.ground_refs for v in visible_palette_indices(art,mid))-{0}
cap=next(c for c in json.loads((Path(__file__).parent/'scenery-profiles/android-capabilities.json').read_text()) if c['game']==a.game)
full=set();masks={}
for key in ('land','secondary_land'):
 for group in cap.get(key,[]):
  if int(group['primary'],16)==primary and (key=='land' or int(group['secondary'],16)==secondary):full.update(group['ids'])
for group in cap.get('secondary_land_masks',[]):
 if int(group['primary'],16)==primary and int(group['secondary'],16)==secondary:
  for cell in group['cells']:masks[cell['id']]=cell['rows']
rows=[]
for mid in ids:
 proposed=material_rows(visible_palette_indices(art,mid),palette)
 existing=[65535]*16 if mid in full else masks.get(mid,[0]*16)
 missing=[v&~old for v,old in zip(proposed,existing)]
 if not any(missing):continue
 im=art.image(mid).convert('RGBA')
 rows.append(dict(id=mid,rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),rows=proposed,existing_rows=existing,missing_rows=missing))
sheet=Image.new('RGB',(1024,max(1,(len(rows)+3)//4)*152),'#20252d');draw=ImageDraw.Draw(sheet)
for i,row in enumerate(rows):
 x=i%4*256;y=i//4*152;im=art.image(row['id']).convert('RGB');overlay=im.copy()
 for py in range(16):
  for px in range(16):
   if row['missing_rows'][py]&(1<<px):overlay.putpixel((px,py),(255,0,255))
 draw.text((x,y),hex(row['id'])+' source / MISSING',fill='white')
 sheet.paste(im.resize((112,112),Image.Resampling.NEAREST),(x,y+24))
 sheet.paste(overlay.resize((112,112),Image.Resampling.NEAREST),(x+120,y+24))
a.report.parent.mkdir(parents=True,exist_ok=True);sheet.save(a.report.with_suffix('.png'))
a.report.write_text(json.dumps(dict(game=a.game,rom_sha256=inv['rom_sha256'],primary=pair['primary'],secondary=pair['secondary'],map=m,map_sha256=hashlib.sha256(raw).hexdigest(),ground_references=a.ground_refs,palette_indices=sorted(palette),cells=rows,reviewed=False,thor_qualified=False),indent=2))
print(len(rows),'candidate cells need source review; palette collisions are not automatic terrain classifications')
