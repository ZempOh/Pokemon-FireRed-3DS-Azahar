#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "scenery_plant_geometry.h"
typedef struct {long x,y,z;} Point;
typedef struct {Point a,b;int count;} Edge;
static Edge edges[1000];static int used,triangles;static double volume;
static double component[10];
static int cmp(Point a,Point b){if(a.x!=b.x)return a.x<b.x?-1:1;if(a.y!=b.y)return a.y<b.y?-1:1;return a.z==b.z?0:a.z<b.z?-1:1;}
static Point point(const SceneryPlantVertex*p){return(Point){lroundf(p->x*10000),lroundf(p->y*10000),lroundf(p->z*10000)};}
static void edge(Point a,Point b){
 if(cmp(a,b)>0){Point t=a;a=b;b=t;}
 for(int i=0;i<used;i++)if(cmp(a,edges[i].a)==0&&cmp(b,edges[i].b)==0){edges[i].count++;return;}
 assert(used<1000);edges[used++]=(Edge){a,b,1};
}
static void emit(void*ctx,const SceneryPlantVertex*a,const SceneryPlantVertex*b,const SceneryPlantVertex*c){
 (void)ctx;const SceneryPlantVertex*p[]={a,b,c};triangles++;
 for(int i=0;i<3;i++){
  assert(isfinite(p[i]->x)&&isfinite(p[i]->y)&&isfinite(p[i]->z));
  assert(p[i]->y>=0&&p[i]->y<=28&&fabsf(p[i]->x)<=8.1f&&fabsf(p[i]->z)<=8.1f);
  assert(p[i]->ink<6);
 }
 edge(point(a),point(b));edge(point(b),point(c));edge(point(c),point(a));
 double part=(a->x*(b->y*c->z-b->z*c->y)+a->y*(b->z*c->x-b->x*c->z)+a->z*(b->x*c->y-b->y*c->x))/6.;
 volume+=part;component[triangles<=64?0:triangles<=80?1:2+(triangles-81)/8]+=part;
}
int main(void){
 SceneryPlant_Emit(NULL,emit,28,16);
 for(int i=0;i<used;i++)assert(edges[i].count==2);
 assert(volume>0&&triangles<=160);
 for(int i=0;i<10;i++)assert(component[i]>0);
 printf("Botanical family: %d triangles, %d closed edges, positive volume %.3f; bounds/materials passed\n",triangles,used,volume);
}
