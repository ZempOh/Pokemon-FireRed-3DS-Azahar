/* Shared closed building geometry. Coordinates/UVs are source-art pixels. */
#ifndef SCENERY_BUILDING_GEOMETRY_H
#define SCENERY_BUILDING_GEOMETRY_H
typedef struct { float x,y,z,u,v; } SceneryBuildingVertex;
typedef void (*SceneryBuildingTriangle)(void*,const SceneryBuildingVertex*,const SceneryBuildingVertex*,const SceneryBuildingVertex*,unsigned);
typedef struct {
    float width,depth,back,wallHeight,ridgeHeight,hipInset;
    float roofTop,wallRow,artHeight;
    int roofKind; /* 0 hip, 1 flat, 2 front gable. */
    float gableX,gableRow,ridgeBackHeight;
    float wallLeft,wallRight,wallBottom; /* Reviewed facade crop, exclusive right/bottom. */
    float roofLeft,roofRight; /* Independent reviewed roof crop; zero pair means full width. */
} SceneryBuildingShape;
static void SceneryBuilding_Quad(void* ctx,SceneryBuildingTriangle emit,
    SceneryBuildingVertex a,SceneryBuildingVertex b,SceneryBuildingVertex c,SceneryBuildingVertex d,unsigned shade) {
    emit(ctx,&a,&b,&c,shade);emit(ctx,&a,&c,&d,shade);
}
static void SceneryBuilding_Emit(void* ctx,SceneryBuildingTriangle emit,const SceneryBuildingShape* s) {
    float w=s->width,f=s->depth,b=s->back,h=s->wallHeight;
    float left=s->wallLeft,right=s->wallRight>left?s->wallRight:w;
    float bottom=s->wallBottom>s->wallRow?s->wallBottom:s->artHeight;
    float u0=left+.5f,u1=right-.5f,vt=s->wallRow+.5f,vb=bottom-.5f;
    SceneryBuildingVertex fl={0,0,f,u0,vb},fr={w,0,f,u1,vb},br={w,0,b,u1,vb},bl={0,0,b,u0,vb};
    SceneryBuildingVertex tl={0,h,f,u0,vt},tr={w,h,f,u1,vt},rr={w,h,b,u1,vt},rl={0,h,b,u0,vt};
    SceneryBuilding_Quad(ctx,emit,fl,fr,tr,tl,248);
    /* Side wall material uses the original facade's blank corner posts. */
    SceneryBuildingVertex l0=bl,l1=fl,l2=tl,l3=rl;
    l0.u=l3.u=left+1.5f;l1.u=l2.u=left+6.5f;
    SceneryBuilding_Quad(ctx,emit,l0,l1,l2,l3,194);
    SceneryBuildingVertex r0=fr,r1=br,r2=rr,r3=tr;
    r0.u=r3.u=right-7.5f;r1.u=r2.u=right-2.5f;
    SceneryBuilding_Quad(ctx,emit,r0,r1,r2,r3,216);
    SceneryBuilding_Quad(ctx,emit,br,bl,rl,rr,184);
    SceneryBuilding_Quad(ctx,emit,bl,br,fr,fl,160);
    /* Roofs retain their independently reviewed original source span. */
    float roofLeft=s->roofLeft,roofRight=s->roofRight>roofLeft?s->roofRight:w;
    tl.u=rl.u=roofLeft+.5f;tr.u=rr.u=roofRight-.5f;
    tl.v=tr.v=s->wallRow-.5f;rl.v=rr.v=s->roofTop+.5f;
    if(s->roofKind==1) {
        SceneryBuilding_Quad(ctx,emit,tl,tr,rr,rl,244);
        return;
    }
    if(s->roofKind==2) {
        float peak=w*s->gableX;
        SceneryBuildingVertex front={peak,s->ridgeHeight,f,peak,s->gableRow+.5f};
        SceneryBuildingVertex back={peak,s->ridgeBackHeight,b,peak,s->roofTop+.5f};
        /* Roof planes sample only roof rows. The vertical gable keeps its own
         * facade triangle; its windows must never stretch onto either slope. */
        SceneryBuildingVertex roofLeft=tl,roofRight=tr,roofFront=front;
        roofLeft.v=roofRight.v=roofFront.v=s->gableRow-.5f;
        SceneryBuilding_Quad(ctx,emit,rl,roofLeft,roofFront,back,216);
        SceneryBuilding_Quad(ctx,emit,roofRight,rr,back,roofFront,248);
        SceneryBuildingVertex gableLeft=tl,gableRight=tr;
        gableLeft.u=u0;gableRight.u=u1;
        emit(ctx,&gableLeft,&gableRight,&front,250);
        SceneryBuildingVertex rb=rr,lb=rl,rear=back;
        /* Rear gable is facade material too; roof UVs can include exterior grass. */
        rb.u=u1;lb.u=u0;
        rb.v=lb.v=s->wallRow-.5f;rear.v=s->gableRow+.5f;
        emit(ctx,&rb,&lb,&rear,184);
        return;
    }
    float m=(b+f)*.5f;
    SceneryBuildingVertex a={s->hipInset,s->ridgeHeight,m,s->hipInset,s->roofTop+.5f};
    SceneryBuildingVertex c={w-s->hipInset,s->ridgeHeight,m,w-s->hipInset,s->roofTop+.5f};
    SceneryBuilding_Quad(ctx,emit,tl,tr,c,a,250);
    SceneryBuildingVertex rb=rr,lb=rl;rb.v=lb.v=s->wallRow-.5f;
    SceneryBuilding_Quad(ctx,emit,rb,lb,a,c,205);
    emit(ctx,&lb,&tl,&a,190);emit(ctx,&tr,&rb,&c,224);
}
#endif
