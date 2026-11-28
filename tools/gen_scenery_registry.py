"""Generate renderer recognition from reviewed capability and plant profiles."""
import argparse,json
from pathlib import Path

def validate_secondary_land(capabilities, review):
    declared=set()
    for p in capabilities:
        for land in p.get('secondary_land',[]):
            assert land['reviewed'] and land['primary'] and land['secondary']
            for mid in land['ids']:
                key=(p['game'],p['rom_crc32'],int(land['primary'],16),int(land['secondary'],16),mid)
                assert key not in declared and 512<=mid<1024
                declared.add(key)
    proven=set()
    for row in review['targets']:
        assert row['reviewed'] and len(row['rom_sha256'])==64
        for cell in row['cells']:
            assert len(cell['rgba_sha256'])==64 and cell['reference_id'] in review['reference_ids']
            key=(row['game'],row['rom_crc32'],int(row['primary'],16),int(row['secondary'],16),cell['id'])
            assert key not in proven
            proven.add(key)
    assert declared==proven, 'Secondary land requires exact reviewed source evidence'

def validate_land_masks(capabilities, review):
    declared=set();proven=set()
    for p in capabilities:
        for group in p.get('secondary_land_masks',[]):
            assert group['reviewed']
            for cell in group['cells']:
                rows=tuple(cell['rows'])
                assert len(rows)==16 and any(rows) and not all(x==65535 for x in rows)
                assert all(0<=x<=65535 for x in rows)
                key=(p['game'],p['rom_crc32'],int(group['primary'],16),int(group['secondary'],16),cell['id'],rows)
                assert key not in declared
                declared.add(key)
    reference={x['id']:x for x in review['reference_masks']}
    for p in review['targets']:
        assert p['reviewed'] and len(p['rom_sha256'])==64
        for cell in p['cells']:
            source=reference[cell['reference_id']]
            assert cell['rows']==source['rows'] and cell['rgba_sha256']==source['rgba_sha256']
            key=(p['game'],p['rom_crc32'],int(p['primary'],16),int(p['secondary'],16),cell['id'],tuple(cell['rows']))
            assert key not in proven
            proven.add(key)
    assert declared==proven, 'Visible-ground masks require exact reviewed source evidence'
    for proof in review['primary_full_land']:
        assert proof['reviewed'] and len(proof['rgba_sha256'])==64
        p=next(x for x in capabilities if x['game']==proof['game'])
        assert p['rom_crc32']==proof['rom_crc32']
        assert any(int(x['primary'],16)==int(proof['primary'],16) and proof['id'] in x['ids'] for x in p['land'])

def generate_trees(profiles,output):
    lines=['// Generated exact complete 2x2 tree patterns.','#pragma once',
        'struct SceneryTreeQuad { uint32_t rom,primary; uint16_t cells[4],ground; };',
        'static const struct SceneryTreeQuad sceneryTreeQuads[] = {']
    for p in profiles:
        assert p['reviewed'] and len(p['cells'])==4
        lines.append('    {0x%s,%s,{%s},%d},'%(p['rom_crc32'],p['primary'],','.join(map(str,p['cells'])),p['ground']))
    lines+=['};','static int sceneryTreeTileset(uint32_t rom,uint32_t primary) {',
        '    for(unsigned i=0;i<sizeof(sceneryTreeQuads)/sizeof(sceneryTreeQuads[0]);i++)',
        '        if(sceneryTreeQuads[i].rom==rom&&sceneryTreeQuads[i].primary==primary)return 1;',
        '    return 0;','}',
        'static int sceneryTreeGround(uint32_t rom,uint32_t primary,const int cells[4]) {',
        '    for(unsigned i=0;i<sizeof(sceneryTreeQuads)/sizeof(sceneryTreeQuads[0]);i++) {',
        '        const struct SceneryTreeQuad *p=&sceneryTreeQuads[i];',
        '        if(p->rom==rom&&p->primary==primary&&p->cells[0]==cells[0]&&p->cells[1]==cells[1]&&p->cells[2]==cells[2]&&p->cells[3]==cells[3])return p->ground;',
        '    }','    return -1;','}']
    (output/'pk_scenery_tree_profiles.h').write_text('\n'.join(lines)+'\n')

