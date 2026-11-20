#include <stdio.h>
#include "scenery_plant_geometry.h"
static int n;
static void emit(void*c,const SceneryPlantVertex*a,const SceneryPlantVertex*b,const SceneryPlantVertex*d){
 const SceneryPlantVertex*p[]={a,b,d};if(n++)printf(",\n");printf("[");
 for(int i=0;i<3;i++)printf("%s[%.8g,%.8g,%.8g,%u,%u]",i?",":"",p[i]->x,p[i]->y,p[i]->z,p[i]->ink,p[i]->shade);printf("]");
}
int main(void){printf("[\n");SceneryPlant_Emit(NULL,emit,1,1);printf("\n]\n");}
