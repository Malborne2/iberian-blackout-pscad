"""Distinct component definitions used on Main (and other canvases) in the pscx."""
import sys
import collections
import xml.etree.ElementTree as ET

PSCX = sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\iberia4.pscx"
root = ET.parse(PSCX).getroot()
defs = root.find("definitions")
for d in defs:
    sc = d.find("schematic")
    if sc is None:
        continue
    c = collections.Counter(e.get("defn") or e.get("name") or "?" for e in sc if e.tag == "User")
    if not c:
        continue
    print("=" * 30, d.get("name"))
    for k, v in c.most_common():
        print(f"  {v:4} {k}")
