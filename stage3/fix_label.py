"""Rename a signal label everywhere on Main (repair helper).

`TIME` is a reserved internal name in PSCAD; the WP3 placement script first used it and the build
failed with `'TIME' is a reserved internal name`. This renames every datalabel with the old name.

usage: python stage3\\fix_label.py <pscx> OLD NEW
"""
import sys
import xml.etree.ElementTree as ET

PSCX, OLD, NEW = sys.argv[1], sys.argv[2], sys.argv[3]
root = ET.parse(PSCX).getroot()
main = [e for e in root.find("definitions") if e.get("name") == "Main"][0]
sc = main.find("schematic")
n = 0
for e in sc:
    if e.tag != "User" or e.get("defn") != "master:datalabel":
        continue
    pl = e.find("paramlist")
    for p in pl.findall("param"):
        if p.get("name") == "Name" and p.get("value") == OLD:
            p.set("value", NEW)
            n += 1
            print("renamed", e.get("id"), f"({int(e.get('x')) // 18},{int(e.get('y')) // 18})")
with open(PSCX, "w", encoding="utf-8") as fh:
    fh.write(ET.tostring(root, encoding="unicode"))
print(f"{n} label(s) {OLD} -> {NEW} in {PSCX}")
