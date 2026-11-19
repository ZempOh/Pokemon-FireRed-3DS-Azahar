#include <assert.h>
#include <stdio.h>
#include "voxel_winter_material.h"
int main(void) {
    for(unsigned c=0;c<65536;c++) {
        assert(VoxelWinter_Color(c,0,1)==c);
        assert((VoxelWinter_Color(c,16,1)&1)==(c&1));
        if(!(c&1))assert(VoxelWinter_Color(c,16,1)==c);
    }
    unsigned grass=(8<<11)|(20<<6)|(5<<1)|1;
    unsigned water=(4<<11)|(12<<6)|(26<<1)|1;
    unsigned dirt=(22<<11)|(17<<6)|(8<<1)|1;
    unsigned wall=(20<<11)|(10<<6)|(8<<1)|1;
    assert((VoxelWinter_Color(grass,16,0)>>11)>23);
    assert(VoxelWinter_Color(water,16,1)==water);
    assert(VoxelWinter_Color(wall,16,0)==wall);
    assert(VoxelWinter_Color(dirt,16,1)!=dirt);
    unsigned prev=0;
    for(unsigned m=0;m<=16;m++){unsigned red=VoxelWinter_Color(grass,m,0)>>11;assert(red>=prev);prev=red;}
    puts("PASS snow alpha, water, wall protection, paths, shading and fade");
}
