"""Recognize complete reviewed ground patterns without recoloring reused cliff cells."""
import json
from pathlib import Path

def generate_ground_patterns(profiles, output):
    seen = set()
    lines = ['// Generated complete ground patterns; individual cell IDs are not sufficient.',
             '#pragma once', '#include <stdint.h>',
             'struct SceneryGroundPattern { uint32_t rom,primary,secondary; uint8_t width,height; uint16_t cells[16]; };',
             'static const struct SceneryGroundPattern sceneryGroundPatterns[] = {']
    for p in profiles:
        assert p['reviewed'] and p['scope'] == 'complete_ground_pattern'
        assert 1 <= p['width'] <= 4 and 1 <= p['height'] <= 4
        assert len(p['cells']) == p['width'] * p['height'] > 1
        assert len(p['rom_sha256']) == 64
        assert all(0 <= x['id'] < 1024 and len(x['rgba_sha256']) == 64 for x in p['cells'])
        key = (p['rom_crc32'], p['primary'], p['secondary'], p['width'], p['height'], tuple(x['id'] for x in p['cells']))
        assert key not in seen
        seen.add(key)
        lines.append('    {0x%s,%s,%s,%d,%d,{%s}},' % (*key[:5], ','.join(map(str,key[5]))))
    lines += ['};',
        'typedef int (*SceneryGroundRead)(const void*,int,int,uint32_t*,uint32_t*);',
        'static int sceneryPatternLand(uint32_t rom,uint32_t primary,uint32_t secondary,int id,int x,int y,const void *context,SceneryGroundRead read) {',
        '    for(unsigned n=0;n<sizeof(sceneryGroundPatterns)/sizeof(sceneryGroundPatterns[0]);n++) {',
        '        const struct SceneryGroundPattern *p=&sceneryGroundPatterns[n];',
        '        if(p->rom!=rom || p->primary!=primary || p->secondary!=secondary)continue;',
        '        for(int slot=0;slot<p->width*p->height;slot++) {',
        '            if(p->cells[slot]!=id)continue;',
        '            int left=x-slot%p->width,top=y-slot/p->width,match=1;',
        '            for(int i=0;i<p->width*p->height;i++) {',
        '                uint32_t a=0,b=0;',
        '                int cell=read(context,left+i%p->width,top+i/p->width,&a,&b);',
        '                if(cell!=p->cells[i] || a!=primary || b!=secondary) { match=0;break; }',
        '            }',
        '            if(match)return 1;',
        '        }',
        '    }',
        '    return 0;',
        '}']
    output.mkdir(parents=True, exist_ok=True)
    (output/'pk_scenery_ground_patterns.h').write_text('\n'.join(lines)+'\n')

if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    generate_ground_patterns(json.loads(Path(__file__).with_name('scenery-profiles').joinpath('android-ground-patterns.json').read_text()),args.output)
