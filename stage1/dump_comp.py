"""Print raw XML of the first N components of a canvas matching a defn filter."""
import sys
import xml.etree.ElementTree as ET

PSCX, CANVAS, FILT = sys.argv[1], sys.argv[2], sys.argv[3]
N = int(sys.argv[4]) if len(sys.argv) > 4 else 1
root = ET.parse(PSCX).getroot()
d = [e for e in root.find("definitions") if e.get("name") == CANVAS][0]
sc = d.find("schematic")
k = 0
for e in sc:
    if e.tag == "User" and FILT in (e.get("defn") or ""):
        s = ET.tostring(e, encoding="unicode")
        print(s[:1500])
        print()
        k += 1
        if k >= N:
            break
print("-- order of Main children tags (first 12 and last 5) --")
tags = [e.tag for e in sc]
print(tags[:12], "...", tags[-5:])