def generate_tall_trees(profiles,output):
    lines=['// Generated reviewed complete 2x3 tree patterns.','#pragma once',
        'struct SceneryTallTree { uint32_t rom,primary; uint16_t cells[6],ground; };',
        'static const struct SceneryTallTree sceneryTallTrees[] = {']
    for p in profiles:
        assert p['reviewed'] and len(p['cells'])==6
        lines.append('    {0x%s,%s,{%s},%d},'%(p['rom_crc32'],p['primary'],','.join(map(str,p['cells'])),p['ground']))
    lines+=['};','static int sceneryTallTreeGround(uint32_t rom,uint32_t primary,const int *cells) {',
        '    for(unsigned i=0;i<sizeof(sceneryTallTrees)/sizeof(sceneryTallTrees[0]);i++) {',
        '        const struct SceneryTallTree *p=&sceneryTallTrees[i];',
        '        if(p->rom!=rom||p->primary!=primary)continue;',
        '        int match=1;if(cells)for(int k=0;k<6;k++)if(cells[k]!=p->cells[k])match=0;',
        '        if(match)return p->ground;','    }','    return -1;','}']
    (output/'pk_scenery_tall_tree_profiles.h').write_text('\n'.join(lines)+'\n')

def generate_engines(profiles,output):
    lines=['// Generated candidate engine rows. Device qualification is separate.']
    for p in profiles:
        assert p['family'] in {'EX','EX640','EM','FR','EM640_40'}
        lines.append('    { 0x%s, PK_WIDE_FAMILY_%s, { %s } }, // %s'%(p['rom_crc32'],p['family'],', '.join('[PK_WIDE_%s]=0x%s'%(k,v) for k,v in p['slots'].items()),p['game']))
    (output/'pk_scenery_engine_rows.h').write_text('\n'.join(lines)+'\n')

def generate_ground_props(profiles,output):
    lines=['// Generated reviewed field props; no ROM artwork.','#pragma once',
           'struct SceneryGroundProp { uint32_t rom,primary,secondary; uint16_t id,ground; uint8_t kind,ink[6],paletteInk[3],clearLayer,floorClimate; };',
           'static const struct SceneryGroundProp sceneryGroundProps[] = {']
    seen={}
    for p in profiles:
        key=(p['rom_crc32'],p['primary'],p['id'])
        secondary=int(p.get('secondary','0'),16)
        prior=seen.setdefault(key,set())
        assert p['reviewed'] and secondary not in prior and 0 not in prior and (secondary or not prior)
        assert p['kind'] in (1,3,4,13)
        if p['kind']==1:assert p.get('behavior')==2,'Encounter grass needs reviewed own-ROM tall-grass semantics'
        floor=p.get('source_floor')
        clear=climate=0
        if floor:
            assert 'ground' not in p and secondary and floor['clear_layer'] in (1,2)
            clear=floor['clear_layer']
            climate={'path':1,'turf':2}[floor['surface']]
        else:
            assert 0<=p['ground']<512
        assert 0<=p['id']<(1024 if secondary else 512) and len(p['ink'])==6 and all(0<=n<16 for n in p['ink'])
        palette_inks=p.get('palette_inks',[0,0,0])
        if 'palette_inks' in p:
            assert p['kind']==13 and len(palette_inks)==3, 'Fixed palette inks are only for reviewed flowers'
            assert all(0<n<256 and n%16 for n in palette_inks), 'Palette inks need opaque BG colors'
        prior.add(secondary)
        lines.append('    {0x%s,%s,%#x,%d,%d,%d,{%s},{%s},%d,%d},'%(p['rom_crc32'],p['primary'],secondary,p['id'],p.get('ground',0),p['kind'],','.join(map(str,p['ink'])),','.join(map(str,palette_inks)),clear,climate))
    lines+=['};','static const struct SceneryGroundProp *sceneryGroundProp(uint32_t rom,uint32_t primary,uint32_t secondary,int id) {',
            '    for(unsigned i=0;i<sizeof(sceneryGroundProps)/sizeof(sceneryGroundProps[0]);i++) {',
            '        const struct SceneryGroundProp *p=&sceneryGroundProps[i];',
            '        if(p->rom==rom && p->primary==primary && (!p->secondary || p->secondary==secondary) && p->id==id)return p;',
            '    }','    return 0;','}',
            'static int sceneryGroundPropsTileset(uint32_t rom,uint32_t primary,uint32_t secondary) {',
            '    for(unsigned i=0;i<sizeof(sceneryGroundProps)/sizeof(sceneryGroundProps[0]);i++) {',
            '        const struct SceneryGroundProp *p=&sceneryGroundProps[i];',
            '        if(p->rom==rom && p->primary==primary && (!p->secondary || p->secondary==secondary))return 1;',
            '    }',
            '    return 0;','}']
    (output/'pk_scenery_ground_props.h').write_text('\n'.join(lines)+'\n')

