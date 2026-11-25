"""Dump the raw XML of selected objects in a definition (to copy their exact attribute set)."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SRC = Path(sys.argv[1])
NAME = sys.argv[2]
WANT = sys.argv[3:]  # defn names

tree = ET.parse(SRC)
root = tree.getroot()
for d in root.iter("Definition"):
    if d.get("name") != NAME:
        continue
    sch = d.find("schematic")
    for u in sch.iter("User"):
        if u.get("defn") in WANT or any(w in str(u.get("defn")) for w in WANT):
            print(ET.tostring(u, encoding="unicode"))
            print("-" * 60)
    for w in sch.iter("Wire"):
        print("WIRE", ET.tostring(w, encoding="unicode")[:200])
