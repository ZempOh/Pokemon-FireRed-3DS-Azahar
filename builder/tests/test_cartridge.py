import hashlib
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from firered3ds_builder.cartridge import fill_image, pack_slot, verify_engine_abi


def template(capacity=32, abi=0x99887766):
    # One unencrypted NCCH with one block per IVFC level and one empty file.
    ncch, romfs, level3 = 0x400, 0x800, 0x1800
    image = bytearray(0x4800)
    image[0x100:0x104] = b"NCSD"
    struct.pack_into("<II", image, 0x120, ncch // 512, (len(image) - ncch) // 512)
    image[ncch + 0x100:ncch + 0x104] = b"NCCH"
    image[ncch + 0x18F] = 4
    struct.pack_into("<III", image, ncch + 0x1B0, 2, 32, 1)
    struct.pack_into("<4sII", image, romfs, b"IVFC", 0x10000, 32)
    for level, size in enumerate((32, 32, 4096)):
        struct.pack_into("<QQI", image, romfs + 12 + 24 * level, level * 4096, size, 12)
    name = "firered3ds.pak".encode("utf-16-le")
    struct.pack_into("<10I", image, level3, 40, 0, 0, 0, 0, 0, 0, 40, 108, 160)
    struct.pack_into("<IIQQII", image, level3 + 40, 0, 0xFFFFFFFF, 4, capacity, 0xFFFFFFFF, len(name))
    image[level3 + 72:level3 + 72 + len(name)] = name
    abi_name = "abi.bin".encode("utf-16-le")
    struct.pack_into("<IIQQII", image, level3 + 100, 24, 0xFFFFFFFF, 0, 4, 0xFFFFFFFF, len(abi_name))
    image[level3 + 132:level3 + 132 + len(abi_name)] = abi_name
    struct.pack_into("<I", image, level3 + 160, abi)
    return image


class CartridgeTests(unittest.TestCase):
    def test_fills_romfs_file_and_repairs_all_hash_levels(self):
        image = template()
        ncch, romfs, level3, entry, offset, _ = pack_slot(image)
        content = b"FR3D test pack"
        fill_image(image, content)
        self.assertEqual(image[offset:offset + len(content)], content)
        self.assertEqual(struct.unpack_from("<Q", image, entry + 16)[0], len(content))
        level1, level2 = level3 + 4096, level3 + 8192
        for source, digest in [(level3, level2), (level2, level1), (level1, romfs + 96)]:
            self.assertEqual(image[digest:digest + 32], hashlib.sha256(image[source:source + 4096]).digest())
        self.assertEqual(image[ncch + 0x1E0:ncch + 0x200], hashlib.sha256(image[romfs:romfs + 512]).digest())

    def test_rejects_a_pack_larger_than_the_reserved_slot(self):
        with self.assertRaisesRegex(ValueError, "too small"):
            fill_image(template(), bytes(33))

    def test_refuses_an_encrypted_template(self):
        image = template()
        image[0x58F] = 0
        with self.assertRaisesRegex(ValueError, "encrypted"):
            fill_image(image, bytes(4))

    def test_checks_the_engine_abi_against_the_recipe(self):
        verify_engine_abi(template(), 0x99887766)
        with self.assertRaisesRegex(ValueError, "different data ABIs"):
            verify_engine_abi(template(), 0)
