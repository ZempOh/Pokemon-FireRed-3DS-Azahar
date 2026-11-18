#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "compat/port_prof.h"

typedef uint32_t u32;
typedef struct { void *data; unsigned size; } C3D_Tex;
typedef struct { C3D_Tex *tex; const void *sub; } C2D_Image;
#define CTR_VOXEL_ENABLED 1
#define CTR_SOFT_WIDTH 240
#define CTR_SOFT_HEIGHT 160
#define TEX_DIM 512
#define UP 2
#define UP_W 480
#define UP_H 320
#define DRAW_SCALE 0.75f
#define SYSCLOCK_ARM11 1000000
#define C3D_FRAME_SYNCDRAW 1
#define GPUREG_TEXUNIT_CONFIG 1
#define GPU_FRAGOPMODE_GL 1
#define GPU_ALWAYS 1
#define GPU_GREATER 1
#define GPU_BLEND_ADD 1
#define GPU_SRC_ALPHA 1
#define GPU_ONE_MINUS_SRC_ALPHA 1
#define CTR_LOG_VIDEO 1
#define GX_BUFFER_DIM(w,h) (((w)<<16)|(h))
#define TILE_TRANSFER_FLAGS 1
#define UI_TRANSFER_FLAGS 2

static uint16_t frame[240*160], uiPixels[240*160], alternateUi[240*160];
static const uint16_t *sFrame=frame, *sUi;
static uint16_t sLut[32768], sUploadedFrame[240*160], sUploadedUi[240*160];
static uint16_t sLastUi[240*160], sHoldUi[240*160];
static uint16_t sLinear[512*512], sUiLinear[512*512], frameTexels[512*512], uiTexels[512*512];
static C3D_Tex sFrameTex={frameTexels,sizeof(frameTexels)}, sUiTex={uiTexels,sizeof(uiTexels)};
static C3D_Tex sSurface, sHoldTex;
static int sFrameSub, sLogicalSub, sTop, sLogical;
static bool sFrameUploaded, sUiUploaded, sVoxelReady=true, sClean, sHold, sBanner;
static bool sHoldReady, sHoldValid, sSurfaceClean, sDrewVoxel, sFrameDrawn=true;
static uint32_t sUiRevision, sLastUiRevision;
static unsigned sVoxelUploads;
static float sPicX, sPicScaleX=1.5f;
static struct { bool on, sliding; float shakeX, shakeY; } sBattle;
static struct { float waitMs, cpuMs; } sStats;
static bool available, updateOk=true, warmingUp, inBattle;
static bool inFrame, failBegin, invalidated, drawn;
static unsigned transfers, begins, ends, pendingCount;
static unsigned uiFlushCalls, uiFlushedBytes;
static bool uiFlushedRows[160];
static uint64_t tick;
static struct { const uint16_t *source; uint16_t *dest; uint16_t snapshot[512*512]; } pending[2];

