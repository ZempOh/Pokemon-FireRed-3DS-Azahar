"""Compile the production solid-tree emitter and check its streamed geometry."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/voxel/voxel_tree.c').read_text()
start=source.index('static void EmitSolidCrown(')
end=source.index('\nstatic void EmitCrown(',start)
function=source[start:end]
prefix=r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
typedef struct {float x,y,z,u,v,shade;} VoxelVertex;
typedef struct {VoxelVertex v[192]; unsigned count;} VoxelBuilder;
#define TEX_U(x) ((float)(x)/512)
#define TEX_V(y) (1.0f-(float)(y)/1024)
static void VoxelBuilder_Quad(VoxelBuilder *b,const VoxelVertex *a,const VoxelVertex *c,const VoxelVertex *d,const VoxelVertex *e) {
 assert(b->count+4<=192);b->v[b->count++]=*a;b->v[b->count++]=*c;b->v[b->count++]=*d;b->v[b->count++]=*e;
}
'''
suffix=r'''
int main(void) {
 VoxelBuilder b={0};
 for(int row=0;row<2;row++) for(int col=0;col<2;col++) EmitSolidCrown(&b,7+col,7+row,col,row);
 assert(b.count==160);
 float minZ=9,maxZ=7,minY=3,maxY=0;
 for(unsigned i=0;i<b.count;i++) {
  VoxelVertex v=b.v[i];assert(isfinite(v.x)&&isfinite(v.y)&&isfinite(v.z));
  assert(v.x>=7 && v.x<=9 && v.z>=7 && v.z<=9.7f);
  assert(v.u>0 && v.u<1 && v.v>0 && v.v<1);
  if(v.z<minZ)minZ=v.z;if(v.z>maxZ)maxZ=v.z;
  if(v.y<minY)minY=v.y;if(v.y>maxY)maxY=v.y;
 }
 assert(maxZ-minZ>1.8f && maxY-minY>2.0f);
 puts("PASS solid crown: all four streamed quadrants, finite bounds, depth and height");
}
'''
with tempfile.TemporaryDirectory() as tmp:
    c=Path(tmp)/'test.c';exe=Path(tmp)/'test'
    c.write_text(prefix+function+suffix)
    subprocess.run(['gcc','-std=c99','-Wall','-Wextra',str(c),'-lm','-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
