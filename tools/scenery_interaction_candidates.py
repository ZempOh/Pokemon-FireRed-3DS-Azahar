"""Propose local HM scenery fixtures from reviewed live-object graphics."""
import argparse,hashlib,json,struct
from pathlib import Path

def propose(rom,inventory,profiles,template_kind,banked=False):
    if hashlib.sha256(rom).hexdigest()!=inventory['rom_sha256']:raise ValueError('ROM revision mismatch')
    def read(address,size):
        off=address-0x08000000
        if not 0<=off<=len(rom)-size:raise ValueError('Invalid ROM range')
        return rom[off:off+size]
    def word(address):return struct.unpack('<I',read(address,4))[0]
    seeds={p['gfx']:p for p in profiles if p['reviewed'] and p['kind'] in (7,8,9)}
    result=[];failures=[]
    for pair in inventory['tileset_pairs']:
        for m in pair['maps']:
            try:
                events=word(int(m['header'],16)+4)
                if not events:continue
                count=read(events,1)[0]
                if count>64:raise ValueError('Invalid object count')
                ptr=word(events+4);objects=[]
                for i in range(count):
                    t=read(ptr+i*24,24)
                    if t[template_kind]!=0:continue
                    gfx=struct.unpack_from('<H',t,2)[0] if template_kind==1 else t[1]|((t[2] if template_kind==3 else t[3] if banked else 0)<<8)
                    x,y=struct.unpack_from('<hh',t,4);script=struct.unpack_from('<I',t,16)[0]
                    objects.append(dict(gfx=gfx,x=x,y=y,script=script,local_id=t[0],flag=struct.unpack_from('<H',t,20)[0]))
                width,height=m['width'],m['height'];cells=struct.unpack('<'+'H'*(width*height),read(word(int(m['layout'],16)+12),width*height*2));occupied={(o['x'],o['y']) for o in objects}
                for o in objects:
                    if o['gfx'] not in seeds or not o['script']:continue
                    x,y=o['x'],o['y']+1
                    if not (0<=x<width and 0<=y<height) or (x,y) in occupied or cells[y*width+x]&0xc00:continue
                    profile=seeds[o['gfx']]
                    result.append(dict(group=m['group'],map=m['map'],x=x,y=y,facing='north',target=o,kind=profile['kind'],asset=profile['asset'],same_kind_count=sum(v['gfx'] in seeds and seeds[v['gfx']]['kind']==profile['kind'] for v in objects),qualified=False))
            except (ValueError,struct.error) as error:failures.append(dict(group=m['group'],map=m['map'],error=str(error)))
    return dict(game=inventory['game'],rom_sha256=inventory['rom_sha256'],candidates=result,failures=failures,qualification=False,note='Source proposals only. Verify flags, eligible party/HM/badge prerequisites, actual script behavior, target movement/removal and neighbor preservation on device.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('rom','inventory','profiles','output'):p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--template-kind',type=int,choices=(1,2,3),required=True);p.add_argument('--banked',action='store_true');a=p.parse_args()
    inv=json.loads(a.inventory.read_text());profiles=[x for x in json.loads(a.profiles.read_text()) if x['game']==inv['game']]
    result=propose(a.rom.read_bytes(),inv,profiles,a.template_kind,a.banked);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(inv['game'],len(result['candidates']),'proposals;',len(result['failures']),'unreadable maps; no passes asserted')
