"""Exercise the actual layer compositor with synthetic art; no ROM required."""
import ast
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'scripts/voxel_building.py'
tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
layout = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'LayoutArt')
method = next(n for n in layout.body if isinstance(n, ast.FunctionDef) and n.name == '_subtiles')
namespace = {'METATILE_ENTRIES': 12}
exec(compile(ast.Module(body=[method], type_ignores=[]), str(SOURCE), 'exec'), namespace)


class Art:
    def subtile(self, tile, palette):
        if tile == 0:
            return [(0, 0)] * 64
        if tile == 1:
            return [(100, 1)] * 64
        return [(200 + i, 2 if i == 0 else 0) for i in range(64)]


class Cell:
    ts = Art()

    def __init__(self, overlay):
        self.words = [1] * 8 + overlay

    def entries(self, _):
        return self.words


class Layers(unittest.TestCase):
    def test_third_layer_preserves_lower_ink_through_transparency(self):
        namespace['METATILE_ENTRIES'] = 12
        result = namespace['_subtiles'](Cell([2, 0, 0, 0]), 0, 1)
        self.assertEqual(result[0][0], (200, 2))
        self.assertEqual(result[0][1:], [(100, 1)] * 63)
        self.assertEqual(result[1], [(100, 1)] * 64)

    def test_flip_bits_move_upper_ink_to_opposite_corner(self):
        namespace['METATILE_ENTRIES'] = 12
        result = namespace['_subtiles'](Cell([2 | 0xC00, 0, 0, 0]), 0, 1)
        self.assertEqual(result[0][63], (200, 2))
        self.assertEqual(result[0][:63], [(100, 1)] * 63)

    def test_ground_and_two_layer_inputs_remain_unchanged(self):
        namespace['METATILE_ENTRIES'] = 12
        self.assertEqual(namespace['_subtiles'](Cell([2]*4), 0, 0), [[(100, 1)]*64]*4)
        namespace['METATILE_ENTRIES'] = 8
        self.assertEqual(namespace['_subtiles'](Cell([2]*4), 0, 1), [[(100, 1)]*64]*4)


if __name__ == '__main__':
    unittest.main()
