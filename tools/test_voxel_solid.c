#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "pk_wide_voxel.h"
#include "pk_wide_solid.h"
#include "pk_wide_props.h"
#include "pk_scenery_candidates.h"

int main(void) {
    const uint32_t expanded[]={0x63478921,0xb9465c5a,0xf2d16ebd,0x6c5ee1b2};
    for(unsigned i=0;i<sizeof(expanded)/sizeof(expanded[0]);i++) {
        assert(sceneryCandidate(expanded[i]));
        assert(solidPlantTileset(expanded[i],0x082d4bb4));
        assert(!solidPlantTileset(expanded[i],0x082d4a94));
    }
    assert(sceneryRadicalProps(0xf2d16ebd,0x082d4a94));
    assert(!sceneryRadicalProps(0xb9465c5a,0x082d4a94));
    assert(!sceneryKanto(0x63478921,0x082d4a94));
    assert(!sceneryCandidate(0x5e704d77)); // Matching art alone is not a mapped engine.
    assert(!sceneryCandidate(0));
    assert(!solidCutLeaf(0));
    assert(!solidCutLeaf(1|(1<<5)|(1<<10)));
    assert(!solidCutLeaf(20|(12<<5)|(6<<10)));
    assert(solidCutLeaf(8|(16<<5)|(12<<10)));
    assert(solidCutLeaf(4|(10<<5)|(10<<10)));

    assert(solidDrescoConifer(0x082d4a94,0x082d4af4,0x2f0,0x2f8));
    assert(solidDrescoConifer(0x082d4a94,0x082d4af4,0x2f2,0x2fa));
    assert(!solidDrescoConifer(0x082d4a94,0x082d4af4,0x2f1,0x2f9));
    assert(!solidDrescoConifer(0x082d4a94,0x082d4af0,0x2f2,0x2fa));
    assert(!solidDrescoConifer(0x082d4a94,0x082d4af4,0x2f2,0x2fb));
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
    for(int kind=1;kind<=10;kind++) {
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
    // A single bark texel must color the complete trunk, including faces
    // whose barycentric weights round just below an integer UV boundary.
    struct SolidProp palm={.kind=6};palm.surface.x=32;palm.surface.y=40;
    for(int i=0;i<32*48;i++)palm.surface.art[i]=0xff00ff00;
    palm.surface.art[43*32+15]=0xff0000ff;
    memset(depth,0,sizeof depth);memset(v.out,0,N*4);
    solidPropDraw(&v,&palm);
    int trunkPixels=0,wrongPixels=0;
    for(int y=voxelY(&v,49,2);y<voxelY(&v,49,0);y++)
      for(int x=voxelX(&v,40,49)-1;x<=voxelX(&v,40,49);x++) {
        uint32_t c=v.out[y*W+x];
        if(c&255)trunkPixels++;
        if(c&0xff00)wrongPixels++;
      }
    assert(trunkPixels>=3 && wrongPixels==0);
    // Snow-capped rocks must retain both the upper cap and lower stone art.
    struct SolidProp rock={.kind=3};rock.surface.x=32;rock.surface.y=40;
    for(int y=0;y<48;y++)for(int x=0;x<32;x++)
        rock.surface.art[y*32+x]=y>=27?0xff0000ff:0xff00ff00;
    memset(depth,0,sizeof depth);memset(v.out,0,N*4);
    solidPropDraw(&v,&rock);
    int stonePixels=0,capPixels=0;
    for(int i=0;i<N;i++) {
        if(v.out[i]&255)stonePixels++;
        if(v.out[i]&0xff00)capPixels++;
    }
    assert(stonePixels>10 && capPixels>10);
    assert(solidSnowRockId(0x24) && solidSnowRockId(0x53));
    assert(solidSnowRockId(0x159) && solidSnowRockId(0x15f));
    assert(!solidSnowRockId(0xe8) && !solidSnowRockId(0xf1));
    assert(!solidSnowRockId(0xfc) && !solidSnowRockId(0x158));
    for(unsigned profile=0;profile<sizeof(solidPlantProfiles)/sizeof(solidPlantProfiles[0]);profile++) {
        const struct SolidPlantProfile *model=&solidPlantProfiles[profile];
        assert(solidPlantProfile(model->rom,model->primary,model->top,model->bottom)==(int)profile);
        assert(solidPlantProfile(model->rom^1,model->primary,model->top,model->bottom)<0);
        assert(solidPlantProfile(model->rom,model->primary^4,model->top,model->bottom)<0);
        assert(solidPlantProfile(model->rom,model->primary,model->top,0xffff)<0);
        struct SolidProp plant={.kind=11,.plantProfile=(int)profile};
        plant.surface.x=32;plant.surface.y=24;plant.surface.rise=8;
        for(int i=0;i<6;i++)plant.surface.art[i]=0xff40c080;
        memset(depth,0,sizeof depth);memset(v.out,0,N*4);solidPropDraw(&v,&plant);
        int pixels=0;for(int i=0;i<N;i++)if(v.out[i])pixels++;
        assert(pixels>40&&pixels<1000);
        for(int y=-160;y<=160;y+=32)for(int x=-160;x<=160;x+=32) {
            plant.surface.x=x;plant.surface.y=y;solidPropDraw(&v,&plant);
            assert(guarded[0]==0x12345678 && guarded[N+1]==0x12345678);
        }
    }
    puts("Solid trees, props and all registered plant profiles: clipping, volume, winding and occlusion passed");
}
