r"""Batch-2 bundle (S27): structural items for Batch 2/3 in ONE build, applied to the S27 bundle case.

 1. Tie 83 -> 76 ohm per circuit (Batch 1 r1: slip at -3.39 GW, target -3.6..-3.9; x 3.39/3.70).
 2. Voltage meters (master:freq-meas, 0 nodes, Vbas 400 -> pu) on every Iberian load bus and the two reactor buses,
    connected by node label only (the load's IA-port label; new `LDxx` labels where none exists). Output `VLbb`
    (bus number) with a pgb -> the C3 balance (P_load = 3*PO*V) and the tranche R_on correction become measurable.
 3. P2 (WP11): switched shunt reactors, 500 Mvar at bus 29 and 500 Mvar at bus 1 (`varrlc` L, 3-phase effective:
    L_on = 400^2/(w*500) = 1.0186 H, off 1e4 H), driven by a copy of LFDD row S1: VLbb > X (X = 99 -> disabled; set
    1.05 from a snapshot to enable) -> 0.1 s ON-delay -> PI latch -> L law. Event-only enable (S6).
 4. Dispatch: the final S27 trim (`C:\PSCAD_work\s27\trim3_spec.json`) is written into the unit Pmec values.
usage: python stage12/add_bundle_s28.py <s27 bundle case.pscx> <out.pscx>
"""
import copy, json, random, sys, xml.etree.ElementTree as ET

G = 18
root = ET.parse(sys.argv[1]).getroot()
D = {d.get("name"): d for d in root.iter("Definition")}
M = D["Main"].find("schematic")
used = {e.get("id") for e in root.iter() if e.get("id")}
rnd = random.Random(28)


def nid():
    while True:
        i = str(rnd.randint(1_000_000_000, 2_100_000_000))
        if i not in used: used.add(i); return i


def P(el):
    pl = el.find("paramlist"); return {q.get("name"): q for q in pl.findall("param")} if pl is not None else {}


gx = lambda e: int(e.get("x")) // G
gy = lambda e: int(e.get("y")) // G
byid = {e.get("id"): e for e in M if e.get("id")}


def clone(el, x=None, y=None, dx=0, dy=0, **vals):
    e = copy.deepcopy(el); e.set("id", nid())
    e.set("x", str((x * G) if x is not None else int(e.get("x")) + dx * G))
    e.set("y", str((y * G) if y is not None else int(e.get("y")) + dy * G))
    pp = P(e)
    for k, v in vals.items(): pp[k].set("value", str(v))
    M.append(e); return e


def region(x0, x1, y0, y1):
    return [e for e in list(M) if e.get("x") is not None and x0 <= gx(e) <= x1 and y0 <= gy(e) <= y1]


log = []
# 1. tie
for tid in ("1600000039", "1600000099"):
    pp = P(byid[tid])
    for k in ("Rp1", "Lp1", "XLp1", "RPUP1", "XLPUP1", "Rz1", "Lz1", "XLz1", "RPUZ1", "XLPUZ1"):
        if k in pp: pp[k].set("value", repr(float(pp[k].get("value").split("[")[0]) * 76.0 / 83.0))
log.append(f"tie Lp1 -> {P(byid['1600000039'])['Lp1'].get('value')}")

# 4. final trim
spec = json.load(open(r"C:\PSCAD_work\s27\trim3_spec.json"))
UNIT = {"30": "993049547", "31": "1404126973", "32": "489869766", "37": "650097263", "France": "1766995819"}
for b, kv in spec["units"].items():
    P(byid[UNIT[b]])["Pmec"].set("value", str(kv["Pmec"]))
log.append("Pmec <- trim3")

# 2. meters
import os
DO_METERS = os.environ.get('NOMETERS') is None
DO_P2 = os.environ.get('NOP2') is None
LOADB = {"744210529": 3, "1004648478": 7, "1522722771": 8, "1862156076": 12, "914258219": 15, "1925407754": 16,
         "1087233095": 18, "2071274910": 20, "775660433": 21, "553408281": 23, "1468690411": 24, "1275297413": 25,
         "979306711": 26, "768585174": 27, "2117866167": 28, "427020063": 29, "1446795315": 31, "2035760321": 4}
