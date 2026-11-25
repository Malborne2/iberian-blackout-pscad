"""Dump the bus-33 plant group from Main (instances, labels, upramps, time-sig, DC source)."""
import sys
import xml.etree.ElementTree as ET

PSCX = sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\iberia4.pscx"
root = ET.parse(PSCX).getroot()
main = [e for e in root.find("definitions") if e.get("name") == "Main"][0]
sc = main.find("schematic")

WANT = ("iberia4:RES_Plant", "master:upramp", "master:time-sig", "master:source1",
        "master:nodelabel", "master:datalabel", "master:const", "master:pgb")


def clean(params):
    keep = {}
    for p in params.findall("param"):
        n, v = p.get("name"), p.get("value")
        if n in ("show_grid", "size", "show_border", "opt_level", "compile_options", "precomp_options",
                 "include_options") or n.startswith(("gf_", "gc_")):
            continue
        keep[n] = v
    return keep


for e in sc:
    if e.tag != "User":
        continue
    d = e.get("defn") or ""
    if d not in WANT:
        continue
    pl = e.find("paramlist")
    p = clean(pl) if pl is not None else {}
    nm = p.get("Name") or p.get("name") or ""
    print(f"{d:22} id={e.get('id'):>12} x={e.get('x'):>6} y={e.get('y'):>6} w={e.get('w'):>4} h={e.get('h'):>3} "
          f"orient={e.get('orient')} link={e.get('link')} name={nm!r}")
    if d in ("iberia4:RES_Plant", "master:upramp", "master:source1"):
        print("     ", p)