def generate_objects(profiles,output):
    lines=['// Generated from semantically reviewed live-object image tables.','#pragma once',
           'struct SceneryObjectProfile { uint32_t rom,images; uint8_t kind,leaf,bark; };',
           'static const struct SceneryObjectProfile sceneryObjects[] = {']
    seen=set()
    for p in profiles:
        if not p['reviewed']:continue
        key=(p['rom_crc32'],p['image_table'])
        if key in seen:raise ValueError('Duplicate object image table')
        seen.add(key)
        assert p['kind'] in (7,8,9,12)
        lines.append('    {0x%s,0x%s,%d,%d,%d}, // %s: %s'%(key[0],key[1],p['kind'],p['leaf'],p['bark'],p['game'],p['asset']))
    lines+=['};','static const struct SceneryObjectProfile *sceneryObjectProfile(uint32_t rom,uint32_t images) {',
            '    for(unsigned i=0;i<sizeof(sceneryObjects)/sizeof(sceneryObjects[0]);i++)',
            '        if(sceneryObjects[i].rom==rom&&sceneryObjects[i].images==images)return &sceneryObjects[i];',
            '    return 0;','}']
    (output/'pk_scenery_object_profiles.h').write_text('\n'.join(lines)+'\n')

def generate(profiles, plants, output):
    crc=lambda p:int(p['rom_crc32'],16)
    def cases(items):return '\n'.join('    case 0x%08x:'%crc(p) for p in items)
    lines=['// Generated by gen_scenery_registry.py. Candidate capabilities are not qualification.','#pragma once','#include <stdint.h>']
    for name,cap,primary in [('sceneryCandidate','climate',False),('sceneryKanto','kanto',True),('sceneryRadicalProps','radical_props',True)]:
        lines += ['static int %s(uint32_t crc%s) {'%(name,',uint32_t primary' if primary else '')]
        if primary:
            for p in profiles:
                if p.get(cap):lines.append('    if(crc==0x%s)return %s;'%(p['rom_crc32'],' || '.join('primary=='+address for address in p.get(cap+'_primary',['0x082d4a94']))))
            lines+=['    return 0;','}']
        else:
            lines+=['    switch(crc) {',cases([p for p in profiles if p.get(cap)]),'        return 1;','    default:return 0;','    }','}']
    lines+=['static int sceneryLand(uint32_t crc,uint32_t primary,int id) {']
    for p in profiles:
        for land in p.get('land',[]):
            assert land['ids'] and all(0<=n<1024 for n in land['ids'])
            lines.append('    if(crc==0x%s && primary==%s && (%s))return 1;'%(p['rom_crc32'],land['primary'],' || '.join('id==%d'%n for n in land['ids'])))
    lines+=['    return 0;','}']
    lines+=['static int scenerySecondaryLand(uint32_t crc,uint32_t primary,uint32_t secondary,int id) {']
    for p in profiles:
        for land in p.get('secondary_land',[]):
            assert land['reviewed'] and land['ids'] and all(512<=n<1024 for n in land['ids'])
            assert land['primary'] and land['secondary']
            lines.append('    if(crc==0x%s && primary==%s && secondary==%s && (%s))return 1;'%(p['rom_crc32'],land['primary'],land['secondary'],' || '.join('id==%d'%n for n in land['ids'])))
    lines+=['    return 0;','}']
    lines+=['static const uint16_t *scenerySecondaryLandMask(uint32_t crc,uint32_t primary,uint32_t secondary,int id) {']
    for p in profiles:
        for group in p.get('secondary_land_masks',[]):
            assert group['reviewed'] and group['cells']
            lines.append('    if(crc==0x%s && primary==%s && secondary==%s) {'%(p['rom_crc32'],group['primary'],group['secondary']))
            lines.append('        static const uint16_t rows[][16] = {')
            for cell in group['cells']:
                # Legacy group name also accepts reviewed primary mixed cells.
                # Both tileset identities remain required by the lookup/proof.
                assert len(cell['rows'])==16 and 0<=cell['id']<1024
                lines.append('            {%s},'%','.join(hex(x) for x in cell['rows']))
            lines+=['        };','        switch(id) {']
            for i,cell in enumerate(group['cells']):lines.append('        case %d:return rows[%d];'%(cell['id'],i))
            lines+=['        default:return 0;','        }','    }']
    lines+=['    return 0;','}']
    lines+=['static int sceneryLandCapRows(uint32_t crc,uint32_t primary,int id) {']
    for p in profiles:
        for cap in p.get('land_caps',[]):
            assert 0<cap['rows']<16 and cap['ids'] and all(0<=n<1024 for n in cap['ids'])
            assert not any(set(cap['ids'])&set(land['ids']) for land in p.get('land',[]) if land['primary']==cap['primary'])
            lines.append('    if(crc==0x%s && primary==%s && (%s))return %d;'%(p['rom_crc32'],cap['primary'],' || '.join('id==%d'%n for n in cap['ids']),cap['rows']))
    lines+=['    return 0;','}']
    lines+=['static int sceneryOutdoor(uint32_t crc,int group,int num,int mapType) {',
            '    if(mapType>=1 && mapType<=3)return 1;']
    for p in profiles:
        for group,num in p.get('outdoor_maps',[]):
            lines.append('    if(crc==0x%s && group==%d && num==%d && mapType==0)return 1;'%(p['rom_crc32'],group,num))
    lines+=['    return 0;','}']
    output.mkdir(parents=True,exist_ok=True)
    (output/'pk_scenery_candidates.h').write_text('\n'.join(lines)+'\n')
    lines=['// Generated from verified local ROM profiles; no ROM textures.','#pragma once','struct SolidPlantProfile { uint32_t rom,primary,secondary; uint16_t top,bottom; uint8_t shape,height,width,centerX2,foot,ink[12],topLayer,bottomLayer; };','static const struct SolidPlantProfile solidPlantProfiles[] = {']
    seen=set()
    for p in plants:
        assert not {'topLayer','bottomLayer'} & p.keys(), 'Plant profiles require top_layer/bottom_layer; camelCase would silently select the wrong layer'
        key=(crc(p),int(p['primary'],16),int(p.get('secondary','0'),16),p['top'],p['bottom'])
        if key in seen:raise ValueError('Duplicate plant profile')
        seen.add(key)
        assert p['shape'] in (0,1,2)
        if p['shape']==2:
            assert p.get('asset_kind')=='bamboo_room_screen' and p['height']==24 and p['width']==16
        assert len(p['ink'])==12 and all(0<=v<16 for v in p['ink'][::2]) and all(0<=v<32 for v in p['ink'][1::2])
        top_layer,bottom_layer=p.get('top_layer',1),p.get('bottom_layer',1)
        assert top_layer in (1,2) and bottom_layer in (1,2)
        lines.append('    {0x%08x,0x%08x,0x%08x,0x%x,0x%x,%d,%d,%d,%d,%d,{%s},%d,%d},'%(*key,p['shape'],p['height'],p['width'],p['center_x2'],p['foot'],','.join(map(str,p['ink'])),top_layer,bottom_layer))
    lines+=['};','static int solidPlantProfile(uint32_t rom,uint32_t primary,uint32_t secondary,int top,int bottom) {','    for(unsigned i=0;i<sizeof(solidPlantProfiles)/sizeof(solidPlantProfiles[0]);i++) {','        const struct SolidPlantProfile *p=&solidPlantProfiles[i];','        if(p->rom==rom&&p->primary==primary&&(!p->secondary||p->secondary==secondary)&&p->top==top&&p->bottom==bottom)return (int)i;','    }','    return -1;','}','static int solidPlantTileset(uint32_t rom,uint32_t primary) {','    for(unsigned i=0;i<sizeof(solidPlantProfiles)/sizeof(solidPlantProfiles[0]);i++)','        if(solidPlantProfiles[i].rom==rom&&solidPlantProfiles[i].primary==primary)return 1;','    return 0;','}']
    (output/'pk_scenery_plant_profiles.h').write_text('\n'.join(lines)+'\n')

