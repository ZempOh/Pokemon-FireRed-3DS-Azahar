from pathlib import Path
import subprocess, tempfile
p=Path(__file__).resolve().parents[1]/"src/voxel/voxel_camera.c"
s=p.read_text(); start=s.index("static void AdaptDistance"); end=s.index("\nvoid VoxelCamera_Snap",start)
harness="""#include <assert.h>
#include <stdbool.h>
typedef struct {float distance,pitch,yaw;} VoxelCamera;
static int width=20,height=20; static bool connected=true;
static void VoxelWorld_GetMapDimensions(int *w,int *h){*w=width;*h=height;}
static bool VoxelWorld_MapIsConnected(void){return connected;}
static int CtrSettings_VoxelZoom(void){return 100;}
static int CtrSettings_VoxelPitch(void){return 40;}
"""+s[start:end]+"""
int main(void){VoxelCamera c;AdaptDistance(&c);float town=c.distance;
width=80;height=60;AdaptDistance(&c);assert(c.distance==town);
connected=false;width=10;height=10;AdaptDistance(&c);assert(c.distance<town);}
"""
with tempfile.TemporaryDirectory() as d:
    c=Path(d)/"camera.c"; exe=Path(d)/"camera.exe"; c.write_text(harness)
    subprocess.run(["gcc","-std=c99","-Wall","-Wextra","-Werror",str(c),"-o",str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print("camera: connected town/route framing stable, interiors retain zoom")
