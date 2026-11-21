"""Protect existing engine layouts when adding Classic's larger object records."""
from pathlib import Path
import argparse,json,re
p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True);a=p.parse_args()
source=(a.runtime/'app/src/main/cpp/pk_wide.c').read_text()
reference=json.loads((Path(__file__).parent/'scenery-profiles/native-adapter-layout-reference.json').read_text())
rows={n:[int(v.strip(),0) for v in data.split(',')] for n,data in re.findall(r'\[(PK_WIDE_FAMILY_\w+)\] = \{([^}]+)\}',source)}
assert len(reference)==9 and len(rows)==10
for name,values in reference.items():assert rows[name]==values+[36,1],name
assert rows['PK_WIDE_FAMILY_EM640_40'][-2:]==[40,255]
assert 'uint8_t objects[16 * 40]' in source
assert '16u * (uint32_t) C[PK_WIDE_OBJECT_SIZE]' in source
assert 'r8(ct + (uint32_t) C[PK_WIDE_TEMPLATE_KIND]) == C[PK_WIDE_TEMPLATE_CLONE_VALUE]' in source
assert not re.search(r's->objects\s*\+\s*0x24|F\.objects\s*\+\s*0x24u',source)
print('Nine existing object layouts preserved; Classic stride and clone marker isolated')
