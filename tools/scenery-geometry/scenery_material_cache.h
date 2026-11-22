#pragma once
#include <stdint.h>

/* Reset for every source snapshot. Never reuse across palette, VRAM, map,
 * layer-order or alpha changes. Returned tiles survive until their slot evicts. */
#define SCENERY_MATERIAL_SLOTS 8
struct SceneryMaterialCache {
    unsigned count, next;
    int ids[SCENERY_MATERIAL_SLOTS];
    uint32_t pixels[SCENERY_MATERIAL_SLOTS][256];
};
typedef uint32_t (*SceneryMaterialSample)(void*, int, int, int);
static const uint32_t* sceneryMaterialTile(struct SceneryMaterialCache* cache,
        int id, SceneryMaterialSample sample, void* context) {
    for(unsigned i=0;i<cache->count;i++)
        if(cache->ids[i]==id)return cache->pixels[i];
    unsigned slot=cache->count<SCENERY_MATERIAL_SLOTS?cache->count++:cache->next;
    cache->next=(slot+1)%SCENERY_MATERIAL_SLOTS;cache->ids[slot]=id;
    for(int y=0;y<16;y++)for(int x=0;x<16;x++)
        cache->pixels[slot][y*16+x]=sample(context,id,x,y);
    return cache->pixels[slot];
}
