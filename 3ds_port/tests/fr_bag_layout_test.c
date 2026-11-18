#include <assert.h>
#include <string.h>
#include <stdio.h>

/* Pinned FRLG+ 1.5.1 pocket ABI. The production header also rejects an
 * upstream order change at compile time. */
#define POCKET_ITEMS 1
#define POCKET_MEDICINE 2
#define POCKET_KEY_ITEMS 3
#define POCKET_HELD_ITEMS 4
#define POCKET_POKE_BALLS 5
#include "fr_bag_layout.h"

int main(void)
{
    assert(NATIVE_BAG_POCKETS == 5);
    assert(!strcmp(sNativeBagPocketNames[POCKET_MEDICINE - 1], "MEDICINE"));
    assert(!strcmp(sNativeBagPocketNames[POCKET_KEY_ITEMS - 1], "KEY ITEMS"));
    assert(!strcmp(sNativeBagPocketNames[POCKET_HELD_ITEMS - 1], "HELD ITEMS"));
    assert(!strcmp(sNativeBagPocketNames[POCKET_POKE_BALLS - 1], "BALLS"));
    for (int i = 0; i < NATIVE_BAG_POCKETS; ++i)
    {
        assert(sNativeBagPocketNames[i] != NULL);
        assert(NativeBagPocketAt(BAG_TAB_Y + i * BAG_TAB_H) == i);
        assert(NativeBagPocketAt(BAG_TAB_Y + (i + 1) * BAG_TAB_H - 1) == i);
    }
    assert(NativeBagPocketAt(BAG_TAB_Y - 1) == -1);
    assert(NativeBagPocketAt(BAG_TAB_Y + NATIVE_BAG_POCKETS * BAG_TAB_H) == -1);
    assert(NativeBagPocketAt(239) == -1);
    puts("FRLG Bag: Medicine label, all five pockets and touch bounds passed");
    return 0;
}
