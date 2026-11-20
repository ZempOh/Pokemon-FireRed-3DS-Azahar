#include "scenery_plant_geometry.h"
struct RoomPlantContext {
    VoxelBuilder *builder;
    const VoxelMapInstance *inst;
    unsigned row;
    float u0,v0,du,dv;
};
static void RoomPlantTriangle(void *opaque,const SceneryPlantVertex *a,
                              const SceneryPlantVertex *b,const SceneryPlantVertex *c) {
    struct RoomPlantContext *ctx=opaque;
    unsigned row=ctx->row,volume=sRoomCells[row].volume;
    const SceneryPlantVertex *source[3]={a,b,c};VoxelVertex out[3];
    float center=ctx->inst->originX+sRoomPlantMaterials[volume].centerX2/32.f;
    float foot=ctx->inst->originY+(sRoomPlantMaterials[volume].foot-sRoomPlantMaterials[volume].width*.25f-sRoomCells[row].back)/16.f;
    for(int i=0;i<3;i++) {
        const SceneryPlantVertex *p=source[i];
        float u=sRoomPlantMaterials[volume].ink[p->ink*2],v=sRoomPlantMaterials[volume].ink[p->ink*2+1];
        out[i]=(VoxelVertex){center+p->x/16,(sRoomCells[row].lift+p->y)/16,foot+p->z/16,
            ctx->u0+(u-sRoomCells[row].sx+.5f)*ctx->du,
            ctx->v0+(v-sRoomCells[row].sy+.5f)*ctx->dv,p->shade/255.f};
    }
    VoxelBuilder_Tri(ctx->builder,&out[0],&out[1],&out[2]);
}
static void EmitPlantVolume(VoxelBuilder *b,const VoxelMapInstance *inst,unsigned i,
                           float u0,float v0,float u1,float v1) {
    unsigned volume=sRoomCells[i].volume;
    if(!sRoomPlantMaterials[volume].draw)return;
    struct RoomPlantContext ctx={b,inst,i,u0,v0,(u1-u0)/16,(v1-v0)/16};
    SceneryPlant_Emit(&ctx,RoomPlantTriangle,sRoomPlantMaterials[volume].height,sRoomPlantMaterials[volume].width);
}
