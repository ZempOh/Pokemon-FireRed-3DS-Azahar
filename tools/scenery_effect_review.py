"""Decode exact own-ROM foliage effect frames for private manual review."""
import argparse,hashlib,json,struct
from pathlib import Path
from PIL import Image,ImageDraw
from scenery_inputs import resolve_input
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--workspace',type=Path,required=True)
p.add_argument('--inventory',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();assert not a.output.exists();a.output.mkdir(parents=True)
data=json.loads(a.inventory.read_text());profiles=[]
spec={4:(5,16),10:(4,8),15:(4,16),16:(6,16),30:(2,16)}
for game,g in data.items():
 rom,_=resolve_input(a.workspace,game,g['rom_sha256']);b=rom.read_bytes()
 assert len(g['tables'])==1,'Review ambiguous effect-table candidates first'
 table,entries=next(iter(g['tables'].items()))
 sheet=Image.new('RGB',(720,240),'#20242c');draw=ImageDraw.Draw(sheet)
 for row,e in enumerate(entries):
  n,h=spec[e['index']];images=int(e['images'],16)-0x08000000;frames=[]
  for frame in range(n):
   ptr,size=struct.unpack_from('<IH',b,images+frame*8);assert size==16*h//2
   off=ptr-0x08000000;assert 0<=off<=len(b)-size
   raw=b[off:off+size];im=Image.new('RGB',(16,h),(24,28,35))
   for y in range(h):
    for x in range(16):
     at=(y//8*2+x//8)*32+(y%8)*4+x%8//2;v=(raw[at]>>(4*(x&1)))&15
     if v:im.putpixel((x,y),(50+v*12,)*3)
   sheet.paste(im.resize((64,h*2),Image.Resampling.NEAREST),(150+frame*90,row*48+12))
   frames.append(dict(pointer=hex(ptr),bytes=size,sha256=hashlib.sha256(raw).hexdigest()))
  draw.text((4,row*48+15),f"{game} {e['index']}",fill='white')
  off=int(e['template'],16)-0x08000000
  profiles.append(dict(game=game,rom_crc32=g['crc32'],rom_sha256=g['rom_sha256'],field_table=table,**e,template_sha256=hashlib.sha256(b[off:off+24]).hexdigest(),frames=frames,reviewed=False))
 sheet.save(a.output/(game+'.png'))
(a.output/'profiles.json').write_text(json.dumps(profiles,indent=2)+'\n')
print(len(profiles),'effects decoded; manual source review still required')
