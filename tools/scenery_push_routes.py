"""Plan local push probes from normalized map cells and live object positions.

Source proposals only: collision flags cannot prove story eligibility or a push.
"""
from collections import deque

def find_push_routes(width,height,cells,objects,player):
    assert len(cells)==width*height
    occupied={tuple(o['position']) for o in objects}
    directions={'u':(0,-1),'d':(0,1),'l':(-1,0),'r':(1,0)}
    def walk(p):
        return (0<=p[0]<width and 0<=p[1]<height
                and not cells[p[1]*width+p[0]]&0xc00 and p not in occupied)
    player=tuple(player);paths={player:[]};todo=deque([player])
    while todo:
        p=todo.popleft()
        for direction,(dx,dy) in directions.items():
            q=(p[0]+dx,p[1]+dy)
            if q not in paths and walk(q):
                paths[q]=paths[p]+[direction];todo.append(q)
    candidates=[]
    for obj in objects:
        if not obj['rock']:continue
        x,y=obj['position']
        for direction,(dx,dy) in directions.items():
            start=(x-dx,y-dy);destination=(x+dx,y+dy)
            if start in paths and walk(destination):
                candidates.append(dict(target=obj,start=start,destination=destination,
                                       direction=direction,approach=paths[start]))
    return sorted(candidates,key=lambda c:len(c['approach']))
