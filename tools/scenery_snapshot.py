"""Inspect a local PokéDaisy v5 companion snapshot without launching a game."""
import argparse,json,struct
from pathlib import Path

def location_header(data):
    pos=0
    def take(n):
        nonlocal pos
        if pos+n>len(data):raise ValueError('Truncated companion snapshot')
        value=data[pos:pos+n];pos+=n;return value
    def integer():return struct.unpack('>i',take(4))[0]
    def utf():
        n=struct.unpack('>H',take(2))[0]
        return take(n).replace(b'\xc0\x80',b'\0').decode('utf-8')
    if take(4)!=b'PDSC' or integer()!=5:raise ValueError('Expected PDSC version5')
    engine=utf();utf();take(10);facing=utf()
    x,y,group,num,section,width,height,kind=[integer() for _ in range(8)]
    integer();take(9);name=utf();has_region=take(1)[0]
    if has_region not in (0,1):raise ValueError('Invalid nullable region flag')
    if has_region:utf()
    take(16);party=integer()
    if not 0<=party<=6 or width<=0 or height<=0:raise ValueError('Invalid party/map dimensions')
    return dict(engine=engine,x=x,y=y,group=group,map=num,width=width,height=height,type=kind,facing=facing,location=name,party_count=party)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('snapshot',type=Path);a=p.parse_args()
    print(json.dumps(location_header(a.snapshot.read_bytes()),indent=2,ensure_ascii=False))
