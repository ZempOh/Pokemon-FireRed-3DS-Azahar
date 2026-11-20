import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scenery_transfer import Art


class TransferTest(unittest.TestCase):
    def art(self):
        a=Art.__new__(Art)
        a.cache={}
        a.data=bytearray(32768)
        struct.pack_into('<I',a.data,4,0x08001000)
        struct.pack_into('<I',a.data,8,0x08000100)
        struct.pack_into('<I',a.data,12,0x08000300)
        struct.pack_into('<I',a.data,20,0x08000400)
        a.data[0x1020]=0x12
        struct.pack_into('<HH',a.data,0x102,0x1234,0x4567)
        struct.pack_into('<8H',a.data,0x300,*([1]*8))
        return a

    def test_material_and_attribute_changes_reject(self):
        a=self.art(); expected=a.signature(0x08000000,[0])
        a.data[0x102]^=1
        self.assertNotEqual(expected,a.signature(0x08000000,[0]))
        a=self.art();a.data[0x400]=1
        self.assertNotEqual(expected,a.signature(0x08000000,[0]))

    def test_flip_changes_asymmetric_art(self):
        a=self.art();expected=a.signature(0x08000000,[0])
        struct.pack_into('<H',a.data,0x300,1|1024)
        self.assertNotEqual(expected,a.signature(0x08000000,[0]))

    def test_secondary_and_bad_pointers_rejected(self):
        a=self.art()
        for entry in [640,7<<12]:
            struct.pack_into('<H',a.data,0x300,entry)
            with self.assertRaises(ValueError):a.signature(0x08000000,[0])
        with self.assertRaises(ValueError):a.read(0x07000000,1)
        with self.assertRaises(ValueError):a.signature(0x08000000,[640])

if __name__=='__main__':unittest.main()
