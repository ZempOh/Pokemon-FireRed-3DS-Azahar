#pragma once
#ifdef __ANDROID__
#include <time.h>
#include <android/log.h>
static double sceneryFrameNow(void) {
    struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
    return t.tv_sec*1000.0+t.tv_nsec/1000000.0;
}
static double sceneryFrameTimes[8];
static unsigned sceneryFrameCount;
#define SCENERY_FRAME_MARK(name) double name=sceneryFrameNow()
#define SCENERY_FRAME_ADD(stage,start,end) (sceneryFrameTimes[stage]+=(end)-(start))
static void sceneryFrameReport(int w,int h,int trees,int props,int buildings) {
    if(++sceneryFrameCount<300)return;
    __android_log_print(ANDROID_LOG_INFO,"pokedaisy",
        "scenery cost ms source=%.3f buildings=%.3f climate=%.3f prepare=%.3f terrain=%.3f geometry=%.3f objects=%.3f atmosphere=%.3f view=%dx%d models=%d/%d/%d",
        sceneryFrameTimes[0]/300,sceneryFrameTimes[1]/300,sceneryFrameTimes[2]/300,sceneryFrameTimes[3]/300,
        sceneryFrameTimes[4]/300,sceneryFrameTimes[5]/300,sceneryFrameTimes[6]/300,sceneryFrameTimes[7]/300,
        w,h,trees,props,buildings);
    for(int i=0;i<8;i++)sceneryFrameTimes[i]=0;
    sceneryFrameCount=0;
}
#else
#define SCENERY_FRAME_MARK(name) ((void)0)
#define SCENERY_FRAME_ADD(stage,start,end) ((void)0)
#define sceneryFrameReport(w,h,trees,props,buildings) ((void)0)
#endif
