r"""S27 Batch-2b build: OV-relay measurement filter `Trel` in RES_Plant (stage 1), applied to the s28 case.

Why (Case B2, S27): the 1.10 pu / 0 s relays fired on the peaks of the 20 µs numerical 17 Hz collector mode
(D26-1), 39 ms after event 4a, with a mean voltage of 1.065 pu. A relay measures through a filter; here VMEAS
(VDF, or POI RMS with MeasSide 1) passes a first-order lag `Trel` [s] before the stage-1 compare.
`Trel` is a per-step argument of RES_PlantDyn (LIVE from a snapshot, stage12/snap_live.py), so it can be
bracketed per event run without a re-settle. Default 0.001 s = practically no filter (old behaviour).

usage: python stage12/add_bundle_s29.py <in.pscx> <out.pscx>
"""
import copy, random, sys, xml.etree.ElementTree as ET

G = 18
root = ET.parse(sys.argv[1]).getroot()
D = {d.get("name"): d for d in root.iter("Definition")}
R = D["RES_Plant"]; S = R.find("schematic")
used = {e.get("id") for e in root.iter() if e.get("id")}
rnd = random.Random(29)


def nid():
    while True:
        i = str(rnd.randint(1_000_000_000, 2_100_000_000))
        if i not in used: used.add(i); return i


def P(el):
    return {q.get("name"): q for q in el.find("paramlist").findall("param")}


byid = {e.get("id"): e for e in S if e.get("id")}
# 1. the stage-1 compare now reads VMF instead of VMEAS
lab = byid["1350000063"]; assert P(lab)["Name"].get("value") == "VMEAS" and (lab.get("x"), lab.get("y")) == ("216", "2736")
P(lab)["Name"].set("value", "VMF")
# 2. VMEAS -> realpole(G 1, T Trel) -> VMF, at (52..56, 100) grid (936..1008, 1800 px): free, checked
occ = {(e.get("x"), e.get("y")) for e in S if e.get("x")}
for x in ("936", "972", "1008"): assert (x, "1800") not in occ, x
rp = next(e for e in S if e.get("defn") == "master:realpole" and P(e)["T"].get("value") == "0.008")
dl = next(e for e in S if e.get("defn") == "master:datalabel")


def put(tmpl, x, y, **v):
    e = copy.deepcopy(tmpl); e.set("id", nid()); e.set("x", str(x)); e.set("y", str(y))
    for k, val in v.items(): P(e)[k].set("value", val)
    S.append(e)


put(dl, 936, 1800, Name="VMEAS"); put(rp, 972, 1800, G="1", T="Trel"); put(dl, 1008, 1800, Name="VMF")
# 3. form parameter + import + instance values
cat = R.find("form").find("category")
t = next(p for p in cat.iter("parameter") if p.get("name") == "Tforce")
p = copy.deepcopy(t); p.set("name", "Trel"); p.set("desc", "OV relay stage-1 measurement lag (0.001 = none)")
p.find("value").text = "0.001"; cat.append(p)
imp = next(e for e in S if e.get("defn") == "master:import")
e = copy.deepcopy(imp); e.set("id", nid()); e.set("x", "1584"); e.set("y", "1008"); P(e)["Name"].set("value", "Trel")
assert ("1584", "1008") not in occ; S.append(e)
n = 0
for d in D.values():
    sc = d.find("schematic")
    if sc is None: continue
    for c in sc:
        if (c.get("defn") or "").endswith(":RES_Plant"):
            q = ET.SubElement(c.find("paramlist"), "param"); q.set("name", "Trel"); q.set("value", "0.001"); n += 1
open(sys.argv[2], "w", encoding="utf-8").write(ET.tostring(root, encoding="unicode"))
print(f"Trel filter added; {n} instances")
