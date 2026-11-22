"""Audit reviewed facade crops against private source ground materials.

Read local ROMs only; report identities/counts, never source artwork. This
does not infer crop bounds, approve visuals, or replace exact-build Thor tests.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
from scenery_inventory import MapArt
from scenery_material_masks import visible_palette_indices
from scenery_buildings import validate
from scenery_inputs import resolve_input

def audit(workspace,profiles,include_uncropped=False):
 validate(profiles);results=[]
 for profile in profiles:
  if 'wall_crop_review' not in profile and not include_uncropped:continue
  game=profile['game'];shape=profile['shape']
  left=shape.get('wall_left',0);right=shape.get('wall_right',profile['width']*16)
  bottom=shape.get('wall_bottom',profile['height']*16)
  rom,inventory=resolve_input(workspace,game,profile['rom_sha256'])
  art=MapArt(rom)
  assert hashlib.sha256(art.data).hexdigest()==profile['rom_sha256']==inventory['rom_sha256']
  art.setup(inventory['numbers'],int(profile['primary'],16),int(profile['secondary'],16))
  source=Image.new('RGB',(profile['width']*16,profile['height']*16))
  for i,mid in enumerate(profile['cells']):source.paste(art.image(mid),(i%profile['width']*16,i//profile['width']*16))
  assert hashlib.sha256(source.tobytes()).hexdigest()==profile['source_art_sha256']
  ground=set(visible_palette_indices(art,profile['ground']))-{0}
  cells={mid:visible_palette_indices(art,mid) for mid in set(profile['cells'])}
  unexpected=[]
  for y in range(shape['wall_row'],bottom):
   for x in range(left,right):
    mid=profile['cells'][y//16*profile['width']+x//16]
    if cells[mid][y%16*16+x%16] in ground:unexpected.append((x,y))
  assert not unexpected,(game,profile['name'],'Source ground inside facade crop',unexpected)
  results.append(dict(game=game,name=profile['name'],rom_sha256=profile['rom_sha256'],
   source_art_sha256=profile['source_art_sha256'],ground_palette_indices=sorted(ground),
   wall_bounds=[left,right,bottom],crop_reviewed='wall_crop_review' in profile,unexpected_ground_pixels=0))
 return results

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--include-uncropped',action='store_true',help='Also inspect default facade bounds; material overlap still requires source-art review.');args=p.parse_args()
 profiles=json.loads((Path(__file__).parent/'scenery-profiles/android-buildings.json').read_text())
 results=audit(args.workspace,profiles,args.include_uncropped);args.report.write_text(json.dumps(results,indent=2)+'\n')
 print('Audited',len(results),'facade material bounds; no source ground remains.')
