"""List the T<a>_<b> instances on Main of iberia4.pscx, with their neighbours (WP2)."""
import sys
import xml.etree.ElementTree as ET
import re

PSCX = sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\iberia4.pscx"
root = ET.parse(PSCX).getroot()
defs = root.find("definitions")
main = [e for e in defs if e.get("name") == "Main"][0]
sc = main.find("schematic")

pat = re.compile(r"^T\d+_\d+$")
insts = []
for e in sc:
    if e.tag == "User" and pat.match(e.get("defn") or ""):
        insts.append(e)

print(f"{len(insts)} line-module instances on Main")
for e in sorted(insts, key=lambda z: z.get("defn")):
    pl = e.find("paramlist")
    vals = {}
    if pl is not None:
        vals = {p.get("name"): p.get("value") for p in pl.findall("param")}
    keep = {k: v for k, v in vals.items()
            if k not in ("show_grid", "size", "orient", "show_border") and not k.startswith("gf_") and not k.startswith("gc_")}
    print(f"  {e.get('defn'):10} id={e.get('id'):12} x={e.get('x'):>5} y={e.get('y'):>5} "
          f"w={e.get('w')} h={e.get('h')} orient={e.get('orient')} link={e.get('link')} {keep}")
