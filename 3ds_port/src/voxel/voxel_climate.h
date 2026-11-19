/* Cosmetic climate. Settings live in each title's own settings.txt. */
#ifndef VOXEL_CLIMATE_H
#define VOXEL_CLIMATE_H
#include <time.h>
#include <stdint.h>
/* Stable pseudo-random fronts change on real-clock 15-minute boundaries.
 * Reloading a map does not reroll weather. Seasons weight precipitation;
 * consecutive equal fronts naturally last longer. No gameplay RNG is used. */
static int climateWeatherAt(time_t seconds, int season) {
    if (seconds < 0) return 1;
    uint32_t x=(uint32_t)((uint64_t)seconds/900u) ^ 0x6d2b79f5u;
    x ^= x >> 16; x *= 0x7feb352du; x ^= x >> 15;
    x *= 0x846ca68bu; x ^= x >> 16;
    unsigned roll=x%100u;
    static const unsigned clear[4]={50,70,45,45};
    if (season<0 || season>3) season=0;
    if (roll<clear[season]) return 1;
    if (roll>=90) return 4;
    return season==3 ? 3 : 2;
}

static float sClimateMix, sClimateSeasonMix;
static int sClimateSeason, sClimateWeather;
static uint64_t sClimateTick;
static uint64_t sClimateClockTick;
static int sClimateClockSeason, sClimateClockWeather;
static void ClimateUpdate(bool eligible) {
    uint64_t now=svcGetSystemTick();
    float dt=sClimateTick ? (float)(now-sClimateTick)/SYSCLOCK_ARM11 : 0.0f;
    sClimateTick=now;
    if(dt>0.1f) dt=0.1f;
    int mode=CtrSettings_GetInt("visual_climate",0);
    int season=CtrSettings_GetInt("visual_season",0);
    int weather=CtrSettings_GetInt("visual_weather",0);
    if(mode==1) {
        /* The calendar and 15-minute fronts do not need per-frame conversion.
         * Poll once a second; animation still advances every frame. */
        if(!sClimateClockTick || now-sClimateClockTick >= SYSCLOCK_ARM11) {
            time_t t=time(NULL); struct tm *tm=gmtime(&t);
            if(tm) {
                sClimateClockSeason=((tm->tm_mon+10)%12)/3;
                sClimateClockWeather=climateWeatherAt(t,sClimateClockSeason);
            }
            sClimateClockTick=now;
        }
        season=sClimateClockSeason; weather=sClimateClockWeather;
    } else sClimateClockTick=0;
    if(mode==1) dt/=8.0f; /* Eight-second automatic fades. */
    if(season<0 || season>3) season=0;
    if(weather<0 || weather>4) weather=0;
    eligible=eligible && (mode==1 || mode==2);
    /* Weather fronts must not fade the calendar's foliage back to summer. */
    if(!eligible || season!=sClimateSeason) {
        sClimateSeasonMix-=dt;
        if(sClimateSeasonMix<=0) { sClimateSeasonMix=0; sClimateSeason=season; }
    } else {
        sClimateSeasonMix+=dt;
        if(sClimateSeasonMix>1) sClimateSeasonMix=1;
    }
    if(!eligible || weather!=sClimateWeather) {
        sClimateMix-=dt;
        if(sClimateMix<=0) { sClimateMix=0; sClimateWeather=weather; }
    } else {
        sClimateMix+=dt;
        if(sClimateMix>1) sClimateMix=1;
    }
    if(!eligible) sClimateMix=sClimateSeasonMix=0;
}
static VoxelLight ClimateLight(VoxelLight light, bool eligible) {
    ClimateUpdate(eligible);
    if(sClimateMix<=0 && sClimateSeasonMix<=0) return light;
    static const float tints[4][3]={{1.02f,1.03f,0.98f},{1,1,1},{1.08f,0.94f,0.83f},{0.91f,0.98f,1.08f}};
    for(int i=0;i<3;i++) {
        float scale=1+(tints[sClimateSeason][i]-1)*sClimateSeasonMix;
        light.sun[i]*=scale; light.shade[i]*=scale;
    }
    if(sClimateWeather==4) {
        light.haze+=(0.60f-light.haze)*sClimateMix;
        light.hazeRgb[0]=0.80f; light.hazeRgb[1]=0.84f; light.hazeRgb[2]=0.88f;
        light.rays*=1-sClimateMix;
    }
    if(sClimateWeather==2 || sClimateWeather==3) {
        light.motes=0.95f*sClimateMix;
        light.rays*=1-sClimateMix;
        light.bloom*=1-sClimateMix;
    }
    return light;
}
#endif
