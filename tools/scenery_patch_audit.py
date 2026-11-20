"""Independent BPS/UPS input, output and patch checksum gate.

IPS has no embedded checksum; it requires separately reviewed source/target
hashes. Never interpret the presence of a checksum as successful validation.
"""
import hashlib,struct,zlib

def audit(source,patch,target):
    result={name+'_sha256':hashlib.sha256(value).hexdigest()
            for name,value in [('source',source),('patch',patch),('target',target)]}
    if patch.startswith(b'PATCH'):
        return dict(result,format='IPS',embedded_validation=False,passed=None)
    if len(patch)<16 or patch[:4] not in (b'BPS1',b'UPS1'):
        raise ValueError('Unsupported or truncated patch')
    expected=struct.unpack('<III',patch[-12:])
    actual=tuple(zlib.crc32(data) for data in (source,target,patch[:-4]))
    return dict(result,format=patch[:3].decode(),embedded_validation=True,
                expected_crc32=[f'{x:08x}' for x in expected],
                actual_crc32=[f'{x:08x}' for x in actual],passed=actual==expected)

def require_match(source,patch,target):
    result=audit(source,patch,target)
    if result['passed'] is not True:
        raise ValueError('Patch requires matching input/output checksums or separate IPS provenance')
    return result
