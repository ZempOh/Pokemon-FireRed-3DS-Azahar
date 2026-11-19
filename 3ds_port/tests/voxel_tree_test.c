/* Exercise the real mesh emitters with a tiny world crossing four chunks. */
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

#include "voxel_tileset_fixture.h"

#include "voxel_tree.h"
#include "voxel_atlas.h"
#include "voxel_regions.h"

/* voxel_tree.c compares the map's secondary tileset with this object to
 * recognise Dewford's tree art; this test never uses that art, so an empty
 * tileset is enough for the link. */
const struct Tileset gTileset_Dewford = {0};
const struct Tileset gTileset_Fortree = {0};
const struct Tileset gTileset_Mauville = {0};
const struct Tileset gTileset_Lavaridge = {0};
const struct Tileset gTileset_Rustboro = {0};
const struct Tileset gTileset_Lilycove = {0};
const struct Tileset gTileset_EverGrande = {0};
const struct Tileset gTileset_BattleFrontierOutsideWest = {0};
const struct Tileset gTileset_Mossdeep = {0};
const struct Tileset gTileset_Fallarbor = {0};

static VoxelMapInstance sMap = {.originX = 7, .originY = 7, .width = 2, .height = 2};
static bool sGeneral = true;
static unsigned sBehavior;
/* Actual Pallet Town / Route 1 forest quadrants from Classic's bank. */
static int sTiles[] = {0x01C, 0x01D, 0x014, 0x015};
static VoxelAtlasMap sAtlas;
static VoxelVertex sWhole[4096], sParts[4096];

bool VoxelWorld_UsesTreeSprites(const VoxelMapInstance *inst)
{
    return inst == &sMap && sGeneral;
}

const VoxelMapInstance *VoxelWorld_Instance(unsigned index)
{
    return index == 0 ? &sMap : NULL;
}

const VoxelMapInstance *VoxelWorld_GetInstanceAt(int x, int y)
{
    return x >= sMap.originX && x < sMap.originX + 2
        && y >= sMap.originY && y < sMap.originY + 2 ? &sMap : NULL;
}

int VoxelWorld_GetMetatileId(int x, int y)
{
    assert(VoxelWorld_GetInstanceAt(x, y) != NULL);
    return sTiles[(y - sMap.originY) * 2 + x - sMap.originX];
}

VoxelVisualShape VoxelWorld_ClassifyTile(int x, int y)
{
    return VoxelWorld_GetInstanceAt(x, y) ? VOXEL_SHAPE_FLAT : VOXEL_SHAPE_VOID;
}

int VoxelWorld_BorderMetatile(int x, int y)
{
    const int pattern[] = {0x01C, 0x01D, 0x014, 0x015};
    return pattern[((x - sMap.originX) & 1) + 2 * ((y - sMap.originY) & 1)];
}

bool VoxelWorld_BorderIsWater(int x, int y) { (void)x; (void)y; return false; }

void VoxelWorld_GetPlayerWorldCoords(float *x, float *z) { *x = *z = 0; }

unsigned VoxelRegions_RoleAt(unsigned layoutId, int x, int y)
{
    (void)layoutId; (void)x; (void)y;
    return VOXEL_ROLE_TREE;
}

void VoxelAtlas_SlotUV(unsigned slot, float *u0, float *v0, float *u1, float *v1)
{
    *u0 = (slot % 32) / 32.0f;
    *v0 = 1.0f - (slot / 32) / 16.0f;
    *u1 = *u0 + 1.0f / 32;
    *v1 = *v0 - 1.0f / 16;
}

void VoxelAtlas_SolidUV(VoxelSolidColor color, float *u0, float *v0, float *u1, float *v1)
{
    VoxelAtlas_SlotUV((unsigned)color, u0, v0, u1, v1);
}

static void Init(VoxelBuilder *b, VoxelVertex *v)
{
    VoxelBuilder_Init(b, v, 4096);
    VoxelBuilder_SetAtlas(b, &sAtlas);
    VoxelBuilder_SetOrigin(b, sMap.originX, sMap.originY);
    VoxelMesh_BeginWindow(sMap.originX - 2, sMap.originY - 2,
                          sMap.originX + 4, sMap.originY + 4);
}

