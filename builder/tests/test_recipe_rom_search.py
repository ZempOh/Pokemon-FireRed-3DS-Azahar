"""The recipe's indexed search keeps exact byte.find semantics."""

import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from gen_recipe import RomSearch


class RomSearchTest(unittest.TestCase):
    def test_all_alignments_and_repeated_words(self):
        rng = random.Random(124)
        rom = bytes(2048) + rng.randbytes(1025) + b"southern edge"
        search = RomSearch(rom)
        for start in (0, 1, 2, 3, 2044, 2047, 2100, 2101, 2102, 2103, len(rom) - 10):
            for width in (0, 1, 6, 7, 8, 16, 40, 128):
                needle = rom[start:start + width]
                self.assertEqual(search.find(needle), rom.find(needle), (start, width))
                if needle:
                    near_match = needle[:-1] + bytes((needle[-1] ^ 1,))
                    self.assertEqual(search.find(near_match), rom.find(near_match), (start, width))
