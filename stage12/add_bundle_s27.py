r"""S27 bundle: every structural change for WP8.3 / WP9.3 / WP10 in ONE build, so that all later events are
parameter edits from one settled snapshot.

 1. Tie calibration (WP8.3): both France tie pi-sections, series R/L x 83/90 (90 -> 83 ohm per circuit;
    120 deg slip at 0.866*V^2/X: 3.39 GW -> 3.68 GW, target 3.6-3.9 GW, Fig 4-91).
 2. Spanish pump shedding (WP9.3, Table 3-15 p.198/203): stage P1 49.5 Hz 2,168 MW (split over two hosts,
    bus 3 and bus 21, 1,084 MW each), stage P2 49.3 Hz 588 MW (bus 27). Each stage is a copy of LFDD row S1
    (compare -> 0.1 s ON-delay -> PI latch 0..10); each tranche a copy of the LF1 varrlc group (node labels
    only) with R = 160000/P_k ohm on, 1e8 off. Host PO reduced by P_k/3 per phase (demand unchanged at 1 pu).
 3. RES_Plant: new parameter Tforce [s] (default 1e6): Force_eff = Force + (TIME > Tforce) -> a per-plant
    forced trip time, settable from a snapshot (Case A schedule, Case B initiator).
 4. SyncUnit: new parameters Ttrip [s] (1e6) and Ptrip [pu of Sbase, negative = loss] (0): a turbine-power
    step at Ttrip added to PMT -> partial unit trips (e.g. the 1,045 MW nuclear trip) from a snapshot.

usage: python stage12/add_bundle_s27.py <in.pscx> <out.pscx>     (project must be unloaded or saved first)
"""
import copy, random, sys, xml.etree.ElementTree as ET

G = 18
src, dst = sys.argv[1], sys.argv[2]
root = ET.parse(src).getroot()
D = {d.get("name"): d for d in root.iter("Definition")}
M = D["Main"].find("schematic")
rnd = random.Random(27)
used = {e.get("id") for e in root.iter() if e.get("id")}


def nid():
    while True:
        i = str(rnd.randint(1_000_000_000, 2_100_000_000))
        if i not in used:
            used.add(i); return i


def P(el):
    pl = el.find("paramlist")
    return {q.get("name"): q for q in pl.findall("param")} if pl is not None else {}


def gx(el): return int(el.get("x")) // G


def gy(el): return int(el.get("y")) // G


def shifted(el, dx, dy, ren=None, vals=None):
    e = copy.deepcopy(el); e.set("id", nid())
    e.set("x", str(int(e.get("x")) + dx * G)); e.set("y", str(int(e.get("y")) + dy * G))
    pp = P(e)
    for k, q in pp.items():
        if ren and q.get("value") in ren and k in ("Name", "R", "I", "C", "L"):
            q.set("value", ren[q.get("value")])
    for k, v in (vals or {}).items():
        pp[k].set("value", str(v))
    return e


def region(S, x0, x1, y0, y1):
    return [e for e in S if e.get("x") is not None and x0 <= gx(e) <= x1 and y0 <= gy(e) <= y1]


log = []
# ---- 1. tie calibration
for tid in ("1600000039", "1600000099"):
    el = next(e for e in M if e.get("id") == tid); pp = P(el)
    for k in ("Rp1", "Lp1", "XLp1", "RPUP1", "XLPUP1", "Rz1", "Lz1", "XLz1", "RPUZ1", "XLPUZ1"):
        if k in pp:
            v = float(pp[k].get("value").split("[")[0]); pp[k].set("value", repr(v * 83.0 / 90.0))
    log.append(f"tie {tid}: Lp1 -> {pp['Lp1'].get('value')}")

# ---- 2. pump shedding stages + tranches
row = region(M, 24, 44, 368, 368)                     # LFDD stage S1 (labels, compare, wire, delay, PI, pgb)
assert len(row) >= 6, len(row)
grp = [e for e in M if e.get("id") in ("1849000725", "1420392976", "662111287", "1040424859", "1361598401")]
assert len(grp) == 5
chain = region(M, 46, 63, 396, 398)                   # LF1 R-law chain (const, labels, gain, sum, I pgb)
assert len(chain) >= 10, len(chain)
STAGES = [("SP1", 0.5, 432), ("SP2", 0.7, 436)]       # 50 - 49.5, 50 - 49.3
for nm, xth, y in STAGES:
    for e in row:
        vals = {"X": xth} if e.get("defn") == "master:compare" else None
        M.append(shifted(e, 0, y - 368, {"S1": nm}, vals))
loads = {e.get("id"): e for e in M if e.get("defn") == "master:fixed_load"}
TR = [("a", "SP1", "744210529", 1084.0, 0, 444), ("b", "SP1", "775660433", 1084.0, 25, 444),
      ("c", "SP2", "768585174", 588.0, 0, 452)]
