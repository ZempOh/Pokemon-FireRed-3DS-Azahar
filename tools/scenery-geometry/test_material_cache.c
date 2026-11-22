#include <assert.h>
#include <stdio.h>
#include "scenery_material_cache.h"
struct Source { unsigned calls, frame; };
static uint32_t value(unsigned frame,int id,int x,int y) {
    return 0xA5000000u ^ (frame*7919u) ^ ((unsigned)id*257u) ^ (unsigned)(y*16+x);
}
static uint32_t sample(void* raw,int id,int x,int y) {
    struct Source* s=raw;s->calls++;return value(s->frame,id,x,y);
}
static void check(struct SceneryMaterialCache* c,struct Source* s,int id) {
    const uint32_t* tile=sceneryMaterialTile(c,id,sample,s);
    for(int y=0;y<16;y++)for(int x=0;x<16;x++)assert(tile[y*16+x]==value(s->frame,id,x,y));
}
int main(void) {
    struct SceneryMaterialCache c={0};struct Source s={0};
    for(int i=0;i<100;i++)check(&c,&s,8);
    assert(s.calls==256); /* 100 identical ground cells decoded only once. */
    for(int i=0;i<40;i++)check(&c,&s,i); /* Eviction never aliases another tile. */
    check(&c,&s,8);
    s.frame++;c.count=0;c.next=0;unsigned before=s.calls;
    check(&c,&s,8);assert(s.calls==before+256); /* Animated palette/VRAM refresh. */
    puts("Material cache: exact pixels, bounded eviction, frame invalidation and decode reduction passed");
    return 0;
}
