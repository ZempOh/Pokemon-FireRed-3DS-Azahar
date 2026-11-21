#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "scenery_building_geometry.h"
static SceneryBuildingVertex vertices[96];static unsigned count;
static void collect(void* ctx,const SceneryBuildingVertex* a,const SceneryBuildingVertex* b,const SceneryBuildingVertex* c,unsigned shade) {
    (void)ctx;assert(shade>=160&&shade<=256);assert(count+3<=96);
    const SceneryBuildingVertex* p[3]={a,b,c};
    for(unsigned i=0;i<3;i++) { assert(isfinite(p[i]->x)&&isfinite(p[i]->y)&&isfinite(p[i]->z));vertices[count++]=*p[i]; }
    float ux=b->x-a->x,uy=b->y-a->y,uz=b->z-a->z,vx=c->x-a->x,vy=c->y-a->y,vz=c->z-a->z;
    float nx=uy*vz-uz*vy,ny=uz*vx-ux*vz,nz=ux*vy-uy*vx;assert(nx*nx+ny*ny+nz*nz>0);
}
static int same(SceneryBuildingVertex a,SceneryBuildingVertex b) {return a.x==b.x&&a.y==b.y&&a.z==b.z;}
static void check(int flat) {
    SceneryBuildingShape s={80,80,16,32,56,12,8,48,80,flat};count=0;SceneryBuilding_Emit(0,collect,&s);
    assert(count==(unsigned)(flat?36:48));
    float highest=0;
    for(unsigned i=0;i<count;i++) {
        SceneryBuildingVertex a=vertices[i],b=vertices[i/3*3+(i+1)%3];unsigned matches=0;
        assert(a.x>=0&&a.x<=80&&a.z>=16&&a.z<=80&&a.y>=0&&a.y<=56);
        assert(a.u>=0&&a.u<80&&a.v>=0&&a.v<80);if(a.y>highest)highest=a.y;
        for(unsigned j=0;j<count;j++) {
            SceneryBuildingVertex c=vertices[j],d=vertices[j/3*3+(j+1)%3];
            if((same(a,c)&&same(b,d))||(same(a,d)&&same(b,c)))matches++;
        }
        assert(matches==2); /* Every mesh edge belongs to exactly two faces. */
    }
    assert(highest==(flat?32:56));
}
int main(void) {check(0);check(1);puts("PASS closed hip/flat buildings, depth, nondegenerate faces, source UV bounds");return 0;}
