#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <stdio.h>
#define SYSCLOCK_ARM11 1000
static uint64_t ticks;
static int mode, season, weather;
static uint64_t svcGetSystemTick(void) { return ticks; }
static int CtrSettings_GetInt(const char *key,int fallback) {
    if(!strcmp(key,"visual_climate")) return mode;
    if(!strcmp(key,"visual_season")) return season;
    if(!strcmp(key,"visual_weather")) return weather;
    return fallback;
}
typedef struct {float sun[3],shade[3],haze,dappleLow,dappleHigh,rays,bloom,motes,hazeRgb[3],hazeStart,hazeRamp;} VoxelLight;
#include <time.h>
static int clockReads;
static time_t clockValue=1795094400;
static time_t testClock(time_t *dest) {
    time_t value=clockValue; /* Stable November clock for the polling test. */
    clockReads++;
    if(dest)*dest=value;
    return value;
}
#define time testClock
#include "voxel_climate.h"
#undef time
int main(void) {
    for(int s=0;s<4;s++) {
        int counts[5]={0};
        for(int slot=0;slot<10000;slot++) {
            time_t t=(time_t)slot*900;
            int w=climateWeatherAt(t,s);
            assert(w==climateWeatherAt(t+899,s));
            assert(w==1 || w==4 || w==(s==3?3:2));
            counts[w]++;
        }
        assert(counts[1]>3500 && counts[4]>700 && counts[4]<1300);
        assert(counts[s==3?3:2]>1500);
    }

    VoxelLight original={.sun={1,1,1},.shade={1,1,1},.haze=.1f,.motes=.5f};
    VoxelLight out=ClimateLight(original,true);
    assert(memcmp(&out,&original,sizeof out)==0);
    mode=2; season=2; weather=2;
    for(int i=0;i<30;i++){ticks+=100;out=ClimateLight(original,true);}
    assert(sClimateMix==1 && out.sun[0]>1 && out.sun[2]<1 && out.motes>0);
    out=ClimateLight(original,false);
    assert(sClimateMix==0 && memcmp(&out,&original,sizeof out)==0);
    for(season=0;season<4;season++) for(weather=0;weather<5;weather++) {
        for(int i=0;i<30;i++){ticks+=100;out=ClimateLight(original,true);}
        assert(sClimateSeason==season && sClimateWeather==weather && sClimateMix==1);
        for(int j=0;j<3;j++) assert(isfinite(out.sun[j]) && out.sun[j]>.8f && out.sun[j]<1.2f);
    }
    mode=1; clockReads=0;
    for(int i=0;i<200;i++){ticks+=100;out=ClimateLight(original,true);}
    assert(clockReads==20 && sClimateSeason==2 && sClimateMix==1);
    /* A real 15-minute weather boundary retains every season-tint frame. */
    clockValue=1795114799; /* 2026-11-19 18:59:59 UTC: clear autumn. */
    for(int i=0;i<200;i++){ticks+=100;out=ClimateLight(original,true);}
    assert(sClimateSeason==2 && sClimateWeather==1 && sClimateSeasonMix==1);
    float autumn=out.sun[0];
    clockValue++;
    for(int i=0;i<200;i++) {
        ticks+=100;out=ClimateLight(original,true);
        assert(sClimateSeasonMix==1 && out.sun[0]==autumn);
    }
    assert(sClimateWeather==4 && sClimateMix==1);
    mode=0; out=ClimateLight(original,true); assert(memcmp(&out,&original,sizeof out)==0);
    puts("climate: original identity, all presets, indoor suppression passed");
}
