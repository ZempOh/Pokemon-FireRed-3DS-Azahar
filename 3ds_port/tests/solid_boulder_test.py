"""Compile the real dynamic-rock emitter and check world-space movement and bounds."""
from pathlib import Path
import argparse,subprocess,tempfile
p=argparse.ArgumentParser();p.add_argument('--cc',default='gcc');a=p.parse_args()
source=(Path(__file__).resolve().parents[1]/'src/voxel/voxel_entities.c').read_text(encoding='utf8')
body=source[source.index('static bool IsSolidBoulder'):source.index('static void EmitBillboard')]
header=(Path(__file__).resolve().parents[1]/'src/voxel/voxel_entities.h').read_text(encoding='utf8')
capacity_defines='\n'.join(line for line in header.splitlines() if any(line.startswith('#define '+name+' ') for name in ['VOXEL_SPRITE_SLOTS','VOXEL_SOLID_BOULDER_VERTICES','VOXEL_SPRITE_VERTEX_RESERVE']))+'\n'
renderer=(Path(__file__).resolve().parents[1]/'src/voxel/ctr_voxel.c').read_text(encoding='utf8')
assert '#define VOXEL_SPRITE_RESERVE VOXEL_SPRITE_VERTEX_RESERVE' in renderer
prelude=capacity_defines+r'''
#include <assert.h>
#include <stdbool.h>
#include <math.h>
#include <stdio.h>
#define OBJ_EVENT_GFX_CUT_TREE 95
#define OBJ_EVENT_GFX_ROCK_SMASH_ROCK 96
#define OBJ_EVENT_GFX_PUSHABLE_BOULDER 97
#define VOXEL_PIXELS_PER_TILE 16.0f
#define VOXEL_SPRITE_COLUMNS 8
#define VOXEL_SPRITE_SLOT_DIM 64
#define VOXEL_SPRITE_ATLAS_DIM 512
#define VOXEL_SPRITE_ATLAS_H 512
typedef struct {float x,y,z,u,v,shade;} VoxelVertex;
typedef struct {int width,height;} VoxelSpriteSlot;
typedef struct {VoxelVertex vertices[VOXEL_SPRITE_VERTEX_RESERVE];unsigned count;} VoxelBuilder;
static int VisibleRows(const VoxelSpriteSlot*s){return s->height-1;}
static float VoxelRelief_LiftAt(float x,float z){(void)x;(void)z;return .25f;}
static float VoxelRelief_ShiftAt(float x,float z){(void)x;(void)z;return .1f;}
static void VoxelBuilder_Quad(VoxelBuilder*b,const VoxelVertex*a,const VoxelVertex*c,const VoxelVertex*d,const VoxelVertex*e){assert(b->count+6<=VOXEL_SPRITE_VERTEX_RESERVE);b->vertices[b->count++]=*a;b->vertices[b->count++]=*c;b->vertices[b->count++]=*d;b->vertices[b->count++]=*a;b->vertices[b->count++]=*d;b->vertices[b->count++]=*e;}
'''
main=r'''
int main(void){
 assert(IsSolidCutTree(95)&&!IsSolidCutTree(96)&&!IsSolidCutTree(0));
 VoxelBuilder tree={0};VoxelSpriteSlot treeSlot={16,24};
 EmitSolidCutTree(&tree,&treeSlot,0,10,20,0,0,1);
 assert(tree.count==144);
 assert(IsSolidBoulder(96)&&IsSolidBoulder(97)&&!IsSolidBoulder(0)&&!IsSolidBoulder(95));
 VoxelBuilder a={0},b={0};VoxelSpriteSlot s={16,16};
 EmitSolidBoulder(&a,&s,3,10,20,.2f,.5f,1);
 EmitSolidBoulder(&b,&s,3,11,22,.2f,.5f,1);
 assert(a.count>16&&a.count==b.count);
 float minY=100,maxY=-100,minZ=100,maxZ=-100;
 for(unsigned i=0;i<a.count;i++){
  VoxelVertex v=a.vertices[i],w=b.vertices[i];
  assert(fabsf((w.x-v.x)-1)<.00001f&&fabsf((w.z-v.z)-2)<.00001f&&w.y==v.y);
  assert(v.u>=0&&v.u<=1&&v.v>=0&&v.v<=1&&isfinite(v.x)&&isfinite(v.z));
  minY=fminf(minY,v.y);maxY=fmaxf(maxY,v.y);minZ=fminf(minZ,v.z);maxZ=fmaxf(maxZ,v.z);
 }
 assert(fabsf(minY-.75f)<.00001f&&maxY-minY>.7f&&maxZ-minZ>.8f);
 VoxelBuilder crowded={0};
 for(unsigned i=0;i<16;i++)EmitSolidBoulder(&crowded,&s,i,10+i%4,20+i/4,0,0,1);
 assert(crowded.count==16*VOXEL_SOLID_BOULDER_VERTICES);
 assert(VOXEL_SPRITE_VERTEX_RESERVE-crowded.count >= (VOXEL_SPRITE_SLOTS-16)*6+32);
 puts("PASS dynamic boulders: explicit IDs, moving world coordinates, ground contact, height and depth");
}
'''
with tempfile.TemporaryDirectory() as tmp:
    c=Path(tmp)/'test.c';exe=Path(tmp)/'test.exe';c.write_text(prelude+body+main)
    subprocess.run([a.cc,'-std=c99','-Wall','-Wextra','-Werror',str(c),'-lm','-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
