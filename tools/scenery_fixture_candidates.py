"""Propose local outdoor QA scenes from reviewed profiles. Does not edit saves or certify scenes."""
import argparse,collections,hashlib,json,struct,zlib
from pathlib import Path

def propose(rom,inventory,cap,props):
 data=rom.read_bytes();assert f'{zlib.crc32(data):08x}'==cap['rom_crc32']
 def read(addr,n):
  off=addr-0x08000000
  assert 0<=off<=len(data)-n,'ROM range'
  return data[off:off+n]
 def word(addr):return struct.unpack('<I',read(addr,4))[0]
 land={int(p['primary'],16):set(p['ids']) for p in cap['land']}
 kinds={}
 for p in props:
  if p['rom_crc32']==cap['rom_crc32']:
   assert hashlib.sha256(data).hexdigest()==p['rom_sha256']
   kinds.setdefault(int(p['primary'],16),{})[p['id']]=p['kind']
 rows=[]
 for pair in inventory['tileset_pairs']:
  primary=int(pair['primary'],16)
  if primary not in land:continue
  for m in pair['maps']:
   if read(int(m['header'],16)+23,1)[0] not in (1,2,3):continue
   w,h=m['width'],m['height'];layout=int(m['layout'],16)
   cells=struct.unpack('<'+'H'*(w*h),read(word(layout+12),w*h*2));mask=inventory['numbers']['mask']
   best=None
   for y in range(2,h-2):
    for x in range(2,w-2):
     cell=cells[y*w+x]
     if cell&0xc00 or (cell&mask) not in land[primary]:continue
     near=collections.Counter(cells[yy*w+xx]&mask for yy in range(max(0,y-5),min(h,y+6)) for xx in range(max(0,x-6),min(w,x+7)))
     visible=sorted({kinds.get(primary,{}).get(mid) for mid in near if mid in kinds.get(primary,{})})
     score=len(visible)*100+sum(min(n,10) for mid,n in near.items() if mid in kinds.get(primary,{}))
     candidate=dict(score=score,x=x,y=y,visible_kinds=visible)
     if best is None or score>best['score']:best=candidate
   if best:rows.append(dict(group=m['group'],map=m['map'],primary=pair['primary'],**best))
 return dict(game=cap['game'],rom_sha256=hashlib.sha256(data).hexdigest(),scenes=sorted(rows,key=lambda x:-x['score'])[:12],qualified=False,note='Source proposals only. Verify live objects, movement, story state and rendered scene on device before use.')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--inventory',type=Path,required=True);p.add_argument('--game',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 base=Path(__file__).resolve().parent/'scenery-profiles'
 caps=json.loads((base/'android-capabilities.json').read_text());cap=next(c for c in caps if c['game']==a.game)
 report=propose(a.rom,json.loads(a.inventory.read_text()),cap,json.loads((base/'android-ground-props.json').read_text()))
 a.output.write_text(json.dumps(report,indent=2));print(a.game,len(report['scenes']),'proposals; none qualified')
if __name__=='__main__':main()
