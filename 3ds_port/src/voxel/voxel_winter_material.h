/* Snow material: preserve alpha, blue water and source shading. */
#ifndef VOXEL_WINTER_MATERIAL_H
#define VOXEL_WINTER_MATERIAL_H
#include <stdint.h>
static uint16_t VoxelWinter_Color(uint16_t c, unsigned mix, int path) {
    unsigned r=(c>>11)&31,g=(c>>6)&31,b=(c>>1)&31;
    if (!mix || !(c&1)) return c;
    int grass=g>r+1 && g>b+1;
    int earth=path && r>=g && g>b+2 && r>9;
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
