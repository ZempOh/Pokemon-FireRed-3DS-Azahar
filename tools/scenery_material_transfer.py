"""Find exact reviewed cell artwork across an identity-checked game's tilesets.

Supports MapArt's declared layer layouts. This produces evidence, not approval.
Reference semantics and full-size device review remain required.
"""
import argparse,hashlib,json
from pathlib import Path
from scenery_inputs import resolve_input
from scenery_inventory import MapArt

def compare(workspace,game,primary,secondary,ids):
    rom,inv=resolve_input(workspace,game)
    art=MapArt(rom);art.setup(inv['numbers'],primary,secondary)
    references={hashlib.sha256(art.image(mid).convert('RGBA').tobytes()).hexdigest():mid for mid in ids}
    assert len(references)==len(ids),'References must identify distinct artwork'
    targets=[];held=[]
    for pair in inv['tileset_pairs']:
        p,s=int(pair['primary'],16),int(pair['secondary'],16)
        cells=[]
        try:
            art.setup(inv['numbers'],p,s)
            for mid in sorted(int(mid,0) for mid in pair['used_metatiles']):
                if mid<inv['numbers']['metatiles']:continue
                sha=hashlib.sha256(art.image(mid).convert('RGBA').tobytes()).hexdigest()
                if sha in references:cells.append(dict(id=mid,reference_id=f'{game}:{references[sha]:x}',rgba_sha256=sha))
        except (ValueError,IndexError) as error:
            held.append(dict(primary=pair['primary'],secondary=pair['secondary'],reason=str(error)));continue
        if cells:targets.append(dict(game=game,rom_crc32=inv['rom_crc32'],rom_sha256=inv['rom_sha256'],primary=pair['primary'],secondary=pair['secondary'],reviewed=False,cells=cells))
    return dict(game=game,rom_sha256=inv['rom_sha256'],primary=hex(primary),secondary=hex(secondary),references=[dict(id=f'{game}:{mid:x}',rgba_sha256=sha) for sha,mid in references.items()],targets=targets,held=held,qualified=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workspace',type=Path,required=True);p.add_argument('--game',required=True);p.add_argument('--primary',type=lambda x:int(x,0),required=True);p.add_argument('--secondary',type=lambda x:int(x,0),required=True);p.add_argument('--ids',type=lambda x:int(x,0),nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=compare(a.workspace,a.game,a.primary,a.secondary,a.ids);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print('Exact matching cells:',sum(len(row['cells']) for row in result['targets']),'held pairs:',len(result['held']))
