/* Cosmetic climate. Settings live in each title's own settings.txt. */
#ifndef VOXEL_CLIMATE_H
#define VOXEL_CLIMATE_H
#include <time.h>
static float sClimateMix;
static int sClimateSeason, sClimateWeather;
static uint64_t sClimateTick;
static void ClimateUpdate(bool eligible) {
    uint64_t now=svcGetSystemTick();
    float dt=sClimateTick ? (float)(now-sClimateTick)/SYSCLOCK_ARM11 : 0.0f;
    sClimateTick=now;
    if(dt>0.1f) dt=0.1f;
    int mode=CtrSettings_GetInt("visual_climate",0);
    int season=CtrSettings_GetInt("visual_season",0);
    int weather=CtrSettings_GetInt("visual_weather",0);
    if(mode==1) {
        time_t t=time(NULL); struct tm *tm=gmtime(&t);
        if(tm) { season=((tm->tm_mon+10)%12)/3; weather=tm->tm_yday%5?1:season==3?3:2; }
    }
    if(season<0 || season>3) season=0;
    if(weather<0 || weather>4) weather=0;
    eligible=eligible && (mode==1 || mode==2);
    if(!eligible || season!=sClimateSeason || weather!=sClimateWeather) {
        sClimateMix-=dt;
        if(sClimateMix<=0) { sClimateMix=0; sClimateSeason=season; sClimateWeather=weather; }
    } else {
        sClimateMix+=dt;
        if(sClimateMix>1) sClimateMix=1;
    }
    if(!eligible) sClimateMix=0;
}
static VoxelLight ClimateLight(VoxelLight light, bool eligible) {
    ClimateUpdate(eligible);
    if(sClimateMix<=0) return light;
    static const float tints[4][3]={{1.02f,1.03f,0.98f},{1,1,1},{1.08f,0.94f,0.83f},{0.91f,0.98f,1.08f}};
    for(int i=0;i<3;i++) {
        float scale=1+(tints[sClimateSeason][i]-1)*sClimateMix;
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
