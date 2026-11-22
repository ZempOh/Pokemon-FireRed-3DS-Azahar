"""Find structurally complete field-effect tables; keep art review mandatory."""
from pathlib import Path
import struct,json,hashlib,argparse,re,zlib
parser=argparse.ArgumentParser(description=__doc__)
inputs=parser.add_mutually_exclusive_group(required=True)
inputs.add_argument('--manifest',type=Path)
inputs.add_argument('--workspace',type=Path)
parser.add_argument('--rom-directory',type=Path)
parser.add_argument('--games',nargs='+')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();result={}
assert not args.output.exists(),'Preserve previous inventory'
if args.workspace:
 from scenery_inputs import resolve_input
 assert args.games and not args.rom_directory
 manifest=[]
 for game in args.games:
  path,inv=resolve_input(args.workspace,game)
  manifest.append(dict(key=game,path=path,sha256=inv['rom_sha256'],crc32=inv.get('rom_crc32',inv.get('crc32'))))
else:
 assert args.rom_directory
 manifest=json.loads(args.manifest.read_text())['games']
 if args.games:manifest=[g for g in manifest if g['key'] in args.games]
for g in manifest:
 b=(g.get('path') or args.rom_directory/(g['key']+'.gba')).read_bytes();assert hashlib.sha256(b).hexdigest()==g['sha256']
 crc=f'{zlib.crc32(b):08x}';assert g['crc32'] in (None,crc);g['crc32']=crc
 def off(p,n=24):
  o=p-0x08000000
  if not 0<=o<=len(b)-n:raise ValueError('bad pointer')
  return o
 def template(p):
  o=off(p);f=struct.unpack_from('<HH5I',b,o)
  for ptr in f[2:6]:off(ptr,4)
  off(f[6]&~1,2)
  return f
 tables={}
 for match in re.finditer(bytes.fromhex('ffff')+b'[\x05\x09]'+bytes.fromhex('10'),b):
  address=match.start()+0x08000000
  if address%4:continue
  try:template(address)
  except (ValueError,struct.error):continue
  needle=struct.pack('<I',address);hit=0
  while True:
   hit=b.find(needle,hit)
   if hit<0:break
   table=hit-16;hit+=1
   if table<0 or table%4:continue
   try:
    ptrs=struct.unpack_from('<31I',b,table);fields={i:template(ptrs[i]) for i in (0,1,2,3,4,10,15,16,30)}
    if any(fields[i][0]!=0xffff or fields[i][1] not in (0x1005,0x1009) for i in (4,10,15,16,30)):continue
    # First four are four shadow sizes; the fifth is tall grass.
    if len(set(ptrs[:5]))!=5:continue
    tables[hex(table+0x08000000)]=[dict(index=i,template=hex(ptrs[i]),images=hex(fields[i][4]),palette_tag=hex(fields[i][1])) for i in (4,10,15,16,30)]
   except (ValueError,struct.error):continue
 result[g['key']]=dict(crc32=g['crc32'],rom_sha256=g['sha256'],tables=tables)
 print(g['key'],list(tables),flush=True)
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(result,indent=2))
