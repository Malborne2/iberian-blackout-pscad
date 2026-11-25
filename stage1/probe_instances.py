"""List the iberia4:T<a>_<b> instances on Main with geometry; also the <using> elements."""
import sys
import re
import xml.etree.ElementTree as ET

PSCX = sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\iberia4.pscx"
root = ET.parse(PSCX).getroot()
defs = root.find("definitions")
main = [e for e in defs if e.get("name") == "Main"][0]
sc = main.find("schematic")

insts = [e for e in sc if e.tag == "User" and (e.get("defn") or "").startswith("iberia4:T")]
print(f"{len(insts)} line-module instances on Main")
print(f"{'defn':10} {'id':>12} {'x':>5} {'y':>5} {'w':>4} {'h':>4} orient other-params")
for e in sorted(insts, key=lambda z: z.get("defn")):
    pl = e.find("paramlist")
    keep = {}
    if pl is not None:
        vals = {p.get("name"): p.get("value") for p in pl.findall("param")}
        keep = {k: v for k, v in vals.items()
                if k not in ("show_grid", "size", "orient", "show_border", "monitor_bus_voltage", "show_signal", "show_virtual",
                             "show_sequence", "auto_sequence", "opt_level", "compile_options", "precomp_options",
                             "include_options")
                and not k.startswith("gf_") and not k.startswith("gc_") and v not in ("0", "false", "")}
    print(f"{e.get('defn')[-8:]:10} {e.get('id'):>12} {e.get('x'):>5} {e.get('y'):>5} {e.get('w'):>4} {e.get('h'):>4} "
          f"{e.get('orient'):>4}  {keep}")

print("\n-- <using> elements --")
for u in root.iter("using"):
    print("  ", u.attrib)