def generate_small_fixtures(profiles, output):
    lines = ['// Generated from reviewed tileset pairs and source layers.',
             '#pragma once',
             'enum SceneryFixtureShape { SCENERY_STEEL_FENCE, SCENERY_CUT_TIMBER, SCENERY_SIGN };',
             'struct SceneryFixture { uint16_t tile; uint8_t shape, rail, posts, x[2], ink[4], art; };',
             'struct SceneryFixtureGroup { uint32_t rom, primary, secondary; uint16_t first, count; };',
             'struct SceneryFixtureArt { uint8_t box[4]; uint16_t mask[16]; };',
             'static const struct SceneryFixture sceneryFixtures[] = {']
    shapes = {'steel_fence': 'SCENERY_STEEL_FENCE', 'cut_timber': 'SCENERY_CUT_TIMBER', 'sign': 'SCENERY_SIGN'}
    signs = {}
    rails = {'none': 0, 'horizontal': 1, 'vertical': 2, 'corner_left': 3, 'corner_right': 4,
             'north_corner_left': 5, 'north_corner_right': 6}
    groups = {}
    seen = set()
    for profile in profiles:
        key = (int(profile['rom_crc32'], 16), int(profile['primary'], 16),
               int(profile['secondary'], 16), profile['id'])
        posts = profile['feet_x']
        ink = profile['ink']
        assert key not in seen and 0 <= key[3] < 1024 and profile['reviewed']
        seen.add(key)
        assert all(len(bytes.fromhex(profile[field])) == 32 for field in
                   ('rom_sha256', 'source_art_sha256', 'floor_sha256'))
        assert 1 <= len(posts) <= 2 and all(3 <= x <= 13 for x in posts)
        assert posts == sorted(set(posts))
        assert len(ink) == 4 and all(0 <= coordinate < 16 for coordinate in ink)
        steel = profile['shape'] == 'steel_fence'
        rail = rails[profile.get('rail', 'horizontal' if steel else 'none')]
        assert (rail != 0) == steel
        assert not steel or len(posts) == (1 if rail == rails['vertical'] else 2)
        art = 0
        if profile['shape'] == 'sign':
            box = tuple(profile['board'])
            mask = tuple(profile['board_mask'])
            x, y, w, h = box
            assert len(posts) == 1 and 0 <= x < 16 and 0 <= y < 16
            assert 1 <= w <= 16 - x and 1 <= h <= 16 - y and len(mask) == h
            assert all(0 <= row < 1 << w for row in mask) and any(mask)
            art = signs.setdefault((box, mask), len(signs) + 1)
            assert art <= 255
        line = '    {0x%x, %s, %d, %d, {%s}, {%s}, %d},' % (
            key[3], shapes[profile['shape']], rail, len(posts),
            ','.join(map(str, posts)), ','.join(map(str, ink)), art)
        overlay = profile.get('overlay_layer', 1)
        assert type(overlay) is int and overlay in (1, 2)
        groups.setdefault(key[:3], {})[key[3]] = line, overlay
    assert 0 < len(seen) <= 65535
    offsets = []
    third_layer = []
    first = 0
    for key, fixtures in sorted(groups.items()):
        count = len(fixtures)
        for index, (_, (line, overlay)) in enumerate(sorted(fixtures.items()), first):
            lines.append(line)
            if overlay == 2:
                third_layer.append(index)
        offsets.append('    {0x%08x, 0x%08x, 0x%08x, %d, %d},' % (*key, first, count))
        first += count
    lines.extend(['};', 'static const struct SceneryFixtureArt sceneryFixtureArt[] = {', '    {{0}, {0}},'])
    for box, mask in signs:
        lines.append('    {{%s}, {%s}},' % (', '.join(map(str, box)), ', '.join(hex(row) for row in mask)))
    lines.extend(['};', 'static const struct SceneryFixtureGroup sceneryFixtureGroups[] = {', *offsets])
    lines.extend([
        '};',
        'static const struct SceneryFixtureGroup* scenerySmallFixtureGroup(uint32_t rom, uint32_t primary, uint32_t secondary) {',
        '    for (unsigned i=0; i<sizeof(sceneryFixtureGroups)/sizeof(sceneryFixtureGroups[0]); ++i) {',
        '        const struct SceneryFixtureGroup* p=&sceneryFixtureGroups[i];',
        '        if (p->rom==rom && p->primary==primary && p->secondary==secondary) return p;',
        '    }',
        '    return 0;',
        '}',
        'static int scenerySmallFixture(const struct SceneryFixtureGroup* group, int tile) {',
        '    if (!group) return -1;',
        '    int first=group->first, last=first+group->count;',
        '    while (first<last) {',
        '        int mid=first+(last-first)/2;',
        '        if (sceneryFixtures[mid].tile==tile) return mid;',
        '        if (sceneryFixtures[mid].tile<tile) first=mid+1;',
        '        else last=mid;',
        '    }',
        '    return -1;',
        '}',
        'static int scenerySmallFixtureOverlayLayer(int index) {',
        '    switch (index) {',
        *(f'    case {index}: return 2;' for index in third_layer),
        '    default: return 1;',
        '    }',
        '}',
    ])
    (output/'pk_scenery_small_fixtures.h').write_text('\n'.join(lines)+'\n')


