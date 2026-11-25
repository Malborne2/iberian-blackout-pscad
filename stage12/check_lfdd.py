r"""S26: what drives the S1..S6 ladder and does anything switch a load with it? (C5: open it.)

usage: python stage12\check_lfdd.py <pscx>
Prints every datalabel/compare on Main whose name contains S1..S6/RPOS/FREQ/UF, the compare inputs'
sources (by nearby labels), and every component whose parameters reference S1..S6 (a varrlc R, a load's
PO, a breaker's control signal ...).
"""
import sys, re, xml.etree.ElementTree as ET

src = sys.argv[1]
r = ET.parse(src).getroot()
D = {d.get("name"): d for d in r.iter("Definition")}
M = D["Main"].find("schematic")


def P(el):
    pl = el.find("paramlist")
    return {} if pl is None else {q.get("name"): q.get("value") for q in pl.findall("param")}


print("labels on Main named like S1..S6 / RPOS / FREQ / UF:")
for c in M:
    d = (c.get("defn") or "").split(":")[-1]
    p = P(c)
    nm = str(p.get("Name", ""))
    if d == "datalabel" and re.fullmatch(r"(S[1-6]|RPOS|FREQ|UF\d?|F[0-9])", nm):
        print(f"  {nm:6s} at ({int(c.get('x'))//18},{int(c.get('y'))//18}) id={c.get('id')}")

print("\nparameters that reference S1..S6 as a signal (any component):")
for c in M:
    for k, v in P(c).items():
        if isinstance(v, str) and re.fullmatch(r"S[1-6]", v):
            print(f"  {(c.get('defn') or '?').split(':')[-1]:14s} id={c.get('id')} {k} = {v}")

print("\ncompares/delays in rows 370-400 (the ladder), with X:")
for c in M:
    d = (c.get("defn") or "").split(":")[-1]
    if d in ("compare", "delay", "hardlimit") and c.get("x"):
        y = int(c.get("y")) / 18.0
        if 360 <= y <= 400:
            p = P(c)
            print(f"  {d:10s} id={c.get('id')} x={int(c.get('x'))//18:3d} y={y:3.0f} X={p.get('X')} T={p.get('T')}")
