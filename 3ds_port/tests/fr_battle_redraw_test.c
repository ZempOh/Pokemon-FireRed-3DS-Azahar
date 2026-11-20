#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <time.h>
typedef uint8_t u8; typedef uint16_t u16; typedef int16_t s16; typedef bool bool8;
#define TRUE true
#define FALSE false
#define W 320
#define H 240
#define HEADER_H 26
#define FOOTER_Y 206
#define FOOTER_H 34
#define BACK_X (W-62)
#define BACK_Y 211
#define BACK_W 56
#define BACK_H 24
#define MEGA_X (BACK_X-92)
#define MEGA_W 86
#define PARTY_SIZE 6
#define MAX_MON_MOVES 4
#define POKEMON_NAME_LENGTH 10
#define PLAYER_NAME_LENGTH 7
#define OPT_PAGE_ROWS 6
#define HIT_BATTLE 20
#define MOVE_NONE 0
#define CHAR_LV 'L'
#define CHAR_SLASH '/'
#define FONT_SMALL 0
#define FONT_NORMAL 1
#define STR_CONV_MODE_LEFT_ALIGN 0
enum {PORT_BATTLE_ACTION=1,PORT_BATTLE_MOVE,PORT_BATTLE_SWITCH};
enum {TYPE_NORMAL,TYPE_FIGHTING,TYPE_FLYING,TYPE_POISON,TYPE_GROUND,TYPE_ROCK,
      TYPE_BUG,TYPE_GHOST,TYPE_STEEL,TYPE_MYSTERY,TYPE_FIRE,TYPE_WATER,
      TYPE_GRASS,TYPE_ELECTRIC,TYPE_PSYCHIC,TYPE_ICE,TYPE_DRAGON,TYPE_DARK,NUMBER_OF_MON_TYPES};
#include "battle_types.h"
static u16 sCanvas[W*H], framebuffer[W*H], expected[W*H], previous[W*H];
static ViewState sShown;
static bool8 sDrawn;
static unsigned copied;
static const u8 gText_MenuBag[]="BAG",gText_MenuPokemon[]="POKEMON";
static u8 gMoveNames[16][16],gTypeNames[NUMBER_OF_MON_TYPES][16];
static struct {u8 type;} gBattleMoves[16];
typedef struct {int size;u16 colour;} UiIcon;
static const UiIcon sIconLens22={22,0x41},sIconKey22={22,0x42},sIconBag28={28,0x43},sIconShoe28={28,0x44};
static const UiIcon category[3]={{12,0x10},{12,0x11},{12,0x12}};
static const UiIcon *CategoryIcon(u16 move) {return &category[move%3];}
static void FillRect(int,int,int,int,u16);
static inline void Put(int,int,u16);
static const u8 *Ascii(const char *s) {return (const u8 *)s;}
static u8 *StringCopy(u8 *a,const u8 *b) {size_t n=strlen((const char *)b);memcpy(a,b,n+1);return a+n;}
static u8 *ConvertIntToDecimalStringN(u8 *s,int n,int mode,int digits) {(void)mode;(void)digits;return s+sprintf((char *)s,"%d",n);}
static int TextWidth(u8 font,const u8 *s) {return (int)strlen((const char *)s)*(font?7:5);}
static int Text(u8 font,const u8 *s,int x,int y,u16 fg,u16 shadow,bool8 draw) {
    int step=font?7:5,begin=x;
    for(;*s;++s,x+=step) if(draw) for(int j=0;j<8;++j) for(int i=0;i<step-1;++i)
        if((*s>>(i%7))&1) Put(x+i,y+j,((j+i)&1)?fg:shadow);
    return x-begin;
}
static void TextCentered(u8 f,const u8 *s,int x,int y,u16 c,u16 sh) {Text(f,s,x-TextWidth(f,s)/2,y,c,sh,TRUE);}
static void TextRight(u8 f,const u8 *s,int x,int y,u16 c,u16 sh) {Text(f,s,x-TextWidth(f,s),y,c,sh,TRUE);}
static void DrawUiIcon(const UiIcon *icon,int x,int y,bool8 on) {FillRect(x,y,icon->size,icon->size,icon->colour+on);}
static void CtrBottom_BlitRect(const u16 *p,int x0,int y0,int x1,int y1) {
    assert(x0>=0&&x1<=W&&y0>=0&&y1<=H);copied+=(x1-x0)*(y1-y0);
    for(int x=x0;x<x1;++x) for(int y=y0;y<y1;++y) framebuffer[x*H+H-1-y]=p[x*H+H-1-y];
}
static void CtrBottom_Blit(const u16 *p,int x0,int x1) {CtrBottom_BlitRect(p,x0,0,x1,H);}
#include "battle_functions.h"

