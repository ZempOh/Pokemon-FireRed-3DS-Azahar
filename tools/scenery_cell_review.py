"""Prepare private exact-source cell reviews; output never implies approval."""
import argparse,hashlib,json,zlib
from pathlib import Path
from PIL import Image,ImageDraw
from scenery_inputs import resolve_input
from scenery_inventory import MapArt
from scenery_material_masks import visible_palette_indices,material_rows

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--workspace',type=Path,required=True);p.add_argument('--game',required=True)
 p.add_argument('--primary',type=lambda x:int(x,0),required=True);p.add_argument('--secondary',type=lambda x:int(x,0),required=True)
 p.add_argument('--ids',type=lambda x:int(x,0),nargs='+',required=True)
 p.add_argument('--ground-reference',type=lambda x:int(x,0));p.add_argument('--output',type=Path,required=True)
 a=p.parse_args();rom,inv=resolve_input(a.workspace,a.game);art=MapArt(rom);art.setup(inv['numbers'],a.primary,a.secondary)
 assert len(a.ids)==len(set(a.ids)) and all(0<=x<=inv['numbers']['mask'] for x in a.ids)
 palette=set(visible_palette_indices(art,a.ground_reference)) if a.ground_reference is not None else set()
 assert not palette or 0 not in palette
 width=210 if palette else 106;sheet=Image.new('RGB',(width*6,125*((len(a.ids)+5)//6)),'#20252d');draw=ImageDraw.Draw(sheet);cells=[]
 for n,mid in enumerate(a.ids):
  im=art.image(mid).convert('RGBA');indices=visible_palette_indices(art,mid);x=n%6*width;y=n//6*125
  draw.text((x,y),hex(mid),fill='white');sheet.paste(im.resize((96,96),Image.Resampling.NEAREST),(x,y+22))
  cell=dict(id=mid,rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),palette_indices=sorted(set(indices)))
  if palette:
   rows=material_rows(indices,palette);preview=im.copy();cell['rows']=rows
   for py in range(16):
    for px in range(16):
     if rows[py]&(1<<px):preview.putpixel((px,py),(235,242,249,255))
   sheet.paste(preview.resize((96,96),Image.Resampling.NEAREST),(x+104,y+22))
  cells.append(cell)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 assert not a.output.with_suffix('.json').exists(),'Preserve previous reviews; choose a new output name'
 sheet.save(a.output.with_suffix('.png'));data=rom.read_bytes()
 report=dict(game=a.game,rom_crc32=f'{zlib.crc32(data):08x}',rom_sha256=hashlib.sha256(data).hexdigest(),primary=hex(a.primary),secondary=hex(a.secondary),cells=cells,reviewed=False,thor_qualified=False,source_review_sha256=hashlib.sha256(a.output.with_suffix('.png').read_bytes()).hexdigest())
 if palette:report.update(ground_reference=a.ground_reference,palette_indices=sorted(palette))
 a.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(a.output.with_suffix('.png'))

if __name__=='__main__':main()
