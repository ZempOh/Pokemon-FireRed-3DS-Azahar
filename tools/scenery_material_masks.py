"""Source-palette masks: retain layer transparency and GBA tile flips."""
import struct

def visible_palette_indices(art, mid):
    split=art.numbers['metatiles'];size=art.numbers['size']
    tileset,local=(art.primary,mid) if mid<split else (art.secondary,mid-split)
    entries=struct.unpack('<'+'H'*(size//2),art.read(art.word(tileset+12)+size*local,size))
    result=[0]*256
    for layer in range(size//8):
        for y in range(16):
            for x in range(16):
                e=entries[layer*4+y//8*2+x//8];px=x&7;py=y&7
                if e&1024:px=7-px
                if e&2048:py=7-py
                offset=(e&1023)*32+py*4+px//2
                if offset>=len(art.tiledata):raise ValueError('Tile data truncated')
                index=art.tiledata[offset]>>(4*(px&1))&15
                if index:result[y*16+x]=(e>>12)*16+index
    return result

def material_rows(indices, palette_entries):
    assert len(indices)==256 and 0 not in palette_entries
    return [sum(1<<x for x in range(16) if indices[y*16+x] in palette_entries) for y in range(16)]
