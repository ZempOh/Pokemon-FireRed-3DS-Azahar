/* Snow material: preserve alpha, blue water and source shading. */
#ifndef VOXEL_WINTER_MATERIAL_H
#define VOXEL_WINTER_MATERIAL_H
#include <stdint.h>
/* Verified Kanto dirt-path center, edges and inner corners. */
static inline int VoxelWinter_IsPath(unsigned id) {
    return id<=0x0d || (id>=0xd0 && id<=0xd5) || (id>=0xd8 && id<=0xdd)
        || (id>=0xe0 && id<=0xe5) || id==0xfe || id==0xff || (id>=0x102 && id<=0x107);
}
/* Verified General tileset ledges: snow the land cap, preserve cliff faces. */
static inline int VoxelWinter_PixelPath(unsigned id,unsigned y) {
    return VoxelWinter_IsPath(id) || (y<8 && (id==0x97 || id==0xc1 || id==0xc8 || id==0xc9));
}
static inline uint16_t VoxelWinter_Color(uint16_t c, unsigned mix, int path) {
    unsigned r=(c>>11)&31,g=(c>>6)&31,b=(c>>1)&31;
    if (!mix || !(c&1)) return c;
    /* Material 2 is a verified grass-effect sprite, including its olive outlines. */
    int grass=path==2 || (g>r+1 && g>b+1);
    int earth=path==1 && r>=g && g>b+2 && r>9;
    if (!grass && !earth) return c;
    if(mix>16)mix=16;
    unsigned lum=(r+2*g+b)/4;
    unsigned nr=23+lum/5,ng=24+lum/5,nb=25+lum/5;
    if(earth)mix=mix*3/4; /* Keep the route's original pattern readable. */
    r=(r*(16-mix)+nr*mix)/16;
    g=(g*(16-mix)+ng*mix)/16;
    b=(b*(16-mix)+nb*mix)/16;
    return (uint16_t)((r<<11)|(g<<6)|(b<<1)|(c&1));
}
#endif
