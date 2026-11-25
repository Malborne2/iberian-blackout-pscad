"""Count the schematic contents of every definition in the pscx."""
import sys
import collections
import xml.etree.ElementTree as ET

PSCX = sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\iberia4.pscx"
root = ET.parse(PSCX).getroot()
defs = root.find("definitions")
for d in defs:
    sc = d.find("schematic")
    if sc is None:
        print(f"{d.get('name'):14} {d.get('classid'):12} NO SCHEMATIC")
        continue
    c = collections.Counter(e.tag for e in sc)
    print(f"{d.get('name'):14} {d.get('classid'):12} {dict(c)}")