int main(void)
{
    VoxelBuilder whole, parts;
    unsigned ground = 0, crown = 0;

    Init(&whole, sWhole);
    VoxelMesh_EmitInstance(&whole, &sMap, 7, 7, 9, 9);
    assert(whole.count == 0); /* no original ground artwork or extruded region */
    VoxelTree_EmitInstance(&whole, &sMap, 7, 7, 9, 9);
    assert(whole.count == 264 && whole.dropped == 0);
    for (unsigned i = 0; i < whole.count; ++i)
    {
        const VoxelVertex *v = &whole.vertices[i];
        assert(isfinite(v->x) && isfinite(v->y) && isfinite(v->z));
        assert(v->x >= 0 && v->x <= 2 && v->v >= 0 && v->v <= 1);
        if (v->y == 0)
        {
            ++ground;
            assert(v->u >= 32.0f / VOXEL_TREE_TEXTURE_DIM
                && v->u <= 64.0f / VOXEL_TREE_TEXTURE_DIM && v->z >= 0 && v->z <= 2);
        }
        else
        {
            ++crown;
            assert(v->u >= 0 && v->u <= 64.0f / VOXEL_TREE_TEXTURE_DIM);
        }
    }
    assert(ground == 24 && crown == 240);
    assert(sWhole[6].y < sWhole[8].y); /* solid side rises */

    Init(&parts, sParts);
    for (int y = 0; y < 2; ++y)
        for (int x = 0; x < 2; ++x)
            VoxelTree_EmitInstance(&parts, &sMap, x * 8, y * 8, (x + 1) * 8, (y + 1) * 8);
    assert(parts.count == whole.count);
    assert(memcmp(sWhole, sParts, whole.count * sizeof(VoxelVertex)) == 0);

    /* Streaming emits one cell per slice; preserve vertices and order. */
    Init(&parts, sParts);
    for (int y = 0; y < 2; ++y)
        for (int x = 0; x < 2; ++x)
            VoxelTree_EmitInstance(&parts, &sMap, x + 7, y + 7, x + 8, y + 8);
    assert(parts.count == whole.count);
    assert(memcmp(sWhole, sParts, whole.count * sizeof(VoxelVertex)) == 0);

    /* A map crossing changes the origin, not the cached local mesh. */
    sMap.originX = -3;
    sMap.originY = -5;
    Init(&parts, sParts);
    VoxelTree_EmitInstance(&parts, &sMap, -3, -5, -1, -3);
    assert(parts.count == whole.count);
    for (unsigned i = 0; i < whole.count; ++i)
    {
        assert(fabsf(sWhole[i].x - sParts[i].x) < 0.00001f);
        assert(fabsf(sWhole[i].y - sParts[i].y) < 0.00001f);
        assert(fabsf(sWhole[i].z - sParts[i].z) < 0.00001f);
    }

    /* Border excludes every mapped cell, including at negative coordinates. */
    Init(&parts, sParts);
    VoxelMesh_BeginWindow(-5, -7, 1, 1);
    VoxelMesh_EmitBorder(&parts, -5, -7, 1, 1);
    assert(parts.count == 0); /* no raised belt under the replacement */
    VoxelTree_EmitBorder(&parts, -5, -7, 1, 1);
    assert(parts.count == (6 * 8 - 4) * 66 && parts.dropped == 0);
    /* Each repeated cell supplies one opaque ground quad and eight crown faces and two trunk faces,
     * even across a chunk edge. No alternating grass/empty cell remains. */
    for (unsigned i = 0; i < parts.count; i += 66)
    {
        for (unsigned j = 0; j < 6; ++j)
            assert(parts.vertices[i + j].y == 0);
        assert(parts.vertices[i + 6].y < parts.vertices[i + 8].y);
        assert(parts.vertices[i + 6].u < 32.0f / VOXEL_TREE_TEXTURE_DIM);
    }

    unsigned borderCount = parts.count;
    memcpy(sWhole, sParts, borderCount * sizeof(VoxelVertex));
    Init(&parts, sParts);
    for (int y = -7; y < 1; ++y)
        for (int x = -5; x < 1; ++x)
            VoxelTree_EmitBorder(&parts, x, y, x + 1, y + 1);
    assert(parts.count == borderCount);
    assert(memcmp(sWhole, sParts, borderCount * sizeof(VoxelVertex)) == 0);

    sGeneral = false;
    Init(&parts, sParts);
    VoxelTree_EmitInstance(&parts, &sMap, -3, -5, -1, -3);
    VoxelTree_EmitBorder(&parts, -5, -7, 1, 1);
    assert(parts.count == 0);
    assert(VoxelTree_Part(NULL, 0x02E) == -1); /* a pine, still its own art */
    assert(VoxelTree_Part(NULL, 0x1D9) == -1); /* rock */

    /* Grass fringes lose the old canopy and never acquire region walls. */
    sGeneral = true;
    sTiles[0] = 0x1CE; sTiles[1] = 0x1CF;
    sTiles[2] = 0x1C6; sTiles[3] = 0x1C7;
    sAtlas.slotOf[0x001] = 1;
    sAtlas.slotOf[0x00D] = 2;
    Init(&parts, sParts);
    VoxelMesh_EmitInstance(&parts, &sMap, -3, -5, -1, -3);
    VoxelTree_EmitInstance(&parts, &sMap, -3, -5, -1, -3);
    assert(parts.count == 24 && parts.uncovered == 0);
    for (unsigned i = 0; i < parts.count; ++i)
        assert(parts.vertices[i].y == 0);

    /* Small trees: the canopy top keeps its ground; each trunk cell - edge of
     * a wood or inside it - lays the trunk and stands the whole crown on it. */
    sTiles[0] = 0x00E; sTiles[1] = 0x00F;
    sTiles[2] = 0x0C6; sTiles[3] = 0x0C7;
    assert(VoxelTree_GroundMetatile(NULL, 0x00E) == 0x001);
    assert(VoxelTree_Part(NULL, 0x0C6) == VOXEL_TREE_SMALL);
    assert(VoxelTree_Part(NULL, 0x1EC) == 2 && VoxelTree_Part(NULL, 0x1ED) == 3);
    assert(VoxelTree_Part(&gTileset_Dewford, 0x23A) == VOXEL_TREE_SMALL);
    assert(VoxelTree_Part(&gTileset_Dewford, 0x243) == VOXEL_TREE_SMALL);
    assert(VoxelTree_Part(NULL, 0x23A) == -1 && VoxelTree_Part(NULL, 0x243) == -1);
    assert(VoxelTree_GroundMetatile(&gTileset_Dewford, 0x239) == 0x124);
    assert(VoxelTree_GroundMetatile(NULL, 0x239) == 0x239);
    /* The General's small tree on a secondary tileset's ground, and only
     * there: the same ids are other drawings on any other map. */
    assert(VoxelTree_Part(&gTileset_Fortree, 0x253) == VOXEL_TREE_SMALL);
    assert(VoxelTree_Part(&gTileset_Mauville, 0x226) == VOXEL_TREE_SMALL);
    assert(VoxelTree_Part(&gTileset_Lavaridge, 0x218) == VOXEL_TREE_SMALL);
    assert(VoxelTree_Part(&gTileset_Lavaridge, 0x253) == -1 && VoxelTree_Part(NULL, 0x226) == -1);
    assert(VoxelTree_GroundMetatile(&gTileset_Rustboro, 0x2C0) == 0x079);
    assert(VoxelTree_GroundMetatile(&gTileset_Lilycove, 0x2C0) == 0x2C0);
    /* Kanto's standalone, edge and repeated trees share paired quadrants. */
    assert(VoxelTree_Part(NULL, 0x01C) == 0 && VoxelTree_Part(NULL, 0x01D) == 1);
    assert(VoxelTree_Part(NULL, 0x014) == 2 && VoxelTree_Part(NULL, 0x015) == 3);
    assert(VoxelTree_Part(NULL, 0x016) == 2 && VoxelTree_Part(NULL, 0x017) == 3);
    assert(VoxelTree_Part(NULL, 0x024) == 2 && VoxelTree_Part(NULL, 0x025) == 3);
    assert(VoxelTree_GroundMetatile(NULL, 0x01D) == 0x01D);
    assert(VoxelTree_GroundMetatile(NULL, 0x025) == 0x025);
    assert(VoxelTree_Part(NULL, 0x01E) == 0 && VoxelTree_Part(NULL, 0x01F) == 1);
    assert(VoxelTree_Part(NULL, 0x026) == 2 && VoxelTree_Part(NULL, 0x027) == 3);
    assert(VoxelTree_Part(NULL, 0x036) == 2 && VoxelTree_Part(NULL, 0x037) == 3);
    /* A secondary tileset's own 2x2 trees: the trunk row (also where it
     * holds the next tree's crown top) is the part, the crown row its plain
     * ground; a trunk in Mossdeep's shallows leaves the water to the ground
     * pass. */
    assert(VoxelTree_Part(&gTileset_Mossdeep, 0x324) == 2 && VoxelTree_Part(&gTileset_Mossdeep, 0x356) == 3);
    assert(VoxelTree_Part(&gTileset_Mossdeep, 0x31C) == -1);
    assert(VoxelTree_GroundMetatile(&gTileset_Mossdeep, 0x31C) == 0x07C);
    assert(VoxelTree_GroundMetatile(&gTileset_Mossdeep, 0x2F8) == 0x19E);
    assert(!VoxelTree_LaysGround(&gTileset_Mossdeep, 0x2F8) && VoxelTree_LaysGround(&gTileset_Mossdeep, 0x322));
    assert(VoxelTree_Part(&gTileset_Fallarbor, 0x26B) == 3 && VoxelTree_Part(&gTileset_Fallarbor, 0x275) == 2);
    assert(VoxelTree_Part(&gTileset_Fallarbor, 0x204) == -1);
    assert(VoxelTree_GroundMetatile(&gTileset_Fallarbor, 0x204) == 0x218);
    assert(VoxelTree_Part(&gTileset_Mossdeep, 0x26B) == -1 && VoxelTree_Part(NULL, 0x324) == -1);
    /* Fortree's wood under its decks and bridges: small trees, its own
     * tileset only; its canopy and palm cells give their ground back */
    assert(VoxelTree_Part(&gTileset_Fortree, 0x23C) == VOXEL_TREE_SMALL);
    assert(VoxelTree_Part(&gTileset_Fortree, 0x256) == VOXEL_TREE_SMALL);
    assert(VoxelTree_Part(&gTileset_Fortree, 0x243) == VOXEL_TREE_SMALL);
    assert(VoxelTree_Part(&gTileset_Fortree, 0x24E) == -1);
    assert(VoxelTree_Part(&gTileset_Dewford, 0x23C) == -1 && VoxelTree_Part(NULL, 0x256) == -1);
    assert(VoxelTree_GroundMetatile(&gTileset_Fortree, 0x244) == 0x001);
    assert(VoxelTree_GroundMetatile(&gTileset_Fortree, 0x273) == 0x001);
    assert(VoxelTree_GroundMetatile(&gTileset_Fortree, 0x24B) == 0x261);
    assert(VoxelTree_GroundMetatile(&gTileset_Dewford, 0x244) == 0x244);
    Init(&parts, sParts);
    VoxelMesh_EmitInstance(&parts, &sMap, -3, -5, -1, -3);
    assert(parts.count == 12 && parts.uncovered == 0); /* two grass tops */
    for (unsigned i = 0; i < parts.count; ++i)
        assert(parts.vertices[i].y == 0 && parts.vertices[i].z <= 1);
    parts.count = 0;
    VoxelTree_EmitInstance(&parts, &sMap, -3, -5, -1, -3);
    assert(parts.count == 24 && parts.dropped == 0);
    for (unsigned i = 0; i < parts.count; ++i)
    {
        const VoxelVertex *v = &parts.vertices[i];
        assert(v->u >= 32.0f / VOXEL_TREE_TEXTURE_DIM
            && v->u <= 64.0f / VOXEL_TREE_TEXTURE_DIM
            && v->v >= 1.0f - 64.0f / VOXEL_TREE_TEXTURE_DIM
            && v->v <= 1.0f - 32.0f / VOXEL_TREE_TEXTURE_DIM);
        if (v->y == 0)
            assert(v->u >= 48.0f / VOXEL_TREE_TEXTURE_DIM
                && v->v >= 1.0f - 48.0f / VOXEL_TREE_TEXTURE_DIM && v->z >= 1 && v->z <= 2);
        else
            assert(v->u <= 48.0f / VOXEL_TREE_TEXTURE_DIM);
    }
    /* Leaning north from its trunk into the cell above, as tall as it is long. */
    assert(parts.vertices[6].z < parts.vertices[8].z && parts.vertices[6].y > parts.vertices[8].y);
    assert(parts.vertices[6].z < 1 && fabsf(parts.vertices[6].y - 1.432089f) < 0.0001f);

    /* A staggered wood's lower row is a whole tree: trunks and both rows. */
    assert(VoxelTree_Part(NULL, 0x1F3) == 2 && VoxelTree_Part(NULL, 0x1F2) == 3);
    assert(VoxelTree_Part(NULL, 0x1FC) == 0 && VoxelTree_Part(NULL, 0x1FD) == 1);
    sTiles[0] = 0x1D4; sTiles[1] = 0x1D5;
    sTiles[2] = 0x1F3; sTiles[3] = 0x1F2;
    Init(&parts, sParts);
    VoxelTree_EmitInstance(&parts, &sMap, -3, -5, -1, -3);
    assert(parts.count == 4 * 66 && parts.dropped == 0);

    /* A roof over the lower row: the crown keeps that row, its ground does
     * not become a trunk. */
    sTiles[2] = 0x008; sTiles[3] = 0x009;
    Init(&parts, sParts);
    VoxelTree_EmitInstance(&parts, &sMap, -3, -5, -1, -3);
    assert(parts.count == 2 * 66 + 2 * 60 && parts.dropped == 0);
    for (unsigned i = 0; i < parts.count; ++i)
        if (parts.vertices[i].y == 0 && parts.vertices[i].u >= 32.0f / VOXEL_TREE_TEXTURE_DIM)
            assert(parts.vertices[i].z <= 8); /* trunk ground only in the tree's row */

    /* Grass retains a floor and has real height and depth, including at a
     * streamed chunk edge. The bounded mesh must fit the staging buffer. */
    sMap.secondaryTileset=&gTileset_Fortree;
    for(int i=0;i<4;i++)sTiles[i]=0x208;
    Init(&parts,sParts);
    VoxelTree_EmitInstance(&parts,&sMap,-3,-5,-1,-3);
    assert(parts.dropped==0 && parts.count>24);
    unsigned floor=0,raised=0;
    for(unsigned i=0;i<parts.count;i++) {
        assert(isfinite(parts.vertices[i].x)&&isfinite(parts.vertices[i].y)&&isfinite(parts.vertices[i].z));
        if(parts.vertices[i].y==0)floor++;
        if(parts.vertices[i].y>.4f)raised++;
    }
    assert(floor>=24 && raised>=28);
    /* Ordinary encounter grass follows behavior metadata, not reused art IDs. */
    sMap.secondaryTileset=NULL;
    for(int i=0;i<4;i++)sTiles[i]=0x001;
    sBehavior=2;
    Init(&parts,sParts);
    VoxelTree_EmitInstance(&parts,&sMap,-3,-5,-1,-3);
    assert(parts.dropped==0 && parts.count==4*84);
    sBehavior=0;
    Init(&parts,sParts);
    VoxelTree_EmitInstance(&parts,&sMap,-3,-5,-1,-3);
    assert(parts.count==0);
    puts("PASS voxel trees and volumetric grass: streamed bounds, ground, height, seams and tileset scope");
    return 0;
}

unsigned VoxelWorld_GetMetatileBehavior(int x,int y){(void)x;(void)y;return sBehavior;}