/* Previous production row rasterizers, retained as an independent oracle. */
static void RefRoundRect(int x,int y,int w,int h,int r,u16 c) {
    if(r*2>h)r=h/2;
    if(r*2>w)r=w/2;
    for(int j=0;j<h;++j) {int in=CornerInset(j<h-j-1?j:h-j-1,r);FillRect(x+in,y+j,w-2*in,1,c);}
}
static void RefRoundGradient(int x,int y,int w,int h,int r,u16 top,u16 c,int shadeRows) {
    if(r*2>h)r=h/2;
    for(int j=0;j<h;++j) {
        int in=CornerInset(j<h-j-1?j:h-j-1,r);
        u16 row=j<shadeRows?Mix(top,c,j,shadeRows):c;
        FillRect(x+in,y+j,w-2*in,1,row);
    }
}
/* Previous full repaint, with unchanged draw ordering and regions. */
static void RefRenderBattle(const ViewState *s) {
    FillRect(0,HEADER_H,W,FOOTER_Y-HEADER_H,C_PAGE);
    if(s->b.choose==PORT_BATTLE_SWITCH) {
        u8 title[32],*p=StringCopy(title,Ascii("Swap "));
        p=StringCopy(p,gMoveNames[s->b.moves[s->b.picked]]);StringCopy(p,Ascii(" with?"));Header(title);
    } else if(s->b.choose&&s->b.player.present) {
        u8 title[32],*p=StringCopy(title,Ascii("What will "));
        p=StringCopy(p,s->b.player.name);StringCopy(p,Ascii(" do?"));Header(title);
    } else Header(NULL);
    Footer();
    if(s->b.choose==PORT_BATTLE_MOVE||s->b.choose==PORT_BATTLE_SWITCH) {
        DrawMoves(s);DrawFighter(&s->b.player,10,s->b.mega?MEGA_X-18:150);
        BackKey(s->pressed==HIT_BATTLE+4);if(s->b.mega)MegaKey(s->b.mega==2,s->pressed==HIT_BATTLE+5);
    } else {
        DrawActions(s);DrawFighter(&s->b.player,10,142);DrawFighter(&s->b.opponent,168,142);
    }
    CtrBottom_Blit(sCanvas,0,W);
}
static uint32_t randomState=0x91ab5845;
static unsigned Random(void) {randomState^=randomState<<13;randomState^=randomState>>17;randomState^=randomState<<5;return randomState;}
static void Check(ViewState state,unsigned n) {
    memcpy(previous,sCanvas,sizeof(previous));
    RefRenderBattle(&state);memcpy(expected,sCanvas,sizeof(expected));
    memcpy(sCanvas,previous,sizeof(previous));memcpy(framebuffer,previous,sizeof(previous));copied=0;
    RenderBattle(&state);
    if(memcmp(sCanvas,expected,sizeof(expected))||memcmp(framebuffer,expected,sizeof(expected))) {
        fprintf(stderr,"battle redraw mismatch case%u choose%u->%u\n",n,sShown.b.choose,state.b.choose);
        for(unsigned i=0;i<W*H;++i)if(sCanvas[i]!=expected[i]||framebuffer[i]!=expected[i]) {
            fprintf(stderr,"pixel%u,%u canvas%04x fb%04x expected%04x\n",i/H,H-1-i%H,sCanvas[i],framebuffer[i],expected[i]);break;
        }
        exit(1);
    }
    sShown=state;sDrawn=TRUE;
}
static void RefDisc(int cx, int cy, int r, u16 c)
{
    for (int dy = -r; dy <= r; dy++)
        for (int dx = -r; dx <= r; dx++)
            if (dx * dx + dy * dy <= r * r + r / 2)
                Put(cx + dx, cy + dy, c);
}

static void RefRing(int cx, int cy, int r, int thick, u16 c)
{
    int outer = r * r + r / 2, inner = (r - thick) * (r - thick) + (r - thick) / 2;

    for (int dy = -r; dy <= r; dy++)
        for (int dx = -r; dx <= r; dx++)
        {
            int d = dx * dx + dy * dy;

            if (d <= outer && d > inner)
                Put(cx + dx, cy + dy, c);
        }
}

