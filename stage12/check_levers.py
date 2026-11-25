r"""S26: read the Main-level lever values of ib6 (taps, reactors, plant Pref, load PO, unit set-points).

usage: python stage12\check_levers.py <pscx>
"""
import sys, xml.etree.ElementTree as ET

src = sys.argv[1]
r = ET.parse(src).getroot()
D = {d.get("name"): d for d in r.iter("Definition")}
M = D["Main"].find("schematic")
TAPS = {"33": "1931291851", "34": "2006720080", "35": "705661550", "36": "506809771", "38": "1387559265"}


def P(el):
    return {q.get("name"): q.get("value") for q in el.find("paramlist").findall("param")}


byid = {}
for c in M:
    byid[c.get("id")] = c

print("collector tap consts")
for b, i in TAPS.items():
    c = byid.get(i)
    print(f"  bus {b}: id {i} defn {c.get('defn') if c is not None else 'MISSING'} "
          f"{P(c) if c is not None else ''}")

print("\nreactive shunts on Main (fixed_load / rtcbranch with reactive PO or QO<0)")
for c in M:
    d = c.get("defn") or ""
    if d in ("master:fixed_load", "master:rtcbranch"):
        p = P(c)
        po = float(str(p.get("PO", "0")).split("[")[0] or 0)
        qo = float(str(p.get("QO", "0")).split("[")[0] or 0)
        if abs(qo) > 1.0 or "SH" in str(p.get("Name", "")):
            print(f"  {d.split(':')[-1]:12s} id={c.get('id')} x={int(c.get('x'))//18} y={int(c.get('y'))//18} "
                  f"Name={p.get('Name')} PO={p.get('PO')} QO={p.get('QO')}")

print("\nsignal consts whose Value looks like a tap (0.8-1.2) near rows 0-30")
for c in M:
    if (c.get("defn") or "").split(":")[-1] == "const":
        p = P(c)
        try:
            v = float(p.get("Value", "nan"))
        except ValueError:
            continue
        if 0.5 < v < 1.5:
            print(f"  const id={c.get('id')} x={int(c.get('x'))//18} y={int(c.get('y'))//18} Value={p.get('Value')}")
