/* Test the actual generated plant cells, not a duplicate implementation. */
#include <assert.h>
#include <math.h>
#include <stdio.h>
typedef struct {float x,y,z,u,v,shade;} VoxelVertex;
typedef struct {unsigned count;} VoxelBuilder;
typedef struct {int originX,originY;} VoxelMapInstance;
#include "voxel_room_table.h"
static unsigned current;
static void CheckVertex(const VoxelVertex *v) {
    assert(isfinite(v->x)&&isfinite(v->y)&&isfinite(v->z));
    assert(v->y+0.0001f>=sRoomCells[current].lift/16.f);
    unsigned volume=sRoomCells[current].volume;
    float center=sRoomPlantMaterials[volume].centerX2/32.f;
    float width=sRoomPlantMaterials[volume].width/16.f;
    assert(fabsf(v->x-center)<=width*.51f);
    assert(v->y<=(sRoomCells[current].lift+sRoomPlantMaterials[volume].height)/16.f+.0001f);
    assert(v->u>=0 && v->u<512 && v->v>=0 && v->v<1024);
}
static void VoxelBuilder_Tri(VoxelBuilder*b,const VoxelVertex*a,const VoxelVertex*c,const VoxelVertex*d) {
    CheckVertex(a);CheckVertex(c);CheckVertex(d);b->count++;
}
#include "voxel_room_volume.h"
int main(void) {
    unsigned cells=0,plants=0,max=0,total=0;VoxelMapInstance m={0,0};
    for(current=0;current<sizeof(sRoomCells)/sizeof(sRoomCells[0]);current++) {
        unsigned volume=sRoomCells[current].volume;if(!volume)continue;
        assert(volume<sizeof(sRoomVolumeMasks)/sizeof(sRoomVolumeMasks[0]));
        assert(volume<sizeof(sRoomPlantMaterials)/sizeof(sRoomPlantMaterials[0]));
        VoxelBuilder b={0};
        EmitPlantVolume(&b,&m,current,sRoomCells[current].sx,sRoomCells[current].sy,sRoomCells[current].sx+16,sRoomCells[current].sy+16);
        assert(b.count==(sRoomPlantMaterials[volume].draw?144u:0u));
        plants+=b.count>0;
        cells++;total+=b.count;if(b.count>max)max=b.count;
    }
    assert(cells>=100&&plants>=30);
    printf("%u actual plant cells, %u plants: bounds, base, UVs, finite geometry passed; max %u triangles/plant, total %u\n",cells,plants,max,total);
}
