#include "global.h"
#include <assert.h>
#include <time.h>

u8 REG_BASE[0x400] __attribute__((aligned(4)));
u8 PLTT[PLTT_SIZE] __attribute__((aligned(4)));
u8 VRAM_[VRAM_SIZE] __attribute__((aligned(4)));
u8 OAM[OAM_SIZE] __attribute__((aligned(4)));
bool8 gPortOamScreen[128];
vu16 gPortEmuDISPSTAT;
static u32 rng=0x61451223;
static bool dynamic;
static unsigned dmaCalls;
static unsigned Random(void) { rng^=rng<<13; rng^=rng>>17; rng^=rng<<5; return rng; }
static void Interrupt(void) {
    if (dynamic) {
        REG_BLDALPHA = 0x1000 | (REG_VCOUNT & 15);
        REG_BLDY = REG_VCOUNT & 15;
        REG_BG0HOFS = REG_VCOUNT & 31;
        REG_WIN0H = (REG_VCOUNT & 127) << 8 | 200;
    }
}
void (*gIntrTable[16])(void) = {Interrupt,Interrupt,Interrupt,Interrupt};
void RunDMAs(u32 type) { (void)type; ++dmaCalls; }
extern void RefDrawFrame(u16 *),NewDrawFrame(u16 *);
#define DECLARE(p) extern u16 *p##gPortUiPixels; extern u16 p##gPortUiLayers; \
extern u8 p##gPortUiTrim,p##gPortUiObjInWindows,p##gPortUiScreenObj,p##gPortDrawLines;
DECLARE(Ref) DECLARE(New)
static u16 frameA[240*160],frameB[240*160],uiA[240*160],uiB[240*160];
static u8 savedRegs[sizeof(REG_BASE)];

static void Setup(unsigned n) {
    memset(REG_BASE,0,sizeof(REG_BASE));
    for (unsigned i=0;i<sizeof(VRAM_);++i) VRAM_[i]=Random();
    for (unsigned i=0;i<sizeof(PLTT)/2;++i) ((u16 *)PLTT)[i]=Random()&0x7fff;
    memset(OAM,0,sizeof(OAM));
    for (unsigned i=0;i<128;++i) ((struct OamData *)OAM)[i].affineMode=2;
    for (unsigned i=0;i<(n%9);++i) {
        struct OamData *o=&((struct OamData *)OAM)[i];
        o->affineMode = i==7 ? 3 : 0;
        o->objMode=(n+i)%3; o->size=(n+i)%4; o->shape=(n+i/2)%3;
        o->x=Random()%512; o->y=Random()%256;
        o->tileNum=Random()%256; o->paletteNum=i;
        o->priority=i%4; o->matrixNum=24;
        o->mosaic=n%7==0; o->bpp=n%11==0;
    }
    ((struct OamData *)OAM)[96].affineParam=256;
    ((struct OamData *)OAM)[99].affineParam=256;
    for (unsigned bg=0;bg<4;++bg) {
        unsigned size=Random()%4;
        *(u16 *)(REG_ADDR_BG0CNT+bg*2)=bg|((12+bg*4)<<8)|(size<<14)|(n%5==0?BGCNT_256COLOR:0);
        *(u16 *)(REG_ADDR_BG0HOFS+bg*4)=Random()%512;
        *(u16 *)(REG_ADDR_BG0VOFS+bg*4)=Random()%512;
        u16 *map=(u16 *)BG_SCREEN_ADDR(12+bg*4);
        for (unsigned t=0;t<4096;++t) map[t]=(Random()&0xfc00)|(Random()%256);
    }
    REG_DISPCNT=DISPCNT_OBJ_1D_MAP|0x1f00|((n%8)<<13);
    if (n%13==0) {
        REG_DISPCNT|=1; /* BG2 affine, as in transitions and move effects. */
        REG_BG2PA=0x100; REG_BG2PB=8; REG_BG2PC=16; REG_BG2PD=0x100;
        REG_BG2X=0; REG_BG2Y=0;
    }
    REG_BLDCNT=Random()&0x3fff; REG_BLDALPHA=0x0808; REG_BLDY=Random()%17;
    REG_WIN0H=Random(); REG_WIN1H=Random(); REG_WIN0V=Random(); REG_WIN1V=Random();
    REG_WININ=Random()&0x3f3f; REG_WINOUT=Random()&0x3f3f;
    if (n%4==0) { REG_WIN0H=240; REG_WIN0V=112; REG_WININ=0x3f3f; REG_WINOUT=0x3f3f; }
    if (n%4==1) { REG_WIN0H=0; REG_WIN1H=0; }
    if (n%4==2) { REG_WIN0H=0xf010; REG_WIN1H=0xa020; }
    REG_MOSAIC=n%7==0?0x2222:0;
    dynamic=n%5==1;
    REG_DISPSTAT=dynamic?DISPSTAT_HBLANK_INTR|DISPSTAT_VCOUNT_INTR:0;
    RefgPortUiPixels=uiA; NewgPortUiPixels=uiB;
    RefgPortUiLayers=NewgPortUiLayers=n%2?0x1700:0x0100;
    RefgPortUiTrim=NewgPortUiTrim=n%2==0;
    RefgPortUiObjInWindows=NewgPortUiObjInWindows=n%3==0;
    RefgPortUiScreenObj=NewgPortUiScreenObj=n%3==1;
    RefgPortDrawLines=NewgPortDrawLines=n%3+1;
    for (unsigned i=0;i<128;++i) gPortOamScreen[i]=i&1;
}

