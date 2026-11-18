#include <assert.h>
#include <stdio.h>
#include "pk_wide_voxel.h"
int main(void) {
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
    puts("voxel projection depth tests passed");
}
