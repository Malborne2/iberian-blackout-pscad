"""Show sample wire encodings on a canvas, grouped by vertex geometry."""
import sys
import collections
import xml.etree.ElementTree as ET

PSCX = sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\iberia4.pscx"
CANVAS = sys.argv[2] if len(sys.argv) > 2 else "Main"
root = ET.parse(PSCX).getroot()
d = [e for e in root.find("definitions") if e.get("name") == CANVAS][0]
sc = d.find("schematic")

groups = collections.defaultdict(list)
for e in sc:
    if e.tag != "Wire":
        continue
    vs = tuple((v.get("x"), v.get("y")) for v in e.findall("vertex"))
    key = (e.get("orient"), vs)
    groups[key].append(e)

for (orient, vs), lst in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    e = lst[0]
    print(f"n={len(lst):3} orient={orient} verts={vs}  x={e.get('x')} y={e.get('y')} w={e.get('w')} h={e.get('h')} "
          f"class={e.get('classid')}")
