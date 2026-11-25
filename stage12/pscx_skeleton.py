r"""S26: print the XML skeleton of a .pscx (top-level elements and their children/params).

usage: python stage12\pscx_skeleton.py <pscx> [maxchildren]
"""
import sys, xml.etree.ElementTree as ET

src = sys.argv[1]
mx = int(sys.argv[2]) if len(sys.argv) > 2 else 12
r = ET.parse(src).getroot()
print("root:", r.tag, r.attrib)
for el in r:
    n = len(list(el))
    print(f"  <{el.tag}> children={n} attrs={el.attrib}")
    for q in list(el)[:mx]:
        if q.tag == "param":
            print(f"      param {q.get('name')} = {q.get('value')!r}")
        else:
            print(f"      <{q.tag}> {q.attrib}")
