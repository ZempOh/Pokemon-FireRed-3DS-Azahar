"""Compare individual reviewed FR metatiles across private, hash-checked ROMs.

Unlike family transfer, a changed tree does not hide identical ground cells.
Output is metadata only and never automatically approves a renderer profile.
The recipe supplies reference {rom, sha256, primary, ids} and targets with
{game, rom, sha256, primary, numbers}. Only the verified FR 640/640/7/16
layout is supported; other layouts fail closed for a separate adapter.
"""
import argparse,hashlib,json
from pathlib import Path
from scenery_transfer import Art


def checked_art(record):
    art=Art(record['rom'])
    if hashlib.sha256(art.data).hexdigest()!=record['sha256']:
        raise ValueError('ROM hash mismatch')
    return art


def compare_cells(reference,reference_primary,target,target_primary,ids):
    rows=[]
    for mid in ids:
        try:
            source=reference.signature(reference_primary,[mid])
            other=target.signature(target_primary,[mid])
            rows.append(dict(id=mid,exact_match=source==other,reference_signature=source,target_signature=other))
        except ValueError as error:
            rows.append(dict(id=mid,exact_match=False,error=str(error)))
    return rows


def run(recipe):
    ref=recipe['reference'];source=checked_art(ref);rows=[]
    for target in recipe['targets']:
        row=dict(game=target['game'],rom_sha256=target['sha256'],primary=target['primary'],reviewed=False)
        numbers=target['numbers']
        if tuple(numbers[k] for k in ('tiles','metatiles','palettes','size'))!=(640,640,7,16):
            row['held']='Unsupported engine layout; no numeric-ID inheritance'
        else:
            art=checked_art(target)
            row['cells']=compare_cells(source,int(ref['primary'],0),art,int(target['primary'],0),ref['ids'])
        rows.append(row)
    return dict(reference_sha256=ref['sha256'],reference_primary=ref['primary'],targets=rows,
                note='Identity evidence only. Reference semantics, engine mapping and Thor qualification remain mandatory.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--recipe',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();result=run(json.loads(a.recipe.read_text()));a.output.write_text(json.dumps(result,indent=2)+'\n')
    for row in result['targets']:
        print(row['game'],sum(c['exact_match'] for c in row.get('cells',[])),'matching cells',row.get('held',''))
