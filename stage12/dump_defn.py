r"""S26: dump the control blocks of a module definition from a .pscx (offline; no PSCAD API).

usage: python stage12\dump_defn.py <pscx> <definition> [block,block,...]
Shows each block's id, position and the parameters named below (defaults: the filter/controller set).
"""
import sys, xml.etree.ElementTree as ET

KEEP = {"T", "Tc", "N", "G", "Ti", "Td", "T1", "T2", "F", "Freq", "Order", "X1", "X2", "Max", "Min",
        "Limit", "Type", "Mode", "Init", "FB", "Y0", "Tdelay", "Dt", "Delay", "Kp", "Ki"}

src, defn = sys.argv[1], sys.argv[2]
want = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
r = ET.parse(src).getroot()
D = {d.get("name"): d for d in r.iter("Definition")}
S = D[defn].find("schematic")
for x in S:
    dn = x.get("defn") or "?"
    short = dn.split(":")[-1]
    if want and short not in want:
        continue
    p = {q.get("name"): q.get("value") for q in x.find("paramlist").findall("param")}
    keep = {k: v for k, v in p.items() if k in KEEP}
    if keep or (want and short in want):
        print(f"{short:12s} id={x.get('id'):>12s} x={int(x.get('x'))//18:3d} y={int(x.get('y'))//18:3d} {keep}")
