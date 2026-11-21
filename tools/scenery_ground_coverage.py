"""Find unregistered source-ground pixels across an entire map, without approval."""
import argparse,hashlib,json,struct,zlib
from pathlib import Path
from PIL import Image,ImageDraw
from scenery_inputs import resolve_input
from scenery_inventory import MapArt
from scenery_material_masks import visible_palette_indices,material_rows

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workspace',type=Path,required=True)
 p.add_argument('--game',required=True);p.add_argument('--group',type=int,required=True);p.add_argument('--map',type=int,required=True)
 p.add_argument('--reference',type=lambda x:int(x,0),required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 rom,inv=resolve_input(a.workspace,a.game)
 pair=next(p for p in inv['tileset_pairs'] if any(m['group']==a.group and m['map']==a.map for m in p['maps']))
 m=next(m for m in pair['maps'] if m['group']==a.group and m['map']==a.map)
 primary,secondary=int(pair['primary'],16),int(pair['secondary'],16);art=MapArt(rom);art.setup(inv['numbers'],primary,secondary)
 size=m['width']*m['height'];layout=int(m['layout'],16);raw=art.read(art.word(layout+12),size*2)
 used=sorted({x&inv['numbers']['mask'] for x in struct.unpack('<'+'H'*size,raw)})
 cap=next(p for p in json.loads(Path(__file__).with_name('scenery-profiles').joinpath('android-capabilities.json').read_text()) if p['game']==a.game)
 full={mid for g in cap['land'] if int(g['primary'],16)==primary for mid in g['ids']}
 full|={mid for g in cap.get('secondary_land',[]) if int(g['primary'],16)==primary and int(g['secondary'],16)==secondary for mid in g['ids']}
 existing={c['id']:c['rows'] for g in cap.get('secondary_land_masks',[]) if int(g['primary'],16)==primary and int(g['secondary'],16)==secondary for c in g['cells']}
 palette=set(visible_palette_indices(art,a.reference));assert 0 not in palette
 cells=[]
 for mid in used:
  if mid in full:continue
  rows=material_rows(visible_palette_indices(art,mid),palette);prior=existing.get(mid,[0]*16)
  if not any(bits&~old for bits,old in zip(rows,prior)):continue
  im=art.image(mid).convert('RGBA')
  cells.append(dict(id=mid,rows=rows,prior_rows=prior,rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest()))
 sheet=Image.new('RGB',(6*210,max(125,125*((len(cells)+5)//6))),'#20252d');draw=ImageDraw.Draw(sheet)
 for n,c in enumerate(cells):
  im=art.image(c['id']).convert('RGBA');preview=im.copy()
  for y in range(16):
   for x in range(16):
    if c['rows'][y]&(1<<x):preview.putpixel((x,y),(235,242,249,255))
  x=n%6*210;y=n//6*125;draw.text((x,y),hex(c['id']),fill='white')
  sheet.paste(im.resize((96,96),Image.Resampling.NEAREST),(x,y+22));sheet.paste(preview.resize((96,96),Image.Resampling.NEAREST),(x+104,y+22))
 assert not a.output.with_suffix('.json').exists(),'Preserve prior source review'
 a.output.parent.mkdir(parents=True,exist_ok=True);sheet.save(a.output.with_suffix('.png'));data=rom.read_bytes()
 report=dict(game=a.game,group=a.group,map=a.map,primary=hex(primary),secondary=hex(secondary),rom_crc32=f'{zlib.crc32(data):08x}',rom_sha256=hashlib.sha256(data).hexdigest(),map_sha256=hashlib.sha256(raw).hexdigest(),ground_reference=a.reference,palette_indices=sorted(palette),cells=cells,reviewed=False,thor_qualified=False,source_review_sha256=hashlib.sha256(a.output.with_suffix('.png').read_bytes()).hexdigest())
 a.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print('Unreviewed map-wide ground candidates:',len(cells))

if __name__=='__main__':main()