static uint64_t svcGetSystemTick(void) { return ++tick; }
uint32_t Port_ProfTick(void) { return (uint32_t)svcGetSystemTick(); }
void Port_ProfAdd(unsigned section, uint32_t start) { (void)section; (void)start; }
static void PlacePicture(void) {}
static void GSPGPU_FlushDataCache(const void *p, unsigned size) {
    uintptr_t address=(uintptr_t)p, first=(uintptr_t)sUiLinear;
    assert(inFrame);
    if (address>=first && address<first+sizeof(sUiLinear)) {
        unsigned rowBytes=UP*TEX_DIM*sizeof(uint16_t), offset=(unsigned)(address-first);
        assert(offset%rowBytes==0 && size%rowBytes==0 && size>0);
        assert(offset+size<=UP_H*TEX_DIM*sizeof(uint16_t));
        for (unsigned y=offset/rowBytes;y<(offset+size)/rowBytes;++y) {
            assert(!uiFlushedRows[y]); uiFlushedRows[y]=true;
        }
        ++uiFlushCalls; uiFlushedBytes+=size;
    }
}
static bool C3D_FrameBegin(unsigned flags) {
    assert(flags==C3D_FRAME_SYNCDRAW && !inFrame);
    ++begins;
    if (failBegin) return false;
    /* Prior commands still hold their original source buffer until here. */
    for (unsigned i=0;i<pendingCount;++i) {
        assert(!memcmp(pending[i].source,pending[i].snapshot,sizeof(pending[i].snapshot)));
        memcpy(pending[i].dest,pending[i].source,sizeof(pending[i].snapshot));
    }
    pendingCount=0; invalidated=drawn=false; inFrame=true;
    uiFlushCalls=uiFlushedBytes=0; memset(uiFlushedRows,0,sizeof(uiFlushedRows));
    return true;
}
static void C3D_SyncDisplayTransfer(u32 *src,u32 inDim,u32 *dst,u32 outDim,u32 flags) {
    assert(inFrame && !drawn && pendingCount<2);
    assert(inDim==GX_BUFFER_DIM(512,512) && outDim==inDim);
    assert(flags==TILE_TRANSFER_FLAGS || flags==UI_TRANSFER_FLAGS);
    pending[pendingCount].source=(uint16_t *)src;
    pending[pendingCount].dest=(uint16_t *)dst;
    memcpy(pending[pendingCount].snapshot,src,sizeof(pending[0].snapshot));
    ++pendingCount; ++transfers;
}
static void C3D_SyncTextureCopy(u32 *s,unsigned a,u32 *d,unsigned b,unsigned size,unsigned f) {
    (void)s;(void)a;(void)d;(void)b;(void)size;(void)f; assert(inFrame && !drawn);
}
static void GPUCMD_AddMaskedWrite(unsigned reg,unsigned mask,unsigned value) {
    assert(inFrame && reg==GPUREG_TEXUNIT_CONFIG && mask==4 && value==(1u<<16)); invalidated=true;
}
static void C3D_FrameEnd(unsigned flags) { assert(inFrame && !flags); inFrame=false; ++ends; }
static bool CtrVoxel_IsAvailableForBattle(void) { return available; }
static bool CtrVoxel_IsAvailable(void) { return available; }
static bool CtrVoxel_InBattle(void) { return inBattle; }
static void CtrVoxel_BeginBattle(void) { inBattle=true; }
static void CtrVoxel_SetBattleFrame(bool a,float b,float c) { (void)a;(void)b;(void)c; }
static bool CtrVoxel_Update(void) { return updateOk; }
static bool CtrVoxel_IsWarmingUp(void) { return warmingUp; }
static unsigned CtrVoxel_ClearColour(void) { return 0; }
static void CtrVoxel_Draw(int target,float depth) { (void)target;(void)depth; assert(inFrame && invalidated); drawn=true; }
static void CtrVoxel_AfterSubmit(uint64_t t) { (void)t; assert(!inFrame); }
static void CtrLog_Write(int c,const char *f,...) { (void)c;(void)f; }
static unsigned C2D_Color32(unsigned r,unsigned g,unsigned b,unsigned a) { return r|g|b|a; }
static void C2D_TargetClear(int t,unsigned c) { (void)t;(void)c; assert(inFrame && invalidated); }
static void C2D_Prepare(void) {}
static void C3D_FragOpMode(int a) { (void)a; }
static void C3D_StencilTest(bool a,int b,int c,int d,int e) { (void)a;(void)b;(void)c;(void)d;(void)e; }
static void C3D_AlphaTest(bool a,int b,int c) { (void)a;(void)b;(void)c; }
static void C3D_AlphaBlend(int a,int b,int c,int d,int e,int f) { (void)a;(void)b;(void)c;(void)d;(void)e;(void)f; }
static void C2D_SceneBegin(int t) { (void)t; }
static void C2D_DrawImageAt(C2D_Image i,float a,float b,float c,void *d,float e,float f) {
    (void)i;(void)a;(void)b;(void)c;(void)d;(void)e;(void)f; assert(inFrame && invalidated); drawn=true;
}
static void BattleShadows(void) {}
static void BannerEdges(void) {}

#include "soft_video_under_test.inc"

static void CheckPixels(const uint16_t *linear,const uint16_t *source,bool alpha) {
    for (unsigned y=0;y<512;++y) for (unsigned x=0;x<512;++x) {
        uint16_t want=0;
        if (x<480 && y<320) {
            uint16_t c=source[(y/2)*240+x/2];
            unsigned r=c&31,g=(c>>5)&31,b=(c>>10)&31;
            if (alpha) want=(c&32768)?(r*2048+g*64+b*2+1):0;
            else want=r*2048+(g*2+g/16)*32+b;
        }
        assert(linear[y*512+x]==want);
    }
}

static void CheckUiRows(const unsigned *rows,unsigned count,unsigned calls) {
    assert(uiFlushCalls==calls && uiFlushedBytes==count*UP*TEX_DIM*sizeof(uint16_t));
    for (unsigned y=0;y<160;++y) {
        bool expected=false;
        for (unsigned n=0;n<count;++n) expected|=rows[n]==y;
        assert(uiFlushedRows[y]==expected);
    }
}

