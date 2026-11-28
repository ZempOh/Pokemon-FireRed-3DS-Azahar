#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "pk_wide_voxel.h"

static void testActorDepth(void) {
    uint32_t frame[64] = {0}, actorDepth[64] = {0};
    struct VoxelView view = {.out=frame,.depth=actorDepth,.width=8,.height=8,.top=-16};
    const uint32_t ink = 0xff82aed4u, nearer = 0xff444444u;
    voxelActorPixel(&view,4,5,6,1,ink);
    assert(frame[5*8+4]==ink);
    assert(frame[2*8+3]==voxelShade(ink,175));
    assert(frame[3*8+3]==voxelShade(ink,175));
    assert(frame[4*8+4]==voxelShade(ink,213));

    voxelActorPixel(&view,4,5,6,0,nearer);
    assert(frame[5*8+4]==nearer);
    voxelActorPixel(&view,4,6,6,2,ink);
    assert(frame[5*8+4]==nearer); // the second sprite's top cannot erase a front face
    voxelPixel(&view,3,2,5,nearer);
    voxelActorPixel(&view,4,5,6,0,ink);
    assert(frame[2*8+3]==nearer); // scenery in front of the rear surface still occludes it
    assert(frame[5*8+4]==ink);

    memset(frame,0,sizeof(frame));
    memset(actorDepth,0,sizeof(actorDepth));
    voxelActorPixel(&view,0,0,6,0,ink);
    assert(frame[0]==ink);
    for (unsigned i=1;i<64;i++) assert(frame[i]==0);
}

int main(void) {
    // Exact76 Thor right-stick pan: ceil(right)-floor(left) is 481,
    // although the selected zoom spans 480 pixels. Exercise runtime guard.
    assert(voxelViewportFits(480,270));
    assert(voxelViewportFits(481,271));
    assert(voxelViewportFits(481,401));
    assert(!voxelViewportFits(482,271));
    assert(!voxelViewportFits(480,402));
    assert(!voxelViewportFits(119,80));
    assert(!voxelViewportFits(120,79));
    // Exact72 Thor: the 480x271 Lazarus view needs more than 800 source pixels.
    struct VoxelSourceWindow wide = voxelSourceWindow(0,0,0,0,480,271,144);
    assert(wide.right-wide.left > 800);
    assert(wide.right-wide.left <= VOXEL_SOURCE_MAX);
    // Exercise the actual runtime window calculation over every tile alignment,
    // both camera directions, and the largest supported projected viewport.
    for(int x=-16;x<16;x++) for(int y=-16;y<16;y++) {
        struct VoxelSourceWindow s=voxelSourceWindow(13,7,x,y,VOXEL_MAX_W,VOXEL_MAX_H,144);
        assert(s.right-s.left <= VOXEL_SOURCE_MAX && s.bottom-s.top <= VOXEL_SOURCE_MAX);
        assert(s.left<=x-144 && s.top<=y-144);
        assert(s.right>=x+VOXEL_MAX_W+144 && s.bottom>=y+VOXEL_MAX_H+144);
        assert((s.left+13)%16==0 && (s.top+7)%16==0);
        assert((s.right-s.left)%16==0 && (s.bottom-s.top)%16==0);
    }
    uint32_t out[4]={0}, depth[4]={0};
    struct VoxelView v={.out=out,.depth=depth,.width=2,.height=2,.top=-16};
    assert(voxelFloor(-1,16)==-1 && voxelFloor(-16,16)==-1 && voxelFloor(-17,16)==-2);
    voxelPixel(&v,0,0,4,1);
    voxelSpritePixel(&v,0,0,4,0,2);
    voxelSpritePixel(&v,0,0,4,1,3);
    assert(out[0]==2); // first OAM entry wins the tie
    voxelSpritePixel(&v,0,0,5,20,4); assert(out[0]==4); // closer foot wins
    voxelSpritePixel(&v,0,0,3,0,5); assert(out[0]==4); // rear sprite stays behind
    voxelPixel(&v,0,0,6,6); assert(out[0]==6); // nearer terrain occludes
    voxelSpritePixel(&v,-1,0,99,0,8); assert(out[0]==6);
    testActorDepth();
    puts("voxel projection depth tests passed");
}
