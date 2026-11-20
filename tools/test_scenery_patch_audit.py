import struct,unittest,zlib
from scenery_patch_audit import audit,require_match

class PatchAuditTest(unittest.TestCase):
    def patch(self,magic=b'BPS1'):
        p=magic+b'fixture'+struct.pack('<II',zlib.crc32(b'source'),zlib.crc32(b'target'))
        return p+struct.pack('<I',zlib.crc32(p))
    def test_all_three_checksums_required(self):
        for magic in (b'BPS1',b'UPS1'):
            self.assertTrue(require_match(b'source',self.patch(magic),b'target')['passed'])
            for src,patch,dst in [(b'wrong base',self.patch(magic),b'target'),
                                  (b'source',self.patch(magic),b'wrong output'),
                                  (b'source',self.patch(magic)[:-1]+b'X',b'target')]:
                with self.assertRaises(ValueError):require_match(src,patch,dst)
    def test_ips_is_not_a_checksum_pass(self):
        self.assertIsNone(audit(b'source',b'PATCHEOF',b'target')['passed'])
        with self.assertRaises(ValueError):require_match(b'source',b'PATCHEOF',b'target')
    def test_unknown_or_truncated_rejected(self):
        for p in (b'',b'BPS1',b'unknown'+bytes(30)):
            with self.assertRaises(ValueError):audit(b'source',p,b'target')

if __name__=='__main__':unittest.main()