def generate_grass_effects(profiles,output):
    lines=['// Generated reviewed live foliage effects; exact ROM/template/image identity.', '#pragma once',
           'struct SceneryGrassEffect { uint32_t rom,template,images; };',
           'static const struct SceneryGrassEffect sceneryGrassEffects[] = {']
    seen=set()
    for p in profiles:
        key=(p['rom_crc32'],p['template'],p['images'])
        assert p['reviewed'] and key not in seen and p['index'] in (4,10,15,16,30)
        assert len(p['rom_sha256'])==len(p['template_sha256'])==64
        assert p['frames'] and all(len(f['sha256'])==64 and f['bytes'] in (64,128) for f in p['frames'])
        seen.add(key)
        if not p['climate_foliage']:
            assert p['exclusion'];continue
        lines.append('    {0x%s,%s,%s},'%key)
    lines+=['};','static int sceneryGrassEffect(uint32_t rom,uint32_t template,uint32_t images) {',
            '    for(unsigned i=0;i<sizeof(sceneryGrassEffects)/sizeof(sceneryGrassEffects[0]);i++) {',
            '        const struct SceneryGrassEffect *p=&sceneryGrassEffects[i];',
            '        if(p->rom==rom && p->template==template && p->images==images)return 1;',
            '    }','    return 0;','}']
    (output/'pk_scenery_grass_effects.h').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    root=Path(__file__).with_name('scenery-profiles')
    capabilities=json.loads((root/'android-capabilities.json').read_text())
    validate_secondary_land(capabilities,json.loads((root/'android-secondary-land-review.json').read_text()))
    validate_land_masks(capabilities,json.loads((root/'android-land-mask-review.json').read_text()))
    outdoor_review=json.loads((root/'android-outdoor-review.json').read_text())
    keys=set()
    for row in outdoor_review:
        key=(row['rom_crc32'],row['group'],row['map'])
        assert row['reviewed'] and key not in keys
        assert len(row['rom_sha256'])==len(row['source_map_sha256'])==64
        keys.add(key)
    for profile in capabilities:
        declared={tuple(x) for x in profile.get('outdoor_maps',[])}
        reviewed={(x['group'],x['map']) for x in outdoor_review if x['rom_crc32']==profile['rom_crc32'] and x['outdoor']}
        assert declared==reviewed,('Outdoor overrides require explicit source-art review',profile['game'])
    generate(capabilities,json.loads((root/'android-potted-plants.json').read_text()),args.output)
    generate_engines(json.loads((root/'android-engines.json').read_text()),args.output)
    generate_objects(json.loads((root/'android-live-objects.json').read_text()),args.output)
    generate_trees(json.loads((root/'android-tree-quads.json').read_text()),args.output)

    generate_tall_trees(json.loads((root/'android-tall-trees.json').read_text()),args.output)
    generate_ground_props(json.loads((root/'android-ground-props.json').read_text()),args.output)
    generate_grass_effects(json.loads((root/'android-grass-effects.json').read_text()),args.output)
    generate_small_fixtures(json.loads((root/'android-small-fixtures.json').read_text()),args.output)
    from gen_scenery_ground_patterns import generate_ground_patterns
    generate_ground_patterns(json.loads((root/'android-ground-patterns.json').read_text()),args.output)
