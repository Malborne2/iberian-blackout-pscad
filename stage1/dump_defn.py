"""Dump one definition of iberia4.pscx concisely (WP2 inspection)."""
import sys
import xml.etree.ElementTree as ET

PSCX = sys.argv[1]
NAME = sys.argv[2]
root = ET.parse(PSCX).getroot()
defs = root.find("definitions")
d = [e for e in defs if e.get("name") == NAME][0]
print("DEFN", NAME, d.get("classid"), "id", d.get("id"))
sc = d.find("schematic")
for e in sc:
    print(" ", e.tag, e.get("classid"), "name=", e.get("name"), "x=", e.get("x"), "y=", e.get("y"),
          "w=", e.get("w"), "h=", e.get("h"), "orient=", e.get("orient"), "id=", e.get("id"))
    pl = e.find("paramlist")
    if pl is not None:
        vals = {p.get("name"): p.get("value") for p in pl.findall("param")}
        keep = {k: v for k, v in vals.items()
                if k not in ("show_grid", "size", "orient", "show_border") and not k.startswith("gf_") and not k.startswith("gc_")}
        if keep:
            print("      params:", keep)
print("-- graphics --")
g = d.find("graphics")
for e in g:
    print(" ", e.tag, e.attrib)
    for sub in e:
        print("    ", sub.tag, sub.attrib)