int main(void) {
    for (unsigned i=0;i<32768;++i) {
        unsigned r=i&31,g=(i>>5)&31,b=(i>>10)&31;
        sLut[i]=(r<<11)|(((g<<1)|(g>>4))<<5)|b;
    }
    for (unsigned i=0;i<240*160;++i) frame[i]=(i*73)^0x9a3f;
    GpuPresent(); assert(transfers==1 && pendingCount==1);
    CheckPixels(sLinear,frame,false);
    GpuPresent(); assert(transfers==1 && pendingCount==0);
    CheckPixels(frameTexels,frame,false);
    frame[239]^=31; frame[159*240]^=0x7fe0;
    GpuPresent(); CheckPixels(sLinear,frame,false);
    sUi=uiPixels; available=true; sFrameDrawn=false;
    for (unsigned pass=0;pass<2;++pass) {
        for (unsigned i=0;i<240*160;++i) uiPixels[i]=(uint16_t)(i+pass*240*160);
        GpuPresent(); CheckPixels(sUiLinear,uiPixels,true);
        assert(uiFlushCalls==1 && uiFlushedBytes==UP_H*TEX_DIM*sizeof(uint16_t));
    }
    GpuPresent(); CheckPixels(uiTexels,uiPixels,true);
    unsigned stable=transfers,revision=sUiRevision;
    GpuPresent(); assert(transfers==stable && sUiRevision==revision);
    CheckUiRows(NULL,0,0);
    uiPixels[0]^=32768; uiPixels[240*160-1]^=0x7fff;
    GpuPresent(); CheckPixels(sUiLinear,uiPixels,true);
    CheckUiRows((const unsigned[]){0,159},2,2);
    /* Adjacent dirty rows share one flush; an unchanged row splits runs. */
    uiPixels[25*240+5]^=32768; uiPixels[26*240+6]^=32768; uiPixels[28*240+7]^=32768;
    GpuPresent(); CheckPixels(sUiLinear,uiPixels,true);
    CheckUiRows((const unsigned[]){25,26,28},3,2);
    /* A different pointer with identical content is unchanged; a partial
     * transparent clear and restoring the other buffer update just one row. */
    memcpy(alternateUi,uiPixels,sizeof(alternateUi)); sUi=alternateUi;
    GpuPresent(); CheckUiRows(NULL,0,0);
    alternateUi[80*240+10]=0;
    GpuPresent(); CheckPixels(sUiLinear,alternateUi,true); CheckUiRows((const unsigned[]){80},1,1);
    sUi=uiPixels;
    GpuPresent(); CheckPixels(sUiLinear,uiPixels,true); CheckUiRows((const unsigned[]){80},1,1);
    for (unsigned pass=0;pass<100;++pass) {
        uint16_t *next=(pass&1)?uiPixels:alternateUi;
        memcpy(next,sUi,sizeof(uiPixels));
        next[((pass*17)%160)*240+(pass*29)%240]^=0x8001;
        sUi=next;
        GpuPresent(); CheckPixels(sUiLinear,sUi,true);
        CheckUiRows((const unsigned[]){(pass*17)%160},1,1);
    }
    GpuPresent(); CheckPixels(uiTexels,sUi,true); CheckUiRows(NULL,0,0);
    assert(sUi==uiPixels);
    /* A rejected FrameBegin must not touch a still-queued source buffer. */
    failBegin=true; uiPixels[1]^=32768;
    stable=transfers; revision=sUiRevision;
    GpuPresent(); assert(transfers==stable && sUiRevision==revision);
    failBegin=false; GpuPresent(); CheckPixels(sUiLinear,uiPixels,true);
    /* The existing hold sources retain distinct revisions and transparency. */
    memcpy(sHoldUi,frame,sizeof(sHoldUi)); sHold=true; sHoldValid=true;
    GpuPresent(); CheckPixels(sUiLinear,sHoldUi,true);
    memcpy(sLastUi,uiPixels,sizeof(sLastUi)); sHoldReady=true; sSurfaceClean=true;
    GpuPresent(); CheckPixels(sUiLinear,sLastUi,true);
    /* A voxel fallback can queue both separate buffers in the same frame. */
    sHold=false; sHoldReady=false; sSurfaceClean=false; sFrameDrawn=true;
    updateOk=false; warmingUp=false; frame[12]^=31; uiPixels[12]^=32768;
    GpuPresent(); assert(pendingCount==2);
    CheckPixels(sLinear,frame,false); CheckPixels(sUiLinear,uiPixels,true);
    GpuPresent(); assert(pendingCount==0);
    assert(begins==ends+1);
    puts("PASS: exact full colour/alpha/2x texture and padding after sparse/disjoint/adjacent row updates, clears and alternating buffers; coalesced dirty flushes; unchanged frames, failed begin, held UI and two-upload fallback; queued buffers survive until next GPU completion.");
    return 0;
}
