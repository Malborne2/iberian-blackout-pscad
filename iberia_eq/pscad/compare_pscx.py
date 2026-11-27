r"""Compare the Main schematics of two .pscx files element by element (S30 sec 23: offline generator vs automation API).

usage: python iberia_eq\pscad\compare_pscx.py A.pscx B.pscx [--show 10]
Components are matched by (defn, x, y); for each pair every parameter value is compared. Wires and buses by
(classid, x, y, vertices). Ids, crc, w/h are ignored. Prints counts and the first --show differences of each kind.
"""
import argparse, collections
import xml.etree.ElementTree as ET

ap = argparse.ArgumentParser(); ap.add_argument("a"); ap.add_argument("b"); ap.add_argument("--show", type=int, default=10); a = ap.parse_args()
def load(p):
    r = ET.parse(p).getroot(); m = [d for d in r.iter("Definition") if d.get("name") == "Main"][0].find("schematic")
    comps, wires = collections.defaultdict(list), collections.Counter()
    for u in m:
        if u.tag == "User":
            comps[(u.get("defn"), u.get("x"), u.get("y"))].append({p.get("name"): p.get("value") for p in u.find("paramlist")})
        elif u.tag == "Wire":
            v = tuple((x.get("x"), x.get("y")) for x in u.findall("vertex"))
            nm = {p.get("name"): p.get("value") for p in u.iter("param")}.get("Name", "")
            wires[(u.get("classid"), u.get("x"), u.get("y"), v, nm)] += 1
    st = {p.get("name"): p.get("value") for p in r.find("paramlist")}
    return comps, wires, st
ca, wa, sa = load(a.a); cb, wb, sb = load(a.b)
onlya = [k for k in ca if k not in cb]; onlyb = [k for k in cb if k not in ca]
pdiff = collections.Counter(); ex = []
for k in ca:
    if k not in cb: continue
    for pa, pb in zip(sorted(ca[k], key=str), sorted(cb[k], key=str)):
        for n in set(pa) | set(pb):
            if pa.get(n) != pb.get(n):
                pdiff[(k[0], n)] += 1
                if len(ex) < a.show: ex.append((k, n, pa.get(n), pb.get(n)))
print(f"components: A {sum(map(len, ca.values()))}, B {sum(map(len, cb.values()))}; positions only in A {len(onlya)}, only in B {len(onlyb)}")
for k in onlya[:a.show]: print("  only A:", k)
for k in onlyb[:a.show]: print("  only B:", k)
print(f"parameter differences: {sum(pdiff.values())}"); [print("  ", k, n) for k, n in pdiff.most_common(a.show)]
for e in ex: print("  e.g.", e)
dw = (wa - wb) + (wb - wa)
print(f"wires/buses: A {sum(wa.values())}, B {sum(wb.values())}, differing {sum(dw.values())}"); [print("  ", k) for k in list(dw)[:a.show]]
print("settings differing:", {k: (sa.get(k), sb.get(k)) for k in set(sa) | set(sb) if sa.get(k) != sb.get(k) and k in
      ("time_duration", "time_step", "sample_step", "PlotType", "StartType", "SnapType")})
