"""Compare mapped field metatiles with a private mGBA state; never exports ROM bytes.

This diagnoses engine layout/camera mapping. It is not a Thor qualification gate.
"""
import argparse,hashlib,json,struct
from pathlib import Path


def probe(rom,state,profile,split,size):
    if hashlib.sha256(rom).hexdigest()!=profile['rom_sha256']:raise ValueError('ROM revision mismatch')
    if state[:4]!=bytes((7,0,0,1)) or len(state)<0x61000:raise ValueError('Unsupported mGBA state layout')
    def read(address,count):
        if 0x08000000<=address<0x0a000000:data,offset=rom,address-0x08000000
        elif 0x02000000<=address<0x02040000:data,offset=state,0x21000+address-0x02000000
        elif 0x03000000<=address<0x03008000:data,offset=state,0x19000+address-0x03000000
        else:raise ValueError('Unmapped address')
        value=data[offset:offset+count]
        if len(value)!=count:raise ValueError('Truncated input')
        return value
    def word(address):return struct.unpack('<I',read(address,4))[0]
    c={key:int(value,16) for key,value in profile['slots'].items()}
    io=struct.unpack_from('<512H',state,0x400);vram=state[0x1000:0x19000]
    px,py=struct.unpack('<hh',read(word(c['SAVE_BLOCK1_PTR']),4));camera=read(c['CAMERA_OFFSET'],4)
    width,height,data=struct.unpack('<III',read(c['VMAP'],12))
    if not (1<=width<=1024 and 1<=height<=1024):raise ValueError('Not a valid field map')
    cells=struct.unpack('<'+'H'*(width*height),read(data,width*height*2))
    layout=word(c['MAP_HEADER']);primary=word(layout+16);secondary=word(layout+20)
    scores=[]
    for dx,dy in ((0,0),(-1,0),(1,0),(0,-1),(0,1)):
        h,v=io[10]&511,io[11]&511
        cx=(px+dx)*16+((h-camera[2]*8+128)%256-128);cy=(py+dy)*16+((v-camera[3]*8+128)%256-128)
        hits=[0,0,0];count=0
        for sy in range(4,160,8):
            for sx in range(4,240,8):
                mx,my=cx+sx,cy+sy
                if not (0<=mx//16<width and 0<=my//16<height):continue
                mid=cells[my//16*width+mx//16]&(c['METATILE_MASK'] or 1023)
                ts,index=(primary,mid) if mid<split else (secondary,mid-split)
                entries=struct.unpack('<'+'H'*(size//2),read(word(ts+12)+index*size,size));q=(my//8&1)*2+(mx//8&1)
                if size==24:expected=(entries[8+q],entries[4+q],entries[q])
                elif size==16:
                    layer=struct.unpack('<H',read(word(ts+16)+index*2,2))[0]>>12
                    expected=(entries[4+q],entries[q],c['NORMAL_BG3']) if layer==0 else (0,entries[4+q],entries[q]) if layer==1 else (entries[4+q],0,entries[q])
                else:raise ValueError('Unsupported metatile size')
                for bg in range(1,4):
                    at=(io[4+bg]>>8&31)*0x800+2*(((v+sy)//8&31)*32+((h+sx)//8&31))
                    hits[bg-1]+=struct.unpack_from('<H',vram,at)[0]==expected[bg-1]
                count+=1
        scores.append(dict(dx=dx,dy=dy,matches=sum(hits),entries=count*3,per_bg=hits))
    best=max(scores,key=lambda s:s['matches']/max(s['entries'],1))
    return dict(game=profile['game'],rom_sha256=hashlib.sha256(rom).hexdigest(),state_sha256=hashlib.sha256(state).hexdigest(),
                primary=hex(primary),secondary=hex(secondary),metatiles=split,size=size,best=best,thor_qualified=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('rom','state','profiles','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--game',required=True);p.add_argument('--metatiles',type=int,required=True);p.add_argument('--size',type=int,choices=(16,24),required=True)
    a=p.parse_args();profile=next(r for r in json.loads(a.profiles.read_text()) if r['game']==a.game)
    report=probe(a.rom.read_bytes(),a.state.read_bytes(),profile,a.metatiles,a.size)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['best']))
