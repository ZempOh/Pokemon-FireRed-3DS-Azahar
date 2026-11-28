"""Emit exact-pattern building profiles without embedding source artwork."""
import argparse,json,math
from pathlib import Path

def hip_roof_texels(shape, width):
 """Source texels touched by the hip roof UVs in SceneryBuilding_Emit."""
 ridge_v=shape['roof_top']+.5
 eave_v=shape['wall_row']-.5
 ridge_left=shape['hip_inset']
 ridge_right=width-ridge_left
 eave_left=shape.get('roof_left',0)+.5
 eave_right=shape.get('roof_right',width)-.5
 # The front and rear share a UV trapezoid. The side hips sample its edges.
 top,bottom=sorted((ridge_v,eave_v))
 for y in range(math.floor(top),math.floor(bottom)+1):
  start,end=0,1
  if eave_v!=ridge_v:
   start=(max(y,top)-ridge_v)/(eave_v-ridge_v)
   end=(min(y+1,bottom)-ridge_v)/(eave_v-ridge_v)
  left=min(ridge_left+(eave_left-ridge_left)*t for t in (start,end))
  right=max(ridge_right+(eave_right-ridge_right)*t for t in (start,end))
  for x in range(math.floor(left),min(width-1,math.floor(right))+1):
   yield x,y

def validate(rows):
 seen=set()
 for row in rows:
  w,h=row['width'],row['height'];shape=row['shape']
  assert all(isinstance(v,(int,float)) and math.isfinite(v) for v in shape.values())
  assert row['reviewed'] and 1<=w<=20 and 2<=h<=10
  assert len(row['cells'])==w*h and all(0<=x<1024 for x in row['cells'])
  assert len(row['source_art_sha256'])==len(row['rom_sha256'])==64
  assert 0<=shape['roof_top']<shape['wall_row']<h*16
  assert 0<=shape['back']<h*16 and 0<shape['wall_height']<=shape['ridge_height']<=128
  assert 0<=shape['hip_inset']<w*8 and 0<=row['ground']<1024
  assert 0<=shape.get('wall_left',0)<shape.get('wall_right',w*16)<=w*16
  assert shape.get('wall_right',w*16)-shape.get('wall_left',0)>=16
  assert shape['wall_row']<shape.get('wall_bottom',h*16)<=h*16
  assert 0<=shape.get('roof_left',0)<shape.get('roof_right',w*16)<=w*16
  assert shape.get('roof_right',w*16)-shape.get('roof_left',0)>=16
  if any(k in shape for k in ('roof_left','roof_right')):
   assert row['roof_crop_review']['source_art_sha256']==row['source_art_sha256']
  if 'roof_crop_review' in row:assert row['roof_crop_review']['source_art_sha256']==row['source_art_sha256']
  if any(k in shape for k in ('wall_left','wall_right','wall_bottom')):
   assert row['wall_crop_review']['source_art_sha256']==row['source_art_sha256']
  kind=shape.get('roof_kind',int(shape.get('flat_roof',False)))
  assert kind in (0,1,2)
  if kind==1:assert shape['ridge_height']==shape['wall_height']
  else:assert shape['ridge_height']>shape['wall_height']
  if kind==2:
   assert .1<=shape['gable_x']<=.9
   assert shape['roof_top']<shape['gable_row']<shape['wall_row']
   assert shape['wall_height']<shape.get('ridge_back_height',shape['ridge_height'])<=128
  key=(row['rom_crc32'],row['primary'],row['secondary'],tuple(row['cells']))
  assert key not in seen;seen.add(key)

def generate(rows,output):
 validate(rows)
 lines=['/* Generated exact source-art building identities; no ROM pixels. */','#pragma once',
  'struct SceneryBuildingProfile { uint32_t crc,primary,secondary; unsigned char width,height; unsigned short ground; SceneryBuildingShape shape; unsigned short cells[200]; };',
  'static const struct SceneryBuildingProfile sceneryBuildings[] = {']
 for row in rows:
  s=row['shape'];shape=[row['width']*16,row['height']*16,s['back'],s['wall_height'],s['ridge_height'],s['hip_inset'],s['roof_top'],s['wall_row'],row['height']*16,s.get('roof_kind',int(s.get('flat_roof',False))),s.get('gable_x',.5),s.get('gable_row',s['roof_top']),s.get('ridge_back_height',s['ridge_height'])]
  shape += [s.get('wall_left',0),s.get('wall_right',row['width']*16),s.get('wall_bottom',row['height']*16)]
  shape += [s.get('roof_left',0),s.get('roof_right',row['width']*16)]
  lines.append(' {0x%s,%s,%s,%d,%d,%d,{%s},{%s}},'%(row['rom_crc32'],row['primary'],row['secondary'],row['width'],row['height'],row['ground'],','.join(map(str,shape)),','.join(map(str,row['cells']))))
 lines+=['};']
 output.write_text('\n'.join(lines)+'\n')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--profiles',type=Path,default=Path(__file__).with_name('scenery-profiles')/'android-buildings.json');p.add_argument('--output',type=Path,required=True);a=p.parse_args();generate(json.loads(a.profiles.read_text()),a.output)