int main(void) {
    for(unsigned i=0;i<16;++i) {sprintf((char *)gMoveNames[i],"MOVE%u",i);gBattleMoves[i].type=i%NUMBER_OF_MON_TYPES;}
    for(unsigned i=0;i<NUMBER_OF_MON_TYPES;++i)sprintf((char *)gTypeNames[i],"TYPE%u",i);
    for(unsigned n=0;n<1200;++n) {
        int x=(int)(Random()%500)-100,y=(int)(Random()%400)-80,w=Random()%400,h=Random()%330,r=Random()%80;
        memset(sCanvas,0x19,sizeof(sCanvas));
        if(n&1)RefRoundRect(x,y,w,h,r,0xafe1);else RefRoundGradient(x,y,w,h,r,0x7812,0xab35,n%120);
        memcpy(expected,sCanvas,sizeof(expected));memset(sCanvas,0x19,sizeof(sCanvas));
        if(n&1)RoundRect(x,y,w,h,r,0xafe1);else RoundGradient(x,y,w,h,r,0x7812,0xab35,n%120);
        if(memcmp(expected,sCanvas,sizeof(expected))) {fprintf(stderr,"rounded primitive mismatch %u\n",n);return 1;}
    }
    for(unsigned n=0;n<1200;++n) {
        int x=(int)(Random()%500)-100,y=(int)(Random()%400)-80,r=Random()%80,thick=Random()%100;
        memset(sCanvas,0x19,sizeof(sCanvas));
        if(n&1)RefDisc(x,y,r,0xafe1);else RefRing(x,y,r,thick,0xafe1);
        memcpy(expected,sCanvas,sizeof(expected));memset(sCanvas,0x19,sizeof(sCanvas));
        if(n&1)Disc(x,y,r,0xafe1);else Ring(x,y,r,thick,0xafe1);
        if(memcmp(expected,sCanvas,sizeof(expected))) {fprintf(stderr,"circle primitive mismatch %u\n",n);return 1;}
    }
    ViewState s={0};s.battle=TRUE;s.b.player.present=s.b.opponent.present=TRUE;
    s.b.player.hp=21;s.b.player.maxHp=21;s.b.opponent.hp=16;s.b.opponent.maxHp=16;
    s.b.player.level=6;s.b.opponent.level=3;StringCopy(s.b.player.name,Ascii("CHARMANDER"));StringCopy(s.b.opponent.name,Ascii("ZIGZAGOON"));
    for(unsigned i=0;i<4;++i) {s.b.moves[i]=i+1;s.b.pp[i]=20;s.b.maxPp[i]=40;}
    s.b.choose=PORT_BATTLE_ACTION;Check(s,0);
    --s.b.player.hp;Check(s,1);assert(copied==W*FOOTER_H);
    ++s.fps;Check(s,2);assert(copied==0);
    for(unsigned n=3;n<2003;++n) {
        unsigned i=Random()%4;
        switch(n%18) {
        case 0:s.b.choose=(s.b.choose+1)%4;break;
        case 1:s.b.cursor=i;break;
        case 2:s.pressed=HIT_BATTLE+Random()%7;break;
        case 3:s.pressed=0;break;
        case 4:s.b.player.hp=Random()%22;break;
        case 5:s.b.opponent.hp=Random()%17;break;
        case 6:s.b.pp[i]=Random()%41;break;
        case 7:s.b.moves[i]=Random()%16;break;
        case 8:s.b.picked=i;break;
        case 9:s.b.mega=Random()%3;break;
        case 10:s.b.balls[Random()%6]=Random()%3;break;
        case 11:s.b.player.name[0]='A'+Random()%26;break;
        case 12:s.b.player.present=!s.b.player.present;break;
        case 13:s.b.opponent.present=!s.b.opponent.present;break;
        case 14:s.b.maxPp[i]=Random()%41;break;
        case 15:s.b.player.level=Random()%100;break;
        case 16:sDrawn=FALSE;memset(sCanvas,n&255,sizeof(sCanvas));break;
        case 17:sShown.battle=FALSE;break;
        }
        Check(s,n);
    }
    clock_t start=clock();for(unsigned n=0;n<1000;++n)RefRenderBattle(&s);double full=(double)(clock()-start)/CLOCKS_PER_SEC;
    start=clock();for(unsigned n=0;n<1000;++n) {s.b.player.hp=n%22;RenderBattle(&s);sShown=s;}double dirty=(double)(clock()-start)/CLOCKS_PER_SEC;
    printf("PASS:2400 old/new rounded and circle raster cases and2003 full/dirty battle transitions pixel-identical; HP-only footer and invisible-state checks.\n");
    printf("Host-only HP update benchmark:full%.3fs dirty%.3fs ratio%.3f\n",full,dirty,dirty/full);
    return 0;
}
