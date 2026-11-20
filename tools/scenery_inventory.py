"""Batch local asset inventory across mapped two/three-layer GBA engines.

Exports metadata only by default. Optional atlases stay in the selected local
output directory; they are source-art review inputs, not release media.
"""
import argparse,collections,hashlib,json,re,struct,zlib
from pathlib import Path
from scenery_transfer import Art


class MapArt(Art):
    def setup(self, numbers, primary, secondary):
        self.numbers=numbers;self.primary=primary;self.secondary=secondary
        split=numbers['tiles'];pals=numbers['palettes']
        def tiledata(ts,count):
            return self.read(self.word(ts+4),count*32) if not self.read(ts,1)[0]&1 else self.tiles(ts)
        self.tiledata=tiledata(primary,split).ljust(split*32,b'\0')[:split*32]+tiledata(secondary,1024-split)
        raw=self.read(self.word(primary+8),pals*32)+self.read(self.word(secondary+8)+pals*32,(16-pals)*32)
        self.palette=[tuple(((c>>shift)&31)*255//31 for shift in (0,5,10)) for c in struct.unpack('<256H',raw)]

    def layers(self,mid):
        from PIL import Image
        split=self.numbers['metatiles'];size=self.numbers['size']
        ts,local=(self.primary,mid) if mid<split else (self.secondary,mid-split)
        entries=struct.unpack('<'+'H'*(size//2),self.read(self.word(ts+12)+size*local,size))
        result=[]
        for layer in range(size//8):
            im=Image.new('RGBA',(16,16))
            for y in range(16):
                for x in range(16):
                    e=entries[layer*4+y//8*2+x//8];px=x&7;py=y&7
                    if e&1024:px=7-px
                    if e&2048:py=7-py
                    offset=(e&1023)*32+py*4+px//2
                    if offset>=len(self.tiledata):raise ValueError('Tile data truncated')
                    index=self.tiledata[offset]>>(4*(px&1))&15
                    if index:im.putpixel((x,y),(*self.palette[(e>>12)*16+index],255))
            result.append(im)
        return result

    def image(self,mid):
        from PIL import Image
        out=Image.new('RGBA',(16,16),(*self.palette[0],255))
        for layer in self.layers(mid):out.alpha_composite(layer)
        return out.convert('RGB')


def tables(path):
    result={}
    pattern=r'0x([0-9a-f]+)L to AreaMapTables\((0x[0-9a-f]+)L, (0x[0-9a-f]+)L, listOf\(([^)]*)\), (\d+), (\d+), (\d+), (-?\d+), (\d+), (0x[0-9a-f]+)'
    for m in re.finditer(pattern,path.read_text(),re.I):
        crc,groups,key,counts,tiles,mts,pals,floor,size,mask=m.groups()
        result[crc.lower()]={'groups':int(groups,16),'xor':int(key,16),'counts':[int(v) for v in counts.split(',')],
                           'tiles':int(tiles),'metatiles':int(mts),'palettes':int(pals),'size':int(size),'mask':int(mask,16)}
    return result


def inventory(art,config):
    pairs={};headers=set();failures=[]
    for group,count in enumerate(config['counts']):
        bank=art.word(config['groups']+group*4)^config['xor']
        for index in range(count):
            try:
                header=art.word(bank+index*4);layout=art.word(header)
                width=art.word(layout);height=art.word(layout+4)
                if not 1<=width<=512 or not 1<=height<=512:raise ValueError('Invalid map dimensions')
                primary=art.word(layout+16);secondary=art.word(layout+20)
                for ts in (primary,secondary):
                    art.read(ts,24)
                    for off in (4,8,12):art.read(art.word(ts+off),2)
                values=struct.unpack('<'+'H'*(width*height),art.read(art.word(layout+12),width*height*2))
                ids=[v&config['mask'] for v in values]
                pair=pairs.setdefault((primary,secondary),{'primary':hex(primary),'secondary':hex(secondary),'maps':[],
                                                          'used_metatiles':collections.Counter(),'vertical_pairs':collections.Counter()})
                pair['maps'].append({'group':group,'map':index,'header':hex(header),'layout':hex(layout),'width':width,'height':height})
                pair['used_metatiles'].update(ids)
                pair['vertical_pairs'].update((ids[y*width+x],ids[(y+1)*width+x]) for y in range(height-1) for x in range(width))
                headers.add(header)
            except (ValueError,struct.error) as error:failures.append({'group':group,'map':index,'error':str(error)})
    for p in pairs.values():
        p['used_metatiles']={hex(k):v for k,v in sorted(p['used_metatiles'].items())}
        p['vertical_pairs']={f'{a:x}/{b:x}':n for (a,b),n in sorted(p['vertical_pairs'].items())}
    return {'map_headers':len(headers),'tileset_pairs':list(pairs.values()),'failures':failures}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--games',nargs='*');parser.add_argument('--atlases',action='store_true')
    args=parser.parse_args();w=args.workspace.resolve();args.output.mkdir(parents=True,exist_ok=True)
    configs=tables(w/'pokedaisy/app/src/main/kotlin/com/pokedaisy/app/companion/data/AreaMapTablesGen.kt')
    manifest=json.loads((w/'solid-rollout/expansion/manifest.json').read_text())['games']
    games={g['key']:g for g in manifest}
    for key,crc in [('letsgo','25c3d89f'),('radical','fba55dd8'),('unbound','4b3d4957')]:games[key]={'key':key,'crc32':crc}
    proof=json.loads((w/'scenery-completion/expansion-engine-proof.json').read_text())
    for key,base in [('fakemon','dd88761c'),('better-emerald-2','1f1c08fb')]:
        g=games[key];configs[g['crc32']]=dict(configs[base]);configs[g['crc32']]['groups']=int(proof[key]['row'][2],16)
    for key in args.games or games:
        game=games[key];crc=game['crc32']
        if crc not in configs:
            print(key,'held: no validated map-bank sizes');continue
        path=w/'solid-rollout'/('expansion/'+key+'.gba' if key in {g['key'] for g in manifest} else key+'.gba')
        art=MapArt(path)
        if f'{zlib.crc32(art.data):08x}'!=crc or ('sha256' in game and hashlib.sha256(art.data).hexdigest()!=game['sha256']):raise ValueError('ROM mismatch: '+key)
        report=inventory(art,configs[crc]);report.update(game=key,crc32=crc,rom_sha256=hashlib.sha256(art.data).hexdigest(),numbers=configs[crc],qualification=False)
        folder=args.output/key;folder.mkdir(exist_ok=True)
        (folder/'inventory.json').write_text(json.dumps(report,indent=2))
        if args.atlases:
            from PIL import Image,ImageDraw
            seen=set();index=[]
            for pair in report['tileset_pairs']:
                primary=int(pair['primary'],16);secondary=int(pair['secondary'],16)
                if primary in seen:continue
                seen.add(primary);art.setup(configs[crc],primary,secondary)
                for page in range((configs[crc]['metatiles']+255)//256):
                    sheet=Image.new('RGB',(768,992),'#20242c');draw=ImageDraw.Draw(sheet)
                    for n in range(256):
                        mid=page*256+n
                        if mid>=configs[crc]['metatiles']:break
                        x=n%16*48;y=n//16*62
                        try:sheet.paste(art.image(mid).resize((48,48),Image.Resampling.NEAREST),(x,y))
                        except ValueError:draw.rectangle((x,y,x+47,y+47),outline='red')
                        draw.text((x,y+48),f'{mid:03x}',fill='white')
                    name=f'primary-{primary:08x}-{page}.png';sheet.save(folder/name)
                    index.append({'file':name,'primary':pair['primary'],'secondary':pair['secondary']})
            (folder/'atlas-index.json').write_text(json.dumps(index,indent=2))
        print(key,report['map_headers'],'maps',len(report['tileset_pairs']),'tileset pairs',len(report['failures']),'failures',flush=True)

if __name__=='__main__':main()
