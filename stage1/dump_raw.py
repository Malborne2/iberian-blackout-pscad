"""Print the raw XML of the components inside a definition (to copy exact encoding)."""
import sys
import xml.etree.ElementTree as ET

PSCX = sys.argv[1]
NAME = sys.argv[2]
root = ET.parse(PSCX).getroot()
d = [e for e in root.find("definitions") if e.get("name") == NAME][0]
sc = d.find("schematic")
for e in sc:
    if e.tag in ("User", "Wire"):
        print(ET.tostring(e, encoding="unicode")[:2500])
        print()
