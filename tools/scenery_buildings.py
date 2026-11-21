"""Emit exact-pattern building profiles without embedding source artwork."""
import argparse,json
from pathlib import Path

def validate(rows):
 seen=set()
 for row in rows:
  w,h=row['width'],row['height'];shape=row['shape']
  assert row['reviewed'] and 1<=w<=20 and 2<=h<=10
  assert len(row['cells'])==w*h and all(0<=x<1024 for x in row['cells'])
  assert len(row['source_art_sha256'])==len(row['rom_sha256'])==64
  assert 0<=shape['roof_top']<shape['wall_row']<h*16
  assert 0<=shape['back']<h*16 and 0<shape['wall_height']<=shape['ridge_height']<=128
  assert 0<=shape['hip_inset']<w*8 and 0<=row['ground']<1024
  key=(row['rom_crc32'],row['primary'],row['secondary'],tuple(row['cells']))
  assert key not in seen;seen.add(key)

def generate(rows,output):
 validate(rows)
 lines=['/* Generated exact source-art building identities; no ROM pixels. */','#pragma once',
  'struct SceneryBuildingProfile { uint32_t crc,primary,secondary; unsigned char width,height; unsigned short ground; SceneryBuildingShape shape; unsigned short cells[200]; };',
  'static const struct SceneryBuildingProfile sceneryBuildings[] = {']
 for row in rows:
  s=row['shape'];shape=[row['width']*16,row['height']*16,s['back'],s['wall_height'],s['ridge_height'],s['hip_inset'],s['roof_top'],s['wall_row'],row['height']*16,int(s.get('flat_roof',False))]
  lines.append(' {0x%s,%s,%s,%d,%d,%d,{%s},{%s}},'%(row['rom_crc32'],row['primary'],row['secondary'],row['width'],row['height'],row['ground'],','.join(map(str,shape)),','.join(map(str,row['cells']))))
 lines+=['};']
 output.write_text('\n'.join(lines)+'\n')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--profiles',type=Path,default=Path(__file__).with_name('scenery-profiles')/'android-buildings.json');p.add_argument('--output',type=Path,required=True);a=p.parse_args();generate(json.loads(a.profiles.read_text()),a.output)
