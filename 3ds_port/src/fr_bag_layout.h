/* FRLG+'s main Bag has five pockets. TM Case and Berry Pouch have separate
 * screens and must not be confused with the five native Bag tabs. */
#ifndef FR_BAG_LAYOUT_H
#define FR_BAG_LAYOUT_H

#if POCKET_ITEMS != 1 || POCKET_MEDICINE != 2 || POCKET_KEY_ITEMS != 3 \
    || POCKET_HELD_ITEMS != 4 || POCKET_POKE_BALLS != 5
#error "Review the native Bag layout for this upstream pocket order"
#endif

#define NATIVE_BAG_POCKETS POCKET_POKE_BALLS
#define BAG_TAB_Y 30
#define BAG_TAB_H 34

static const char *const sNativeBagPocketNames[NATIVE_BAG_POCKETS] = {
    [POCKET_ITEMS - 1] = "ITEMS",
    [POCKET_MEDICINE - 1] = "MEDICINE",
    [POCKET_KEY_ITEMS - 1] = "KEY ITEMS",
    [POCKET_HELD_ITEMS - 1] = "HELD ITEMS",
    [POCKET_POKE_BALLS - 1] = "BALLS",
};

static int NativeBagPocketAt(int y)
{
    if (y < BAG_TAB_Y || y >= BAG_TAB_Y + NATIVE_BAG_POCKETS * BAG_TAB_H)
        return -1;
    return (y - BAG_TAB_Y) / BAG_TAB_H;
}

#endif
