"""Build a static, hash-checked gallery from already selected release media."""
from pathlib import Path
import argparse,hashlib,html,json
NAMES={'classic':'Pokémon Classic','firered':'FireRed 3DS','frlg':'FireRed & LeafGreen+','letsgo':'Let’s Go Pikachu','radical':'Radical Red','unbound':'Unbound','better-emerald-2':'Better Than Better Emerald 2','modern-emerald':'Modern Emerald','fakemon':'Fakemon FireRed','lazarus':'Lazarus','dragonsden':'Dragonsden','ash-gray':'Ash Gray','gaia':'Gaia','rocket':'FireRed Rocket Edition','seaglass':'Emerald Seaglass','odyssey':'Odyssey'}
def render(media,output):
 rows=json.loads((media/'manifest.json').read_text(encoding='utf-8'));by={}
 for row in rows:
  assert row['game'] in NAMES and Path(row['file']).name==row['file']
  file=media/row['file'];assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256'],file
  assert row.get('commit') and row.get('build_reference')
  by.setdefault(row['game'],[]).append(row)
 esc=html.escape
 body=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PokéDaisy graphics gallery</title><link rel="stylesheet" href="assets/css/site.css"><style>.views{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}.views figure{margin:0}.views img{width:100%;height:auto;image-rendering:auto;border-radius:10px}section{margin:40px 0}figcaption{padding:8px 0}.games{display:flex;flex-wrap:wrap;gap:14px}code{overflow-wrap:anywhere}</style><main class="wrap"><p><a href="voxel.html">Back to builder</a></p><h1>Graphics on the Thor</h1><p>Actual device captures from the published builds. Each game links to its test scope. Coverage is limited to the reviewed environmental profiles and scenes; character and battle Pokémon sprites remain their original art.</p><nav class="games">']
 for g in NAMES:
  if g in by:body.append(f'<a href="#{g}">{esc(NAMES[g])}</a>')
 body.append('</nav>')
 groups=[('2D and 3D', [('2d','png'),('3d','png')]),('Four seasons',[(v,'png') for v in ('spring','summer','autumn','winter')]),('Weather',[(v,'png') for v in ('clear','rain','snow','fog','automatic')]),('Scenery in motion',[('motion','gif'),('natural-transition','gif'),('weather-transition','gif')]),('Battles and scenery interactions',[('battle','png'),('battle','gif'),('boulder-moving','gif'),('rock-smash','gif'),('cut-tree','gif')])]
 for g in NAMES:
  if g not in by:continue
  items=by[g];commits=sorted({x['commit'] for x in items});refs=sorted({x['build_reference'] for x in items})
  body.append(f'<section id="{g}"><h2>{esc(NAMES[g])}</h2><p>'+ ' · '.join(f'<a href="{esc(ref,quote=True)}">Build and Thor test scope</a>' for ref in refs)+'</p>')
  for title,views in groups:
   selected=[]
   for view,ext in views:
    matches=[x for x in items if x['view']==view and x['file'].endswith('.'+ext)]
    assert len(matches)<=1,(g,view,ext)
    selected+=matches
   if not selected:continue
   body.append(f'<h3>{esc(title)}</h3><div class="views">')
   for row in selected:
    caption=row['view'].replace('-',' ').title();body.append(f'<figure><img loading="lazy" src="assets/gallery/{esc(row["file"],quote=True)}" alt="{esc(NAMES[g]+": actual Thor "+caption,quote=True)}"><figcaption>{esc(caption)}</figcaption></figure>')
   body.append('</div>')
  body.append('<p>Source build'+('s' if len(commits)>1 else '')+': '+', '.join('<code>'+esc(c)+'</code>' for c in commits)+'.</p></section>')
 body.append('<p><a href="assets/gallery/manifest.json">Capture hashes and build references</a>. GIF frame rate is reduced for download size and is not a gameplay performance measurement.</p></main></html>')
 output.write_text(''.join(body),encoding='utf-8');print('Rendered',len(by),'games from',len(rows),'hash-verified release images')
def render_builder_motion(media,page):
 rows=json.loads((media/'manifest.json').read_text(encoding='utf-8'));cards=[];esc=html.escape
 for game,name in NAMES.items():
  selected={}
  for view,ext in (('3d','png'),('motion','gif')):
   matches=[row for row in rows if row['game']==game and row['view']==view and row['file'].endswith('.'+ext)]
   assert len(matches)<=1
   if matches:
    row=matches[0];assert hashlib.sha256((media/row['file']).read_bytes()).hexdigest()==row['sha256'];selected[view]=row['file']
  if not selected:continue
  assert len(selected)==2
  cards.append(f'<article class="panel"><h3>{esc(name)}</h3><figure class="motion"><img src="assets/gallery/{selected["3d"]}" data-still="assets/gallery/{selected["3d"]}" data-gif="assets/gallery/{selected["motion"]}" alt="{esc(name)} actual Thor capture" loading="lazy" width="480" height="270"><figcaption><button type="button" class="btn btn-ghost" data-motion aria-pressed="false">Play GIF</button> <a href="assets/gallery/{selected["motion"]}">Open GIF</a></figcaption></figure><a href="gallery.html#{game}">2D / 3D, seasons and battles</a></article>')
 begin='<!-- THOR GALLERY START -->';end='<!-- THOR GALLERY END -->';text=page.read_text(encoding='utf-8');a=text.index(begin);b=text.index(end,a)+len(end)
 body=begin+'<section aria-labelledby="gallery-title"><h2 id="gallery-title">See every game in motion</h2><p>Actual passing-build captures on the AYN Thor. <a href="gallery.html">Complete comparison gallery and test scope</a>. GIFs play on request.</p><div class="motion-grid">'+''.join(cards)+'</div></section>'+end
 page.write_text(text[:a]+body+text[b:],encoding='utf-8')
 print('Rendered builder motion cards:',len(cards))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--media',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();render(a.media,a.output)
