#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <stdio.h>
#include <stdint.h>
#include <time.h>
static uint64_t fakeMs;
static time_t fakeSeconds=1795114799;
static int fakeGetTime(int clock,struct timespec *ts) {
    (void)clock;ts->tv_sec=fakeMs/1000;ts->tv_nsec=(fakeMs%1000)*1000000;return 0;
}
static time_t fakeTime(time_t *out) { if(out)*out=fakeSeconds;return fakeSeconds; }
#define clock_gettime fakeGetTime
#define time fakeTime
#include "pk_voxel_climate.h"
#undef time
#undef clock_gettime
int main(void) {
    uint32_t tealLeaf=0xff606800u;
    voxelClimate.season=3;voxelClimate.seasonBlend=256;
    assert(climateTerrain(tealLeaf)==tealLeaf); // Generic terrain keeps its water protection.
    assert(climateLeafColor(tealLeaf)!=tealLeaf); // Known conifer foliage includes dark teal.
    assert((climateLeafColor(tealLeaf)&0xff000000u)==(tealLeaf&0xff000000u));
    voxelClimate.seasonBlend=0;
    assert(climateLeafColor(tealLeaf)==tealLeaf);
    assert(climateKantoPath(0xdc) && climateKantoPath(0x105));
    assert(climateKantoPath(0xd0) && climateKantoPath(0xd9) && climateKantoPath(0xe2));
    assert(climateKantoPath(0xc1) && climateKantoPath(0xfe) && climateKantoPath(0x107));
    assert(!climateKantoPath(0xde) && !climateKantoPath(0xdf));
    assert(!climateKantoPath(0x95) && !climateKantoPath(0x200));
    for(int season=0;season<4;season++) {
        int counts[5]={0};
        for(int slot=0;slot<10000;slot++) {
            time_t t=(time_t)slot*900;
            int w=climateWeatherAt(t,season);
            assert(w==climateWeatherAt(t+899,season));
            assert(w==1 || w==4 || w==(season==3?3:2));
            counts[w]++;
        }
        assert(counts[1]>3500 && counts[4]>700 && counts[4]<1300);
        assert(counts[season==3?3:2]>1500);
    }

    uint32_t foliage=0xff409040u, stone=0xff888888u;
    assert(climateTerrain(foliage)==foliage);
    uint32_t colors[4];
    for(int season=0;season<4;season++) {
        voxelClimate.season=season; voxelClimate.blend=voxelClimate.seasonBlend=256;
        assert(climateTerrain(stone)==stone);
        assert((climateTerrain(foliage)&0xff000000u)==0xff000000u);
        colors[season]=climateTerrain(foliage);
        for(int i=0;i<season;i++)assert(colors[i]!=colors[season]);
    }
    voxelClimate.season=3;voxelClimate.seasonBlend=256;
    assert(climateGround(foliage,0)!=foliage);
    assert(climateGround(stone,1)==stone);
    assert(climateGround(0xffcc7733u,1)==0xffcc7733u); /* water */
    assert(climateGround(0xff4488bbu,1)!=0xff4488bbu); /* earth */
    assert(climateGround(0xff4488bbu,0)==0xff4488bbu); /* wall */
    for(unsigned a=0;a<256;a++)assert((climateGround((a<<24)|0x409040,1)>>24)==a);
    voxelClimate.seasonBlend=0;assert(climateGround(foliage,1)==foliage);
    voxelClimate.config=2|(3<<2)|(3<<4);
    voxelClimate.blend=256;
    climateUpdate(0,0); assert(voxelClimate.blend==0);
    voxelClimate.blend=256;
    voxelClimate.season=3; voxelClimate.weather=3;
    climateUpdate(1,1); assert(voxelClimate.blend==256);
    /* Native weather retains foliage season but owns precipitation. */
    uint32_t native[4]={1,2,3,4},ground[4]={0,0,0,0};
    climateAtmosphere(native,ground,2,2);
    assert(native[0]==1 && native[1]==2 && native[2]==3 && native[3]==4);
    voxelClimate.nativeWeather=0;
    climateAtmosphere(native,ground,2,2);
    assert(native[0]!=1 || native[1]!=2 || native[2]!=3 || native[3]!=4);
    uint32_t out[4]={1,2,3,4},depth[4]={UINT32_MAX,UINT32_MAX,UINT32_MAX,UINT32_MAX};
    voxelClimate.blend=256;
    for(int w=0;w<5;w++){voxelClimate.weather=w;climateAtmosphere(out,depth,2,2);}
    assert(out[0]==1 && out[1]==2 && out[2]==3 && out[3]==4);
    memset(&voxelClimate,0,sizeof voxelClimate);voxelClimate.config=1;
    for(int i=0;i<200;i++){fakeMs+=100;climateUpdate(1,0);}
    assert(voxelClimate.season==2 && voxelClimate.weather==1 && voxelClimate.seasonBlend==256);
    uint32_t autumn=climateTerrain(foliage);
    fakeSeconds++;
    for(int i=0;i<200;i++) {
        fakeMs+=100;climateUpdate(1,0);
        assert(climateTerrain(foliage)==autumn && voxelClimate.seasonBlend==256);
    }
    assert(voxelClimate.weather==4 && voxelClimate.blend==256);
    puts("climate: original identity, foliage mask, alpha, indoor/native weather and UI protection passed");
}