for tag, sig, host, pmw, dx, y in TR:
    k = "PU" + tag
    ren = {"LF1": "L" + k, "GND1": "G" + k, "RON1": "RO" + k, "S1": sig, "SGA1": "SG" + k,
           "LFR1": "LR" + k, "ILF1": "I" + k}
    for e in grp:
        M.append(shifted(e, dx, y - 372, ren))
    ron = 160000.0 / pmw
    for e in chain:
        vals = None
        if e.get("defn") == "master:const": vals = {"Value": f"{ron:.4f}"}
        if e.get("defn") == "master:gain": vals = {"G": f"{1e8 - ron:.4f}"}
        M.append(shifted(e, dx, y + 24 - 396, ren, vals))
    L = loads[host]; lab = next(e for e in M if e.get("id") == "1420392976")
    hl = copy.deepcopy(lab); hl.set("id", nid()); hl.set("x", L.get("x")); hl.set("y", str(int(L.get("y")) - G))
    P(hl)["Name"].set("value", "L" + k); M.append(hl)
    po = P(L)["PO"]; old = float(po.get("value")); po.set("value", f"{old - pmw / 3.0:.4f}")
    log.append(f"pump tranche {k}: host {host} PO {old:.4f} -> {old - pmw/3:.4f}, R_on {ron:.3f}, signal {sig}")


# ---- helpers for definition edits
def add_param(defn, after, name, desc, unit, default):
    form = defn.find("form"); cat = form.find("category")
    tmpl = next(p for p in cat.iter("parameter") if p.get("name") == after)
    p = copy.deepcopy(tmpl); p.set("name", name); p.set("desc", desc); p.set("unit", unit)
    p.find("value").text = str(default); cat.append(p)


def add_import(defn, name, x, y):
    """every form parameter needs a master:import of the same Name on the definition canvas"""
    S = defn.find("schematic")
    t = next(e for e in S if e.get("defn") == "master:import")
    e = copy.deepcopy(t); e.set("id", nid()); e.set("x", str(x * G)); e.set("y", str(y * G))
    P(e)["Name"].set("value", name); S.append(e)


def add_inst_param(dname, name, value):
    n = 0
    for d in D.values():
        S = d.find("schematic")
        if S is None: continue
        for e in S:
            if e.get("defn") == dname:
                pl = e.find("paramlist"); q = ET.SubElement(pl, "param"); q.set("name", name); q.set("value", str(value)); n += 1
    return n


tmpl = {}
for k in ("master:time-sig", "master:compare", "master:gain", "master:sumjct", "master:datalabel"):
    tmpl[k] = next(e for d in D.values() if d.find("schematic") is not None for e in d.find("schematic") if e.get("defn") == k)


def place(S, kind, x, y, **vals):
    e = copy.deepcopy(tmpl["master:" + kind]); e.set("id", nid()); e.set("x", str(x * G)); e.set("y", str(y * G)); e.set("orient", "0")
    pp = P(e)
    for k, v in vals.items(): pp[k].set("value", str(v))
    S.append(e); return e


# ---- 3. RES_Plant forced trip time
R = D["RES_Plant"]; RS = R.find("schematic")
fl = next(e for e in RS if e.get("id") == "1350000908"); assert P(fl)["Name"].get("value") == "Force"
P(fl)["Name"].set("value", "FORCE2")
Y = 352
place(RS, "time-sig", 10, Y); place(RS, "compare", 14, Y, X="Tforce", OL=0, OH=1)
place(RS, "sumjct", 18, Y, A=0, B=0, C=0, D=1, E=0, F=1, G=0); place(RS, "datalabel", 18, Y + 2, Name="Force")
place(RS, "datalabel", 20, Y, Name="FORCE2")
add_param(R, "Tt3", "Tforce", "Forced trip time (1e6 = never)", "s", "1e6")
add_import(R, "Tforce", 8, 358)
log.append(f"RES_Plant Tforce added to {add_inst_param('ib6:RES_Plant', 'Tforce', '1e6')} instances")

# ---- 4. SyncUnit partial trip
Sd = D["SyncUnit"]; SS = Sd.find("schematic")
place(SS, "time-sig", 15, 94); place(SS, "compare", 19, 94, X="Ttrip", OL=0, OH=1)
place(SS, "gain", 23, 94, G="Ptrip"); place(SS, "datalabel", 25, 94, Name="PTRP")
place(SS, "datalabel", 30, 84, Name="PTRP")
sm = next(e for e in SS if e.get("id") == "1455352607"); P(sm)["B"].set("value", "1")
add_param(Sd, "Pmec", "Ttrip", "Partial trip time (1e6 = never)", "s", "1e6")
add_param(Sd, "Pmec", "Ptrip", "Turbine power step at Ttrip, pu of Sbase (negative = loss)", "pu", "0.0")
add_import(Sd, "Ttrip", 40, 100); add_import(Sd, "Ptrip", 40, 104)
log.append(f"SyncUnit Ttrip/Ptrip added to {add_inst_param('ib6:SyncUnit', 'Ttrip', '1e6')} instances")
add_inst_param("ib6:SyncUnit", "Ptrip", "0.0")

open(dst, "w", encoding="utf-8").write(ET.tostring(root, encoding="unicode"))
print("\n".join(log)); print("written", dst)