int main(void) {
    for (unsigned n=0;n<600;++n) {
        Setup(n);
        u16 savedDispstat=REG_DISPSTAT;
        memcpy(savedRegs,REG_BASE,sizeof(REG_BASE));
        memset(frameA,0x42,sizeof(frameA)); memset(frameB,0x42,sizeof(frameB));
        memset(uiA,0x42,sizeof(uiA)); memset(uiB,0x42,sizeof(uiB));
        dmaCalls=0; RefDrawFrame(frameA); assert(dmaCalls==160);
        u8 finalRegs[sizeof(REG_BASE)]; memcpy(finalRegs,REG_BASE,sizeof(REG_BASE));
        memcpy(REG_BASE,savedRegs,sizeof(REG_BASE));
        REG_DISPSTAT=savedDispstat;
        dmaCalls=0; NewDrawFrame(frameB); assert(dmaCalls==160);
        if (memcmp(frameA,frameB,sizeof(frameA)) || memcmp(uiA,uiB,sizeof(uiA)) || memcmp(finalRegs,REG_BASE,sizeof(REG_BASE))) {
            fprintf(stderr,"scanline mismatch case %u\n",n);
            for (unsigned i=0;i<240*160;++i) if (frameA[i]!=frameB[i] || uiA[i]!=uiB[i]) {
                fprintf(stderr,"pixel %u,%u: frame %04x/%04x UI %04x/%04x\n",i%240,i/240,frameA[i],frameB[i],uiA[i],uiB[i]); break;
            }
            return 1;
        }
    }
    Setup(0); dynamic=false; REG_DISPCNT=0xbf40; REG_WIN0H=240; REG_WIN0V=112;
    REG_WININ=REG_WINOUT=0x3f3f; REG_BLDCNT=0; REG_MOSAIC=0;
    RefgPortUiTrim=NewgPortUiTrim=0; RefgPortUiLayers=NewgPortUiLayers=0x1700;
    RefgPortDrawLines=NewgPortDrawLines=2;
    clock_t begin=clock(); for(unsigned n=0;n<300;++n) RefDrawFrame(frameA); double before=(double)(clock()-begin)/CLOCKS_PER_SEC;
    begin=clock(); for(unsigned n=0;n<300;++n) NewDrawFrame(frameB); double after=(double)(clock()-begin)/CLOCKS_PER_SEC;
    printf("PASS: 600 pixel-identical full/UI frames including split/wrapped/object windows, blend, mosaic, hidden frames, HBlank/VCount register changes.\n");
    printf("Synthetic battle UI benchmark (host only): reference %.3fs optimized %.3fs ratio %.3f\n",before,after,after/before);
    return 0;
}
