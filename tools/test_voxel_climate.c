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
#include "pk_scenery_candidates.h"
#undef time
#undef clock_gettime
int main(void) {
    /* Same type-zero engine metadata, different scene semantics. Route 16
     * must keep winter on crossing from Celadon; an actual room must clear it. */
    voxelClimate.config=62;
    fakeMs=5000;
    climateUpdate(sceneryOutdoor(0xcec21496,1,6,0),0,0);
    fakeMs+=5000;
    climateUpdate(sceneryOutdoor(0xcec21496,1,26,0),0,0);
    assert(voxelClimate.seasonBlend>0 && voxelClimate.season==3);
    fakeMs+=5000;
    climateUpdate(sceneryOutdoor(0xcec21496,13,83,0),0,0);
    assert(voxelClimate.seasonBlend==0 && voxelClimate.blend==0);
    assert(!sceneryOutdoor(0xcec21496,55,5,0)); /* Ice cave. */
    assert(!sceneryOutdoor(0xcec21497,1,26,0)); /* Unreviewed ROM. */
    assert(!sceneryOutdoor(0xcec21496,1,26,8)); /* Explicit indoor metadata wins. */
    memset(&voxelClimate,0,sizeof(voxelClimate));fakeMs=0;
    for(unsigned i=0;i<sizeof(sceneryGrassEffects)/sizeof(sceneryGrassEffects[0]);i++) {
        const struct SceneryGrassEffect *p=&sceneryGrassEffects[i];
        assert(climateGrassEffect(p->rom,p->template,p->images));
        assert(!climateGrassEffect(p->rom^1,p->template,p->images));
        assert(!climateGrassEffect(p->rom,p->template+4,p->images));
        assert(!climateGrassEffect(p->rom,p->template,p->images+4));
    }
    assert(climateGrassEffect(0xf2d16ebd,0x083a5e38,0x083a5e18)); /* Rocket short grass. */
    assert(!climateGrassEffect(0x63478921,0x083a593c,0x083a58f8)); /* Ash replacement art held. */
    assert(!climateGrassEffect(0x63478921,0x083a5e38,0x083a5e18));
    const uint32_t profiles[]={0x25c3d89f,0xfba55dd8,0x4b3d4957};
    for(int i=0;i<3;i++) {
        assert(climateGrassEffect(profiles[i],0x083a5420,0x083a53dc));
        assert(climateGrassEffect(profiles[i],0x083a5e38,0x083a5e18));
        assert(!climateGrassEffect(profiles[i],0x083a5420,0x08eb3810));
        assert(!climateGrassEffect(profiles[i],0x03007d6c,0x083a53dc));
    }
    assert(!climateGrassEffect(0,0x083a5420,0x083a53dc));
    uint32_t tealLeaf=0xff606800u;
    voxelClimate.season=3;voxelClimate.seasonBlend=256;
    /* Exact77: Classic day-colored ground passed, then native night colors
     * escaped hue recognition above mailboxes and beside partial trees. */
    const uint16_t *classicMailbox=scenerySecondaryLandMask(0xe4deb9be,0x084ad600,0x084add10,0x2a5);
    assert(classicMailbox && (classicMailbox[0]&1) && !(classicMailbox[15]&(1u<<8)));
    assert(!scenerySecondaryLandMask(0xe4deb9bf,0x084ad600,0x084add10,0x2a5));
    assert(!scenerySecondaryLandMask(0xe4deb9be,0x084ad600,0x084add14,0x2a5));
    const uint32_t classicGroundColors[]={0xff88c478u,0xff554c34u,0xff604028u};
    for(unsigned i=0;i<sizeof(classicGroundColors)/sizeof(classicGroundColors[0]);i++) {
        uint32_t ink=classicGroundColors[i];
        assert(climateGround(ink,2)!=ink);
        assert((climateGround(ink,2)&0xff000000u)==(ink&0xff000000u));
    }
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
    assert(climateGround(0xff554c34u,2)!=0xff554c34u); /* verified night grass */
    assert(climateGround(0xff554c34u,0)==0xff554c34u); /* same hue outside land profile */
    assert(climateGround(0xffcc7733u,1)==0xffcc7733u); /* water */
    assert(climateGround(0xff4488bbu,1)!=0xff4488bbu); /* earth */
    assert(climateGround(0xff4488bbu,0)==0xff4488bbu); /* wall */
    /* Frozen Heights: never whiten already snowy, night-lit tree ground a
     * second time. The same colors must still whiten on reviewed bare land. */
    const uint32_t nativeSnow[]={0xffb09592u,0xffd0a8a0u,0xffeeddddu,0x7f887760u};
    for(unsigned i=0;i<sizeof(nativeSnow)/sizeof(nativeSnow[0]);i++) {
        assert(climateGround(nativeSnow[i],2)!=nativeSnow[i]);
        for(int season=0;season<4;season++) {
            voxelClimate.season=season;
            for(unsigned blend=0;blend<=256;blend+=32) {
                voxelClimate.seasonBlend=blend;
                assert(climateGround(nativeSnow[i],CLIMATE_GROUND_NATIVE_SNOW)==nativeSnow[i]);
            }
        }
        voxelClimate.season=3;voxelClimate.seasonBlend=256;
    }
    for(unsigned a=0;a<256;a++)assert((climateGround((a<<24)|0x409040,1)>>24)==a);
    voxelClimate.seasonBlend=0;assert(climateGround(foliage,1)==foliage);
    voxelClimate.config=2|(3<<2)|(3<<4);
    voxelClimate.blend=256;
    climateUpdate(0,0,0); assert(voxelClimate.blend==0);
    voxelClimate.blend=256;
    voxelClimate.season=3; voxelClimate.weather=3;
    climateUpdate(1,1,0); assert(voxelClimate.blend==256);
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
    for(int i=0;i<200;i++){fakeMs+=100;climateUpdate(1,0,0);}
    assert(voxelClimate.season==2 && voxelClimate.weather==1 && voxelClimate.seasonBlend==256);
    uint32_t autumn=climateTerrain(foliage);
    fakeSeconds++;
    for(int i=0;i<200;i++) {
        fakeMs+=100;climateUpdate(1,0,0);
        assert(climateTerrain(foliage)==autumn && voxelClimate.seasonBlend==256);
    }
    assert(voxelClimate.weather==4 && voxelClimate.blend==256);
    // FireRed preview samples civil time directly, including on first outdoor frame.
    struct tm boundary = {.tm_mon=11, .tm_mday=1};
    assert(climateCalendarPhase(&boundary)==256);
    boundary.tm_mday=8;
    assert(climateCalendarPhase(&boundary)==128);
    boundary.tm_mday=15;
    assert(climateCalendarPhase(&boundary)==0);
    boundary.tm_hour=23;
    assert(climateCalendarPhase(&boundary)==0);
    boundary.tm_mon=0; boundary.tm_mday=1;
    assert(climateCalendarPhase(&boundary)==0);
    climateUpdate(1,0,1);
    assert(voxelClimate.seasonBlend==256);
    uint32_t liveColor=climateGround(foliage,2);
    climateUpdate(0,0,1);
    assert(voxelClimate.seasonBlend==0 && voxelClimate.blend==0);
    fakeMs+=60000;
    climateUpdate(1,0,1);
    assert(voxelClimate.seasonBlend==256 && climateGround(foliage,2)==liveColor);
    puts("climate: original identity, foliage mask, alpha, indoor/native weather and UI protection passed");
}
