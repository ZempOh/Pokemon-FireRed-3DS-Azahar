"""Find scenery graphics variants through shared map-object interaction scripts.

Only metadata is exported. Matches are review candidates, never auto-approved.
"""
import argparse,collections,hashlib,json,struct
from pathlib import Path
from scenery_interaction_candidates import script_rejection

def discover(rom,inventory,profiles,kind,banked=False):
    if hashlib.sha256(rom).hexdigest()!=inventory['rom_sha256']:raise ValueError('ROM revision differs from inventory')
    def read(address,size):
        offset=address-0x08000000
        if offset<0 or offset+size>len(rom):raise ValueError('ROM pointer outside input')
        return rom[offset:offset+size]
    def word(address):return struct.unpack('<I',read(address,4))[0]
    seeds={p['gfx']:p['kind'] for p in profiles if p['reviewed'] and p['kind'] in (7,8,9)}
    scripts=collections.defaultdict(list);failures=[]
    for pair in inventory['tileset_pairs']:
        for m in pair['maps']:
            try:
                events=word(int(m['header'],16)+4)
                if not events:continue
                count=read(events,1)[0]
                if count>64:raise ValueError('Invalid object count')
                if not count:continue
                ptr=word(events+4)
                for i in range(count):
                    t=read(ptr+i*24,24)
                    if t[kind]!=0:continue
                    gfx=struct.unpack_from('<H',t,2)[0] if kind==1 else t[1]|((t[2] if kind==3 else t[3] if banked else 0)<<8)
                    script=struct.unpack_from('<I',t,16)[0]
                    if script_rejection(rom,script):continue
                    scripts[script].append(dict(group=m['group'],map=m['map'],gfx=gfx,local_id=t[0]))
            except ValueError as e:failures.append(dict(group=m['group'],map=m['map'],error=str(e)))
    candidates=[]
    for script,objects in scripts.items():
        kinds={seeds[o['gfx']] for o in objects if o['gfx'] in seeds}
        if len(kinds)!=1:continue
        counts=collections.Counter(o['gfx'] for o in objects)
        for gfx,count in counts.items():
            if gfx in seeds:continue
            candidates.append(dict(gfx=gfx,kind=next(iter(kinds)),instances=count,script=hex(script),known_seeds=sorted(set(counts)&set(seeds)),example=next(o for o in objects if o['gfx']==gfx),reviewed=False))
    return dict(game=inventory['game'],rom_sha256=inventory['rom_sha256'],template_kind=kind,candidates=candidates,failures=failures)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('rom','inventory','profiles','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--template-kind',type=int,choices=(1,2,3),required=True);p.add_argument('--banked',action='store_true')
    a=p.parse_args();inv=json.loads(a.inventory.read_text());profiles=[v for v in json.loads(a.profiles.read_text()) if v['game']==inv['game']]
    result=discover(a.rom.read_bytes(),inv,profiles,a.template_kind,a.banked)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['game'],len(result['candidates']),'review candidates;',len(result['failures']),'unreadable maps')
