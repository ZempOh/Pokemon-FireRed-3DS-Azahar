/* Renderer-neutral potted foliage. Positions use pixels, Y is height.
 * Adapters supply source-palette materials and coordinate transforms.
 * Materials: leaf, leaf highlight, stem, pot, rim, soil. */
#ifndef SCENERY_PLANT_GEOMETRY_H
#define SCENERY_PLANT_GEOMETRY_H
typedef struct {float x,y,z;unsigned char ink,shade;} SceneryPlantVertex;
typedef void (*SceneryPlantTriangle)(void*,const SceneryPlantVertex*,const SceneryPlantVertex*,const SceneryPlantVertex*);
static SceneryPlantVertex SceneryPlant_Point(float x,float y,float z,int ink,int shade) {
    return (SceneryPlantVertex){x,y,z,(unsigned char)ink,(unsigned char)shade};
}
static void SceneryPlant_Quad(void *ctx,SceneryPlantTriangle emit,
    SceneryPlantVertex a,SceneryPlantVertex b,SceneryPlantVertex c,SceneryPlantVertex d) {
    emit(ctx,&c,&b,&a);emit(ctx,&d,&c,&a);
}
static void SceneryPlant_EmitStyle(void *ctx,SceneryPlantTriangle emit,float height,float width,int rounded) {
    static const float dx[9]={1,.7071068f,0,-.7071068f,-1,-.7071068f,0,.7071068f,1};
    static const float dz[9]={0,.7071068f,1,.7071068f,0,-.7071068f,-1,-.7071068f,0};
    const float radii[4]={.14f,.22f,.25f,.19f},levels[4]={0,.24f,.29f,.29f};
    for(int band=0;band<3;band++)for(int e=0;e<8;e++) {
        int ink=band==2?4:3,shade=190+(e<4?35:0)+(band==2?20:0);
        SceneryPlant_Quad(ctx,emit,
            SceneryPlant_Point(dx[e]*width*radii[band],height*levels[band],dz[e]*width*radii[band],ink,shade),
            SceneryPlant_Point(dx[e+1]*width*radii[band],height*levels[band],dz[e+1]*width*radii[band],ink,shade),
            SceneryPlant_Point(dx[e+1]*width*radii[band+1],height*levels[band+1],dz[e+1]*width*radii[band+1],ink,shade),
            SceneryPlant_Point(dx[e]*width*radii[band+1],height*levels[band+1],dz[e]*width*radii[band+1],ink,shade));
    }
    for(int e=0;e<8;e++) {
        SceneryPlantVertex center=SceneryPlant_Point(0,0,0,3,150);
        SceneryPlantVertex a=SceneryPlant_Point(dx[e]*width*.14f,0,dz[e]*width*.14f,3,150);
        SceneryPlantVertex b=SceneryPlant_Point(dx[e+1]*width*.14f,0,dz[e+1]*width*.14f,3,150);
        emit(ctx,&center,&a,&b);
        center=SceneryPlant_Point(0,height*.29f,0,5,185);
        a=SceneryPlant_Point(dx[e]*width*.19f,height*.29f,dz[e]*width*.19f,5,185);
        b=SceneryPlant_Point(dx[e+1]*width*.19f,height*.29f,dz[e+1]*width*.19f,5,185);
        emit(ctx,&center,&b,&a);
    }
    for(int e=0;e<8;e+=2) {
        int j=e+2;
        SceneryPlant_Quad(ctx,emit,
            SceneryPlant_Point(dx[e]*width*.025f,height*.27f,dz[e]*width*.025f,2,200),
            SceneryPlant_Point(dx[j]*width*.025f,height*.27f,dz[j]*width*.025f,2,200),
            SceneryPlant_Point(dx[j]*width*.018f,height*.70f,dz[j]*width*.018f,2,220),
            SceneryPlant_Point(dx[e]*width*.018f,height*.70f,dz[e]*width*.018f,2,220));
        SceneryPlantVertex center=SceneryPlant_Point(0,height*.27f,0,2,180);
        SceneryPlantVertex a=SceneryPlant_Point(dx[e]*width*.025f,height*.27f,dz[e]*width*.025f,2,180);
        SceneryPlantVertex b=SceneryPlant_Point(dx[j]*width*.025f,height*.27f,dz[j]*width*.025f,2,180);
        emit(ctx,&center,&a,&b);
        center=SceneryPlant_Point(0,height*.70f,0,2,220);
        a=SceneryPlant_Point(dx[e]*width*.018f,height*.70f,dz[e]*width*.018f,2,220);
        b=SceneryPlant_Point(dx[j]*width*.018f,height*.70f,dz[j]*width*.018f,2,220);
        emit(ctx,&center,&b,&a);
    }
    if(rounded) {
        const float radius[3]={.26f,.49f,.36f},level[3]={.48f,.68f,.87f};
        for(int band=0;band<2;band++)for(int e=0;e<8;e++) {
            int ink=band,shade=195+band*25+(e<4?20:0);
            SceneryPlant_Quad(ctx,emit,
                SceneryPlant_Point(dx[e]*width*radius[band],height*level[band],dz[e]*width*radius[band],ink,shade),
                SceneryPlant_Point(dx[e+1]*width*radius[band],height*level[band],dz[e+1]*width*radius[band],ink,shade),
                SceneryPlant_Point(dx[e+1]*width*radius[band+1],height*level[band+1],dz[e+1]*width*radius[band+1],ink,shade),
                SceneryPlant_Point(dx[e]*width*radius[band+1],height*level[band+1],dz[e]*width*radius[band+1],ink,shade));
        }
        for(int e=0;e<8;e++) {
            SceneryPlantVertex center=SceneryPlant_Point(0,height*.44f,0,0,175);
            SceneryPlantVertex a=SceneryPlant_Point(dx[e]*width*radius[0],height*level[0],dz[e]*width*radius[0],0,175);
            SceneryPlantVertex b=SceneryPlant_Point(dx[e+1]*width*radius[0],height*level[0],dz[e+1]*width*radius[0],0,175);
            emit(ctx,&center,&a,&b);
            center=SceneryPlant_Point(0,height*.98f,0,1,245);
            a=SceneryPlant_Point(dx[e]*width*radius[2],height*level[2],dz[e]*width*radius[2],1,245);
            b=SceneryPlant_Point(dx[e+1]*width*radius[2],height*level[2],dz[e+1]*width*radius[2],1,245);
            emit(ctx,&center,&b,&a);
        }
        return;
    }
    /* Each leaf is a closed lens, with a ridge and a separate underside. */
    for(int leaf=0;leaf<8;leaf++) {
        float x=dx[leaf],z=dz[leaf],reach=leaf%3==0?.30f:.49f;
        float tip=leaf%3==0?.98f:.65f,shoulder=leaf%3==0?.80f:.72f;
        float wide=leaf%3==0?.11f:.16f;
        SceneryPlantVertex rim[4]={
            SceneryPlant_Point(0,height*.56f,0,0,210),
            SceneryPlant_Point(width*(x*reach*.52f-z*wide),height*shoulder,width*(z*reach*.52f+x*wide),0,210),
            SceneryPlant_Point(width*x*reach,height*tip,width*z*reach,0,210),
            SceneryPlant_Point(width*(x*reach*.52f+z*wide),height*shoulder,width*(z*reach*.52f-x*wide),0,210)};
        SceneryPlantVertex top=SceneryPlant_Point(width*x*reach*.52f,height*(shoulder+.065f),width*z*reach*.52f,leaf&1,245);
        SceneryPlantVertex bottom=SceneryPlant_Point(width*x*reach*.52f,height*(shoulder-.045f),width*z*reach*.52f,0,160);
        for(int e=0;e<4;e++) {
            SceneryPlantVertex a=rim[e],b=rim[(e+1)&3];
            a.ink=b.ink=top.ink;a.shade=b.shade=top.shade;
            emit(ctx,&a,&b,&top);
            a.ink=b.ink=bottom.ink;a.shade=b.shade=bottom.shade;
            emit(ctx,&b,&a,&bottom);
        }
    }
}
static inline void SceneryPlant_Emit(void *ctx,SceneryPlantTriangle emit,float height,float width) {
    SceneryPlant_EmitStyle(ctx,emit,height,width,0);
}
#endif
