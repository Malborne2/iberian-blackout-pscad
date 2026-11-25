r"""S26: dump one component's raw XML by id (learn the wire/port geometry format).

usage: python stage12\dump_el.py <pscx> <definition> <id> [<id> ...]
"""
import sys, xml.etree.ElementTree as ET

src, defn = sys.argv[1], sys.argv[2]
r = ET.parse(src).getroot()
D = {d.get("name"): d for d in r.iter("Definition")}
S = D[defn].find("schematic")
want = set(sys.argv[3:])
for c in S:
    if c.get("id") in want:
        print(ET.tostring(c, encoding="unicode")[:2500])
        print("---")
