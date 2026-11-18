"""Signposts: the sign event rule, eventless posts (street lamps) and the sign
silhouette, on synthetic cells and on real maps."""

import pathlib
import sys
import types

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import voxel_cells  # noqa: E402
from gen_voxel_sign_masks import sign_record  # noqa: E402
from voxel_sign_mask import cutout_mask  # noqa: E402


class FakeLayout:
    is_signpost = voxel_cells.Layout.is_signpost
    open_post = voxel_cells.Layout.open_post
    free_post = voxel_cells.Layout.free_post
    drawn_as_post = voxel_cells.Layout.drawn_as_post
    primary, secondary = "primary", "secondary"

    def __init__(self, blocked, signs, outdoor=True, drawn=None, covering=(), posts=(),
                 copies=()):
        self.events = types.SimpleNamespace(posts={("primary", m) for m in posts})
        self._copies = set(copies)
        self.w = len(blocked[0])
        self.h = len(blocked)
        self.outdoor = outdoor
        self.signs = signs
        self._blocked = blocked
        self._drawn = drawn or [[0] * self.w for _ in range(self.h)]
        self._covering = set(covering)

    def metatile(self, x, y):
        return None if self.off_map(x, y) else self._drawn[y][x]

    def covers(self, metatile):
        return metatile in self._covering

    def draws_post_sign(self, metatile):
        return metatile in self._copies

    def foliage(self, metatile):
        return 0.0

    def houses(self):
        return set()

    def lamps(self):
        return set()

    def off_map(self, x, y):
        return x < 0 or y < 0 or x >= self.w or y >= self.h

    def blocked(self, x, y):
        return False if self.off_map(x, y) else self._blocked[y][x]


def run():
    # An enclosed transparent pocket survives the outside flood.
    rows = cutout_mask({(x, y) for x in range(3) for y in range(3) if (x, y) != (1, 1)}, 3, 3)
    assert rows[1] & (1 << 1)
    # A board that fills its cell is all sign.
    assert cutout_mask({(x, y): 1 for x in range(16) for y in range(16)}) == [65535] * 16

    blocked = [[False] * 3 for _ in range(3)]
    blocked[1][1] = True
    blocked[0][1] = True  # a building behind the sign is allowed
    assert FakeLayout(blocked, {(1, 1)}).is_signpost(1, 1)
    # No event: a post if it does not cover the player and differs from
    # what stands north of it (a lamp); not a boulder, nor a fence's run.
    drawn = [[0, 2, 0], [0, 1, 0], [0, 0, 0]]
    assert FakeLayout(blocked, set(), drawn=drawn).is_signpost(1, 1)
    assert not FakeLayout(blocked, set(), drawn=drawn, covering={1}).is_signpost(1, 1)
    drawn[0][1] = 1
    assert not FakeLayout(blocked, set(), drawn=drawn).is_signpost(1, 1)
    assert not FakeLayout(blocked, {(1, 1)}, outdoor=False).is_signpost(1, 1)
    blocked[1][0] = True
    assert not FakeLayout(blocked, {(1, 1)}).is_signpost(1, 1)         # a side is closed
    # ...unless it is drawn as a sign stands elsewhere, open on three sides:
    # a house's sign against its wall
    drawn = [[0, 2, 0], [0, 3, 0], [0, 0, 0]]
    assert FakeLayout(blocked, {(1, 1)}, drawn=drawn, posts={3}).is_signpost(1, 1)
    # ...or as its sign is, in another tileset's metatile
    assert FakeLayout(blocked, {(1, 1)}, drawn=drawn, copies={3}).is_signpost(1, 1)
    blocked[2][1] = True
    assert not FakeLayout(blocked, {(1, 1)}, drawn=drawn, posts={3}).is_signpost(1, 1)
    assert not FakeLayout(blocked, {(1, 1)}, drawn=drawn, copies={3}).is_signpost(1, 1)

    events = voxel_cells.MapEvents()
    layouts = {entry["id"]: entry for entry in voxel_cells.load_layouts()}
    opening_signs = {
        "LAYOUT_PALLET_TOWN": {(9, 11), (5, 14), (16, 16)},
        "LAYOUT_ROUTE1": {(9, 31)},
        "LAYOUT_VIRIDIAN_CITY": {(23, 9), (32, 18), (20, 24), (20, 39)},
    }
    for name, signs in opening_signs.items():
        layout = voxel_cells.Layout(layouts[name], events)
        pair = voxel_cells.pair_for(layout.primary, layout.secondary)
        for x, y in signs:
            assert (x, y) in layout.signs and layout.role_at(x, y) == "signpost", (name, x, y)
            rows, _, _, _ = sign_record(layout, pair, x, y)
            assert any(rows), (name, x, y)
            for px, py in pair.layer_pixels(layout.metatile(x, y), 1):
                assert rows[py] & (1 << px), (name, x, y, px, py)
    print("PASS voxel signpost: sign events, lamps, open sides, and Classic's opening signs")


if __name__ == "__main__":
    run()
