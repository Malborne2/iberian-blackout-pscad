"""Print the SyncUnit definition XML out of iberia3.pscx (read-only inspection)."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\iberia3.pscx")
NAME = sys.argv[2] if len(sys.argv) > 2 else "SyncUnit"

tree = ET.parse(SRC)
root = tree.getroot()
for d in root.iter("Definition"):
    if d.get("name") == NAME:
        print(ET.tostring(d, encoding="unicode"))
        break
else:
    print("not found; definitions:", [d.get("name") for d in root.iter("Definition")])
