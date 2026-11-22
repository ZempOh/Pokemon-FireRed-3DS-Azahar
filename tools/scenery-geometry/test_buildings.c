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
static void check(int kind,float peak) {
    int flat=kind==1;
    SceneryBuildingShape s={80,80,16,32,flat?32:56,12,8,48,80,kind,peak,24,56,5,75,78,1,79};
    if(kind==2 && peak>.6f)s.ridgeHeight=48; /* Sloping ridge on compound entry roofs. */
    count=0;SceneryBuilding_Emit(0,collect,&s);
    assert(count==(unsigned)(flat?36:48));
    /* Synthetic source grass at x<5, x>=75, y>=78 must never reach walls. */
    for(unsigned i=0;i<30;i++) {
        assert(vertices[i].u>=5&&vertices[i].u<75);
        assert(vertices[i].v>=48&&vertices[i].v<78);
    }
    if(kind==2)for(unsigned i=30;i<42;i++)assert(vertices[i].v<s.gableRow);
    /* Flat roof excludes exterior ground columns independently of walls. */
    if(flat)for(unsigned i=30;i<count;i++) {
        assert(vertices[i].u>=1&&vertices[i].u<79);
        assert(vertices[i].v>=8&&vertices[i].v<48);
    }
    /* Both vertical gables must exclude synthetic exterior grass columns.
     * Exact74 exposed the rear triangle retaining the uncropped roof UVs. */
    if(kind==2)for(unsigned i=42;i<48;i++) {
        assert(vertices[i].u>=s.wallLeft&&vertices[i].u<s.wallRight);
        assert(vertices[i].v>=s.gableRow&&vertices[i].v<s.wallRow);
    }
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
int main(void) {check(0,.5f);check(1,.5f);check(2,.5f);check(2,.65f);puts("PASS closed hip/flat/gable buildings, depth, nondegenerate faces, source UV bounds");return 0;}
