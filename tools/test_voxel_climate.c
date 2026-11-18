#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <stdio.h>
#include "pk_voxel_climate.h"
int main(void) {
    uint32_t foliage=0xff409040u, stone=0xff888888u;
    assert(climateTerrain(foliage)==foliage);
    for(int season=0;season<4;season++) {
        voxelClimate.season=season; voxelClimate.blend=256;
        assert(climateTerrain(stone)==stone);
        assert((climateTerrain(foliage)&0xff000000u)==0xff000000u);
    }
    voxelClimate.config=2|(3<<2)|(3<<4);
    voxelClimate.blend=256;
    climateUpdate(0,0); assert(voxelClimate.blend==0);
    voxelClimate.blend=256;
    climateUpdate(1,1); assert(voxelClimate.blend==0);
    uint32_t out[4]={1,2,3,4},depth[4]={UINT32_MAX,UINT32_MAX,UINT32_MAX,UINT32_MAX};
    voxelClimate.blend=256;
    for(int w=0;w<5;w++){voxelClimate.weather=w;climateAtmosphere(out,depth,2,2);}
    assert(out[0]==1 && out[1]==2 && out[2]==3 && out[3]==4);
    puts("climate: original identity, foliage mask, alpha, indoor/native weather and UI protection passed");
}