labels = [e for e in M if e.get("defn") == "master:nodelabel"]
lab_at = {(gx(e), gy(e)): P(e)["Name"].get("value") for e in labels}
tmpl_lab = next(e for e in labels if P(e)["Name"].get("value") == "LF1")
meter = next(e for e in M if e.get("defn") == "master:freq-meas")
pgb = next(e for e in M if e.get("defn") == "master:pgb" and P(e)["Name"].get("value") == "ILF1")
dlab = next(e for e in M if e.get("defn") == "master:datalabel" and P(e)["Name"].get("value") == "ILF1")
targets = []
for lid, bus in LOADB.items():
    L = byid[lid]; ia = (gx(L), gy(L) + (1 if lid in ('1862156076', '1468690411') else -1))   # these two loads are flipped (IA below; pscad_get_ports)
    name = lab_at.get(ia)
    if name is None:
        name = f"LD{bus:02d}"; clone(tmpl_lab, x=ia[0], y=ia[1], Name=name)
    targets.append((bus, name))
targets += [("R29", "SH29"), ("R01", "SH01")]
for i, (bus, node) in enumerate(targets if DO_METERS else []):
    x, y = 10 + 14 * (i % 10), 500 + 10 * (i // 10)
    clone(meter, x=x, y=y, Name=f"FM{bus}")
    clone(tmpl_lab, x=x - 4, y=y, Name=node)
    out = f"VL{bus}" if isinstance(bus, int) else f"V{bus}"
    clone(dlab, x=x + 4, y=y, Name=out); clone(pgb, x=x + 4, y=y, Name=out)
    log.append(f"meter {out} on node {node}")

# 3. P2 switched reactors
row = region(24, 44, 368, 368)                      # LFDD stage S1
grp_ids = ("1849000725", "1420392976", "662111287", "1040424859", "1361598401")
chain = region(46, 63, 396, 398)
LON = 160000.0 / (314.159265 * 500.0); LOFF = 1.0e4
for j, (vsig, node, tag) in enumerate((("VR29", "SH29", "29"), ("VR01", "SH01", "01")) if DO_P2 else ()):
    y = 540 + 12 * j
    for e in row:
        vals = {"X": 99.0} if e.get("defn") == "master:compare" else {}
        c = clone(e, dy=y - 368, **vals); pp = P(c)
        if "Name" in pp and pp["Name"].get("value") == "RPOS": pp["Name"].set("value", vsig)
        if "Name" in pp and pp["Name"].get("value") == "S1": pp["Name"].set("value", "RS" + tag)
    ren = {"LF1": node, "GND1": "GR" + tag}
    for gid in grp_ids:
        c = clone(byid[gid], dy=y + 4 - 372); pp = P(c)
        if pp.get("Name") is not None and pp["Name"].get("value") in ren: pp["Name"].set("value", ren[pp["Name"].get("value")])
        if c.get("defn") == "master:varrlc":
            pp["RLC"].set("value", "1"); pp["L"].set("value", "LL" + tag); pp["I"].set("value", "IR" + tag)
            pp["Name"].set("value", "P2R" + tag)
    ren2 = {"RON1": "LO" + tag, "S1": "RS" + tag, "SGA1": "SL" + tag, "LFR1": "LL" + tag, "ILF1": "IR" + tag}
    for e in chain:
        vals = {}
        if e.get("defn") == "master:const": vals = {"Value": f"{LOFF:.4f}"}
        if e.get("defn") == "master:gain": vals = {"G": f"{-(LOFF - LON) / 10.0:.6f}"}
        c = clone(e, dy=y + 12 - 396, **vals); pp = P(c)
        if pp.get("Name") is not None and pp["Name"].get("value") in ren2: pp["Name"].set("value", ren2[pp["Name"].get("value")])
    log.append(f"P2 reactor bus {tag}: 500 Mvar, L_on {LON:.4f} H, compare X 99 (disabled), signal {vsig}")

open(sys.argv[2], "w", encoding="utf-8").write(ET.tostring(root, encoding="unicode"))
print("\n".join(log))
