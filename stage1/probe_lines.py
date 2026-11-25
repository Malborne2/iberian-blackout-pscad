"""Probe iberia4 .pscx for the T<a>_<b> line modules (WP2).

Usage: python stage1\probe_lines.py [pscx] [--defn NAME]
"""
import sys
import xml.etree.ElementTree as ET
import collections

PSCX = r"C:\PSCAD_work\iberia4.pscx"
DEFN = None
args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--defn":
        DEFN = args[i + 1]
        i += 2
    else:
        PSCX = args[i]
        i += 1

root = ET.parse(PSCX).getroot()
print("project:", root.get("name"))

defs = root.find("definitions")
print("\n-- definitions --")
for e in defs:
    print(f"  {e.get('name'):28} id={e.get('id'):12} class={e.get('classid')} inst={e.get('instances')}")

# the hierarchy: which component ids are used on Main?
print("\n-- hierarchy --")
for e in root.find("hierarchy"):
    print(" ", e.tag, e.attrib)

if DEFN:
    d = None
    for e in defs:
        if e.get("name") == DEFN:
            d = e
            break
    print(f"\n-- definition {DEFN} --")
    if d is None:
        print("  not found")
        sys.exit(1)
    for child in d:
        print("  ", child.tag, child.attrib, "children:", len(list(child)))
        if child.tag == "schematic":
            for sub in child:
                print("     ", sub.tag, sub.attrib, len(list(sub)))
