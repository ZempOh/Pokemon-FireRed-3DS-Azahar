#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "pk_wide_voxel.h"
#include "pk_wide_solid.h"
#include "pk_wide_props.h"

int main(void) {
    enum { W=96,H=96,N=W*H };
    uint32_t guarded[N+2],depth[N],first[N];
    guarded[0]=guarded[N+1]=0x12345678;
    memset(guarded+1,0,N*4);memset(depth,0,sizeof depth);
    struct VoxelView v={.out=guarded+1,.depth=depth,.width=W,.height=H,.centreX=48,.centreY=48,.top=-64};
    struct SolidTree t={.x=32,.y=16,.rise=8};
    for(int i=0;i<32*48;i++)t.art[i]=0xff88cc44;
    solidTreeDraw(&v,&t);
    int count=0,at=-1;
    for(int i=0;i<N;i++) if(depth[i]) {count++;at=i;}
    assert(count>300 && count<2000 && at>=0);
    memcpy(first,v.out,sizeof first);
    // The original sprite's foot controls visibility behind and in front of the crown.
    uint32_t treeColor=v.out[at];
    voxelSpritePixel(&v,at%W,at/W,-63,0,0xff112233);
    assert(v.out[at]==treeColor);
    voxelSpritePixel(&v,at%W,at/W,200,0,0xff112233);
    assert(v.out[at]==0xff112233);
    // Geometry clips safely on all viewport sides, including entirely offscreen trees.
    for(int y=-160;y<=160;y+=32)for(int x=-160;x<=160;x+=32) {
        t.x=x;t.y=y;solidTreeDraw(&v,&t);
        assert(guarded[0]==0x12345678 && guarded[N+1]==0x12345678);
    }
    // Front-to-back and back-to-front triangles have identical coverage.
    struct SolidVertex a={30,40,8,8,8},b={60,40,8,24,8},c={48,60,32,16,24};
    memset(depth,0,sizeof depth);memset(v.out,0,N*4);
    solidTriangle(&v,&t,a,b,c,256,0);memcpy(first,v.out,sizeof first);
    memset(depth,0,sizeof depth);memset(v.out,0,N*4);
    solidTriangle(&v,&t,a,c,b,256,0);
    assert(memcmp(first,v.out,sizeof first)==0);
    for(int kind=1;kind<=6;kind++) {
        struct SolidProp p={.surface=t,.kind=kind};
        p.surface.x=32;p.surface.y=40;
        memset(depth,0,sizeof depth);memset(v.out,0,N*4);
        solidPropDraw(&v,&p);
        int raised=0;
        for(int y=0;y<voxelY(&v,49,8);y++)for(int x=0;x<W;x++)if(v.out[y*W+x])raised++;
        assert(raised>12); // each category has geometry above its footprint
        for(int y=-160;y<=160;y+=32)for(int x=-160;x<=160;x+=32) {
            p.surface.x=x;p.surface.y=y;solidPropDraw(&v,&p);
            assert(guarded[0]==0x12345678 && guarded[N+1]==0x12345678);
        }
    }
    puts("Solid trees and field props: clipping, volume, winding and occlusion passed");
}
