r"""Build the v2 Iberian equivalent in PSCAD from the accepted pandapower state (RUNLOG S30).

usage: python iberia_eq\pscad\build_v2.py --probe          place one of each module type, print ports/params, stop
       python iberia_eq\pscad\build_v2.py [--build]       generate C:\PSCAD_work\v2\v2.pscx (+ build, print node count)

Source of every number: iberia_eq\cal_s29\base_vk3_net.p (DUMP_NET of the accepted state, S29 sec 10), the v2 design
(V2_BUS_UNIT_LIST.md) and the S30 decisions:
  - all units directly on their 400 kV bus (no step-up), AVR load compensation XCc = +vk (3 % Spain, 5 % Portugal),
    outer Q loop Kdrp 4 / Kiq 0.005 on generators; embedded machines hold Q (Kdrp 0);
  - Morocco keeps its 15 % transformer (Morocco-Iberia mode);
  - pumps: PumpUnit per stage behind breaker3 (M1 Duero, M2 Ebro, M3..M7 Portugal Table 3-15);
  - RES: 21 RES_Plant (report plants + zone aggregates + ARA); zones without a plant net their RES into the load;
  - loads / shunts / HVDC as varrlc to ground (constant impedance in the skeleton; controls come in the full build);
  - France: source3 at the FR hub, Z 20 ohm / 85 deg [inf, to calibrate for the 4,609 MW AC peak].
Everything is connected with node labels placed on the ports (no wires), skill P2/P4.
"""
import argparse, math, os, shutil, subprocess, sys, time
import xml.etree.ElementTree as ET
import numpy as np, pandapower as pp

HERE = os.path.dirname(os.path.abspath(__file__)); IEQ = os.path.dirname(HERE)
ap = argparse.ArgumentParser(); ap.add_argument("--probe", action="store_true"); ap.add_argument("--nobuild", action="store_true")
ap.add_argument("--work", default=r"C:\PSCAD_work\v2sld")
ap.add_argument("--replay", action="store_true")     # add the V2_EVENT_SPEC replay elements (S30 sec 16)
ap.add_argument("--t0", type=float, default=30.0)    # model time of 12:32:00 (short tests: 6)
ap.add_argument("--tw", type=float, default=5.0)     # time compression of report 0..76 s (S30 sec 21); 1 = real time
ap.add_argument("--fr-dang", type=float, default=0.0)   # France source angle shift [deg] (S30 sec 22: -3.1 -> ~+390 MW export)
ap.add_argument("--pv-mw", type=float, default=4447.0)  # rooftop PV < 1 MW production ([FR] 4.3.3.2.1)
ap.add_argument("--pv-ftrip", type=float, default=0.15) # fraction of it that trips at full band [inf, calibrated]
ap.add_argument("--pv-dv0", type=float, default=3.0)    # trip band start above the load-flow bus voltage [kV] [inf]
ap.add_argument("--pv-dv1", type=float, default=15.0)   # trip band end [kV] [inf]
ap.add_argument("--api", action="store_true")         # place through the PSCAD automation API (old path, ~8 min); default: offline XML (S30 sec 23)
ap.add_argument("--no-series", action="store_true")   # TIMING TEST ONLY (S30 sec 23): replay without the France breaker/meter and the Morocco breaker
ap.add_argument("--no-frchain", action="store_true")  # TIMING TEST ONLY: without the France breaker + multimeter
ap.add_argument("--no-brkma", action="store_true")    # TIMING TEST ONLY: without the Morocco breaker
ap.add_argument("--ftest")     # TEST ONLY "t1:t2:df": frequency offset ramp 0 -> df Hz (t1..t2) added to every UF stage input (S30 sec 23)
ap.add_argument("--vtest")     # TEST ONLY "t1:t2:dv": voltage offset ramp 0 -> dv pu added to every rooftop-PV voltage input
a = ap.parse_args()
REPLAY = a.replay
WORK = a.work; os.makedirs(WORK, exist_ok=True); PSCX = os.path.join(WORK, "v2.pscx")
log = open(os.path.join(WORK, "build_v2.log"), "w")
def L(*x): print(*x, flush=True); print(*x, file=log, flush=True)

# ---------------- project file: lt6 template (DS, empty Main, PumpUnit) + SyncUnit (patched) + RES_Plant ----------------
t = open(r"C:\PSCAD_work\lt6\lt6_template.pscx", encoding="utf-8").read().replace("lt6:", "v2:").replace('name="lt6"', 'name="v2"')
open(PSCX, "w", encoding="utf-8").write(t)
root = ET.parse(PSCX).getroot(); defs = root.find("definitions")
src = ET.parse(r"C:\PSCAD_work\s29\ib6.pscx").getroot()
for nm in ("SyncUnit", "RES_Plant"):
    defs.append([d for d in src.find("definitions") if d.get("name") == nm][0])
open(PSCX, "w", encoding="utf-8").write(ET.tostring(root, encoding="unicode"))
r = subprocess.run([sys.executable, os.path.join(HERE, "add_qloop.py"), "--pscx", PSCX], capture_output=True, text=True); L(r.stdout.strip(), r.stderr.strip())
r = subprocess.run([sys.executable, os.path.join(HERE, "add_xt.py"), "--pscx", PSCX], capture_output=True, text=True); L(r.stdout.strip(), r.stderr.strip())
r = subprocess.run([sys.executable, os.path.join(HERE, "add_varrlc0.py"), "--pscx", PSCX], capture_output=True, text=True); L(r.stdout.strip(), r.stderr.strip())   # S30 sec 9
r = subprocess.run([sys.executable, os.path.join(HERE, "add_pumpheld.py"), "--pscx", PSCX], capture_output=True, text=True); L(r.stdout.strip(), r.stderr.strip())   # S30 sec 10
# S30 sec 13: machines take over (S2M) only after the RES plants are at full current, exciter references after that
r = subprocess.run([sys.executable, os.path.join(HERE, "add_switchtimes.py"), "--pscx", PSCX, "--s2m", "2.0", "--l2n", "5.0"], capture_output=True, text=True); L(r.stdout.strip(), r.stderr.strip())
r = subprocess.run([sys.executable, os.path.join(HERE, "add_exinit.py"), "--pscx", PSCX, "--t", "2.1"], capture_output=True, text=True); L(r.stdout.strip(), r.stderr.strip())
r = subprocess.run([sys.executable, os.path.join(HERE, "trim_channels.py"), "--pscx", PSCX], capture_output=True, text=True); L(r.stdout.strip(), r.stderr.strip())   # S30 sec 23
v1res = {p.get("name"): p.get("value") for e in [x for x in src.find("definitions") if x.get("name") == "Main"][0].iter("User")
         if e.get("defn") == "ib6:RES_Plant" for p in e.findall("./paramlist/param")}

# ---------------- data from the accepted pandapower state ----------------
net = pp.from_pickle(os.path.join(IEQ, "cal_s29", "base_vk3_net.p"))
BN = dict(zip(net.bus.index, net.bus.name)); V = dict(zip(net.bus.name, net.res_bus.vm_pu)); A = dict(zip(net.bus.name, net.res_bus.va_degree))
lab = lambda b: "B_" + b.replace("-", "_").replace(" ", "_")
W50 = 2 * math.pi * 50

import mhi.pscad
os.environ["PATH"] = os.path.join(WORK, "v2.gf81_x86") + os.pathsep + os.environ.get("PATH", "")   # S30 run-env fix
def _launch():
    p_ = mhi.pscad.launch(minimize=False, splash=False, timeout=60)
    if not p_.licensed():
        c = p_.get_available_certificates(); c = next(iter(c.values())) if isinstance(c, dict) else c[0]; p_.get_certificate(c)
    return p_
pscad = None
try:
    if a.api or a.probe:
        pscad = _launch(); pscad.load(PSCX); prj = pscad.project("v2"); cv = prj.canvas("Main")
    else:                                                             # S30 sec 23: write the schematic XML directly (seconds)
        sys.path.insert(0, HERE); from pscx_canvas import OfflineCanvas
        cv = OfflineCanvas(PSCX); T_GEN = time.time()
    L("Main canvas parameters:", cv.parameters() if hasattr(cv, "parameters") else "?")
    if a.probe:
        for k, (lib, nm) in enumerate((("v2", "SyncUnit"), ("v2", "RES_Plant"), ("v2", "PumpUnit"), ("master", "breaker3"),
                                       ("master", "xfmr-3p2w"), ("master", "ground"))):
            cmp_ = cv.add_component(lib, nm, 20, 20 + 15 * k, 0)
            L(f"{lib}:{nm} at (20,{20 + 15 * k}) ports", {p: (v.x, v.y) for p, v in cmp_.ports().items()})
            L("   params", list(cmp_.parameters().keys()) if nm in ("SyncUnit", "RES_Plant", "PumpUnit") else "")
        raise SystemExit(0)

    # ---------------- single-line-diagram layout (owner request S30 sec 8) ----------------
    # Zone blocks at geographic positions (rows north -> south). Each bus gets a visible busbar; every electrical element of
    # that bus hangs below it on a vertical wire. Sub-buses (pump stations, TS buses, Morocco cable end/terminal) have their
    # own busbar lower in the same block. Lines hang under their sending bus; their far end is a node label with the
    # receiving bus name, connected to that busbar through its named stub (wiring a 33-line mesh across the diagram would
    # cross busbars, and in PSCAD a wire crossing a bus connects to it). Control blocks sit in a strip below the elements.
    TERM0 = {BN[tr.lv_bus]: BN[tr.hv_bus] for _, tr in net.trafo.iterrows() if tr["name"].startswith("T G")}
    ROWS = [("NORTH / NORTH-WEST AREA  +  FRANCE", ["NW", "N", "FR"]),
            ("PORTUGAL NORTH  /  NORTH AREA  /  EAST AREA", ["PT-N", "CYL", "ARA", "CAT"]),
            ("CENTRE  (SOUTH-WEST AREA)  /  EAST AREA", ["CAC", "MAD", "VAL"]),
            ("PORTUGAL SOUTH  /  SOUTH-WEST AREA  /  EAST AREA", ["PT-S", "BAD", "SCE", "SE"]),
            ("SOUTH-WEST AREA  (ANDALUSIA)", ["WAN", "GRA"]),
            ("MOROCCO", ["MA"])]
    SUBS = {"PT-N": ["PS-PT"], "CYL": ["PS-CYL"], "ARA": ["PS-ARA"], "BAD": ["BAD-TS"], "WAN": ["WAN-TS", "MA-B"], "MA": ["Morocco term"]}
    ZNAME = {"NW": "NW  Galicia / Asturias / Leon", "N": "N  Basque C. / Navarra / Cantabria", "FR": "FR  France (source behind 20 ohm)",
             "PT-N": "PT-N  Portugal north", "CYL": "CYL  Castilla y Leon", "ARA": "ARA  Aragon", "CAT": "CAT  Catalonia",
             "CAC": "CAC  Caceres (Almaraz)", "MAD": "MAD  Madrid", "VAL": "VAL  Valencia / Cuenca", "PT-S": "PT-S  Portugal south",
             "BAD": "BAD  Badajoz", "SCE": "SCE  Cordoba / Ciudad Real", "SE": "SE  Murcia / Almeria", "WAN": "WAN  Sevilla / Huelva / Cadiz",
             "GRA": "GRA  Granada / Malaga / Jaen", "MA": "MA  Morocco"}
    ZOF = {b: z for z, ss in SUBS.items() for b in ss}; ZOF.update({z: z for _, zs in ROWS for z in zs})
    # pre-count hanging electrical items per zone to size the blocks
    NIT = {}
    def nit(z, k=1): NIT[z] = NIT.get(z, 0) + k
    for _, ln in net.line.iterrows(): nit(ZOF[BN[ln.from_bus]])
    for _, g in net.gen.iterrows(): nit(ZOF.get(TERM0.get(BN[g.bus], BN[g.bus]), "MA"))
    for _, s_ in net.sgen.iterrows(): nit(ZOF[BN[s_.bus]], 1 if s_["name"].startswith(("E", "RES")) else 0)
    for _, l_ in net.load.iterrows(): nit(ZOF[BN[l_.bus]], 2)
    for b in set(BN.values()):
        if " term" not in b or "Morocco" in b: nit(ZOF[b], 2)
    nit("PT-N", 6); nit("BAD", 3); nit("WAN", 1); nit("GRA", 2)
    if REPLAY: nit("FR", 3); nit("WAN", 1)
    SLOT = 9
    ZX, ZY = {}, {}
    y = 12
    for title, zs in ROWS:
        x = 10
        for z in zs:
            ZX[z], ZY[z] = x, y; x += max(56, 12 * NIT.get(z, 3) + 20)
        y += 66
    CUR = {}                                   # bus -> next x for hanging items
    CTL = {}                                   # zone -> next x in the control strip
    PORTS = {}                                 # bus -> [(x, y)] electrical ports to wire to its busbar
    def busy(b): return ZY[ZOF[b]] + (0 if ZOF[b] == b else 34)
    def nlab(x, y, n, meas=False):
        c_ = cv.add_component("master", "nodelabel", x, y, 0); c_.parameters(Name=n)
        if meas: c_.parameters(MeasV="YES", VName="V_" + n[2:], PU="NO")
    def dlab(x, y, n): c_ = cv.add_component("master", "datalabel", x, y, 0); c_.parameters(Name=n)
    def gnd(x, y): cv.add_component("master", "ground", x, y, 0)
    def hang(bus, lib, nm, params, eport, node=None, data=None, ground=(), w=SLOT, dy=7):
        """Place an electrical element under bus `bus`; its port `eport` is wired up to the busbar later."""
        z = ZOF[bus]; lane = SUBS.get(z, []).index(bus) * 60 if bus in SUBS.get(z, []) else 0   # own x lane per sub-bus (S30 sec 8 fix)
        x = CUR.get(bus, ZX[z] + 6 + lane); CUR[bus] = x + w
        c_ = cv.add_component(lib, nm, x, busy(bus) + dy, 0)
        if params: c_.parameters(**params)
        P = c_.ports()
        if eport: PORTS.setdefault(bus, []).append((P[eport].x, P[eport].y))
        for port, n in (node or {}).items(): nlab(P[port].x, P[port].y, n)
        for port, n in (data or {}).items(): dlab(P[port].x, P[port].y, n)
        for port in ground: gnd(P[port].x, P[port].y)
        return c_, P
    ZW = {z: max(56, 12 * NIT.get(z, 3) + 20) for z in ZX}
    def ctl(zone, lib, nm, params, data=None, w=8):
        """Control (data-only) block in the zone's control strip, rows of blocks below the hanging elements."""
        k = CTL.get(zone, 0); CTL[zone] = k + 1
        per = max(1, (ZW[zone] - 12) // w); x = ZX[zone] + 6 + (k % per) * w; y_ = ZY[zone] + 17 + 4 * (k // per)
        c_ = cv.add_component(lib, nm, x, y_, 0)
        if params: c_.parameters(**params)
        P = c_.ports()
        for port, n in (data or {}).items(): dlab(P[port].x, P[port].y, n)
        return c_, P
    PTB = {"PT-N", "PT-S", "PS-PT"}; MAB = {"MA", "Morocco term"}
    def CTRY(b): return "PT" if b in PTB else ("MA" if b in MAB else "ES")          # LFDD country of a bus (sec 16)
    def RESGRP(b): return "N" if b in ("CYL", "ARA") else ("S" if b in ("BAD", "BAD-TS", "WAN", "WAN-TS", "GRA", "CAC", "SCE", "SE") else "O")
    def const(v, n, zone="CAT"):
        c_, P = ctl(zone, "master", "const", dict(Value=str(v))); dlab(list(P.values())[0].x, list(P.values())[0].y, n)
    CNT = {}
    def count(k):
        CNT[k] = CNT.get(k, 0) + 1
        if sum(CNT.values()) % 10 == 0: L(f"placing: {sum(CNT.values())} groups so far ({k})")   # S30 sec 23: progress for the dashboard
    # titles
    for title, zs in ROWS:
        a_ = cv.add_component("master", "annotation", ZX[zs[0]], ZY[zs[0]] - 9, 0); a_.parameters(AL1=title, AL2="")
    for z in ZX:
        a_ = cv.add_component("master", "annotation", ZX[z] + 2, ZY[z] - 4, 0); a_.parameters(AL1=ZNAME.get(z, z), AL2="")
    # ---------------- lines (pi sections, SI values): hang under the sending bus, far end labelled ----------------
    for i_, ln in net.line.iterrows():
        fa, fb = BN[ln.from_bus], BN[ln.to_bus]; nc = ln.parallel; Lkm = ln.length_km
        R = ln.r_ohm_per_km * Lkm / nc; X = ln.x_ohm_per_km * Lkm / nc; C = ln.c_nf_per_km * Lkm * nc * 1e-3   # ohm, ohm, uF
        tie_ma = REPLAY and not (a.no_series or a.no_brkma) and ln["name"] == "MA-B-MA"           # V2_EVENT_SPEC F5: Morocco tie breaker at the Spanish cable end
        if tie_ma:
            hang(fa, "master", "breaker3", dict(NAME="BRKMA", BP="PBMA", OPCUR="1"), "N1", node={"N2": "MA_TIE"}, w=6); count("breaker_ma")
        hang(fa, "master", "pi_section", dict(Name=f"L{i_}", PU="4", F="50.0", len="1.0", Rp1=f"{R:.6g}", Lp1=f"{X / W50:.6g}", Cp1=f"{max(C, 1e-6):.6g}",
                                               Rz1=f"{3 * R:.6g}", Lz1=f"{3 * X / W50:.6g}", Cz1=f"{max(0.6 * C, 1e-6):.6g}"),
             None if tie_ma else "N1", node={"N2": lab(fb), **({"N1": "MA_TIE"} if tie_ma else {})}); count("line")
    # ---------------- transformers kept: pump stations, Morocco ----------------
    for i_, tr in net.trafo.iterrows():
        if not (tr["name"].startswith("T PS") or tr["name"] == "T Morocco"): continue
        hang(BN[tr.hv_bus], "master", "xfmr-3p2w", dict(Tmva=f"{tr.sn_mva:.1f}", Xl=f"{tr.vk_percent / 100:.4f} [pu]", V1="400", V2="400", NLL="0.0016 [pu]",
                                                         Im1="2.0 [%]", Sat="0", YD1="0", YD2="0", f="50"),
             "N1", node={"N2": lab(BN[tr.lv_bus])}, ground=("G1",)); count("xfmr")
    # ---------------- synchronous units ----------------
    H_ES, H_PT = 5.25, 5.3          # [inf] uniform H so that sum H*S meets Table 2-4 (Spain 97,590, Portugal 21,884 MW s)
    TERM = TERM0
    QHV = {tr["name"][2:]: -net.res_trafo.at[i_, "q_hv_mvar"] for i_, tr in net.trafo.iterrows() if tr["name"].startswith("T G")}
    XT_UNIT = 0.15                  # step-up reactance lumped into the machine (S30 sec 5: bench xreal vs xlump, swing 1.695 Hz both)
    def unit(name, bus, Pmw, Qmvar, S, H, XCc, Kdrp, Kiq, Kgov, gov=True, xt=XT_UNIT):
        prm = dict(Sbase=f"{S:.1f}", Vbase="400", VbaseLN="230.9401", Ibase=f"{S / (3 ** 0.5 * 400):.4f}", H=f"{H}", P0=f"{Pmw:.1f}",
                   Q0=f"{Qmvar:.1f}", V0=f"{V[bus]:.5f}", Ph0=f"{math.radians(A[bus]):.6f}", Vctl="0", Tstart="0.5", Pmec="0.0",
                   Kgov=f"{Kgov}", Tgov="2.0", GovLim="0.054" if gov else "0.0", KA="80", KF="0.03", TF="1.0", Ttrip="1e6", Ptrip="0.0",
                   XCc=f"{XCc}", Kdrp=f"{Kdrp}", Kiq=f"{Kiq}",
                   XmD=f"{1.79 + xt}", XmD1=f"{0.169 + xt}", XmD2=f"{0.135 + xt}", XmQ=f"{1.71 + xt}", XmQ1=f"{0.228 + xt}", XmQ2=f"{0.2 + xt}", XmP=f"{0.130 + xt}")
        hang(bus, "v2", "SyncUnit", prm, "T", w=SLOT + 1); count("syncunit")
        L(f"unit {name:22s} at {bus:12s} P {Pmw:7.1f} Q {Qmvar:+7.1f} S {S:6.0f} V {V[bus]:.4f} ang {A[bus]:+7.2f}")
    for i_, g in net.gen.iterrows():
        nm = g["name"]; gb = BN[g.bus]
        if nm.startswith("G"):
            zone = TERM[gb]; S = [tr.sn_mva for _, tr in net.trafo.iterrows() if tr["name"] == "T " + nm][0]
            unit(nm, zone, g.p_mw, QHV[nm], S, H_PT if "PT" in nm else H_ES, 0.05 if "PT" in nm else 0.03, 4.0, 0.005, 5.726)
        elif nm == "Morocco":
            unit(nm, gb, g.p_mw, net.res_gen.at[i_, "q_mvar"], 5556.0, 4.0, 0.0, 0.0, 0.0, 5.726, xt=0.0)   # real 15 % transformer kept
    for i_, s_ in net.sgen.iterrows():                      # embedded synchronous generation: constant Q (outer loop, no droop)
        if s_["name"].startswith("E"):
            bus = BN[s_.bus]; unit(s_["name"], bus, s_.p_mw, s_.q_mvar, s_.p_mw / 0.9, H_ES, 0.0, 0.0, 0.05, 0.0, gov=False)
    # ---------------- pumps: one PumpUnit per stage behind breaker3 ----------------
    PUMPS = [("M1", "PS-CYL", 1049.0), ("M2", "PS-ARA", 1017.0), ("M3", "PS-PT", 381.0), ("M4", "PS-PT", 450.0), ("M5", "PS-PT", 438.0),
             ("M6", "PS-PT", 470.0), ("M7", "PS-PT", 359.0)]
    QP = {BN[g.bus]: (net.res_gen.at[i_, "q_mvar"], -g.p_mw) for i_, g in net.gen.iterrows() if g["name"].startswith("M")}
    const(0.0, "PLD0", "PT-N")
    for k, (m_, bus, mw) in enumerate(PUMPS):
        S = mw / 0.863; q = QP[bus][0] * mw / QP[bus][1]
        hang(bus, "master", "breaker3", dict(NAME=f"BRK{m_}", BP=f"PB{m_}", OPCUR="1"), "N1", node={"N2": f"P_{m_}"}, w=6)
        hang(bus, "v2", "PumpUnit", dict(Sbase=f"{S:.1f}", Vbase="400", VbaseLN="230.9401", Ibase=f"{S / (3 ** 0.5 * 400):.4f}", H=f"{H_PT if 'PT' in bus else H_ES}",
                                          P0=f"{-mw:.1f}", Q0=f"{q:.1f}", V0=f"{V[bus]:.5f}", Ph0=f"{math.radians(A[bus]):.6f}", Vctl="0", Tstart="0.5",
                                          Pmec="0.0", Kgov="0.0", Tgov="5.0", GovLim="0.0", KA="80", KF="0.03", TF="1.0", Ttrip="1e6", Ptrip="0.0"),
             None, node={"T": f"P_{m_}"}, data={"PLD": "PLD0"}, w=SLOT); count("pump")
        if not REPLAY: const(0.0, f"BRK{m_}", ZOF[bus])      # replay: BRK<M> comes from the frequency stage (sec 16)
    # ---------------- RES plants (21) ----------------
    RESP = [("R1_Granada", "GRA", 355.0), ("R10_Malaga", "GRA", 154.0), ("A5_GRA", "GRA", 1706 + 82 - 509),
            ("R2_Badajoz4a", "BAD-TS", 582.0), ("R3_Badajoz4b", "BAD-TS", 145.0), ("R4_Badajoz5b1", "BAD-TS", 118.0), ("R7_BadajozTS3", "BAD-TS", 108.0),
            ("A2_BAD", "BAD", 1585 - 202), ("R6_Sevilla", "WAN-TS", 550.0), ("R9_Cadiz", "WAN-TS", 153.0), ("A1_WAN", "WAN", 1857 - 145),
            ("R8_Caceres", "CAC", 78.5), ("A3_CAC", "CAC", 1692 - 226 - 78.5), ("A4_SCE", "SCE", 3687 - 97), ("R5_Segovia", "CYL", 117.0),
            ("A6_CYL", "CYL", 1010 + 6 - 117), ("R11_Cuenca", "VAL", 530.0), ("A7_VAL", "VAL", 2449 - 105 - 530), ("A7b_SE_R12", "SE", 1524 - 176),
            ("A8_PTS", "PT-S", 2681.0), ("A9_ARA", "ARA", 1370 + 236)]
    xs, ys = ZX["MA"] + 70, ZY["MA"]                         # shared DC rail source (v1 pattern) and shared time signal, next to Morocco
    a_ = cv.add_component("master", "annotation", xs - 2, ys - 5, 0); a_.parameters(AL1="Shared DC rail of all RES plants (800 kV) and shared time signal", AL2="")
    c1 = cv.add_component("master", "source1", xs, ys, 0); c1.parameters(ACDC="1", Esd="800 [kV]", Ia="IDC"); P1 = c1.ports()
    pe = sorted(P1.values(), key=lambda v: v.x); nlab(pe[0].x, pe[0].y, "RAILP"); nlab(pe[-1].x, pe[-1].y, "RAILN")
    ts_ = cv.add_component("master", "time-sig", xs + 12, ys, 0); tq = list(ts_.ports().values())[0]; dlab(tq.x, tq.y, "TT")
    cf = cv.add_component("master", "const", xs + 20, ys, 0); cf.parameters(Value="0.0"); cq = list(cf.ports().values())[0]; dlab(cq.x, cq.y, "FRC")
    KPF = -0.135
    for k, (nm, bus, mw) in enumerate(RESP):
        S = mw / 0.9; prm = {kk: vv for kk, vv in v1res.items() if kk in ("Sbase", "Kv", "Ki", "Lf", "Cf", "Rf", "Kmod", "Kpf", "CarrPh", "Imax",
                             "RampLim", "Vt1", "Tt1", "Vt2", "Tt2", "Vt3", "Tt3", "Nsub", "Share1", "Share2", "Share3", "MeasSide", "Qmode", "Vset", "Tforce", "Trel")}
        prm.update(Sbase=f"{S:.2f}", Lf=f"{76.394 / S:.6g}", Cf=f"{0.001167 * S:.6g}", Ki=f"{489.9 / S:.6g}", Kpf=f"{KPF}",
                   Vt1="1.5", Vt2="1.5", Vt3="1.5", Nsub="1", Share1="1.0", Share2="0.0", Share3="0.0", CarrPh=f"{(k * 17.0) % 360:.1f}")
        up, upp = ctl(ZOF[bus], "master", "upramp", dict(X1="0.3", X2="1.5", Y2="0.9"))
        po = max(upp.values(), key=lambda v: v.x); pi_ = min(upp.values(), key=lambda v: v.x); dlab(pi_.x, pi_.y, "TT")
        if REPLAY:                                           # driver factor RF_<group> (F1/F2, sec 16)
            dlab(po.x, po.y, f"PR{k + 1}u"); _, mp = ctl(ZOF[bus], "master", "mult", None)
            dlab(mp["IN1"].x, mp["IN1"].y, f"PR{k + 1}u"); dlab(mp["IN2"].x, mp["IN2"].y, "RF_" + RESGRP(bus)); dlab(mp["OUT"].x, mp["OUT"].y, f"PR{k + 1}")
        else:
            dlab(po.x, po.y, f"PR{k + 1}")
        dd = {"Pref": f"PR{k + 1}", "Force": "FRC"}
        if REPLAY: dd["Trip"] = f"T_{nm}"                    # named per-plant trip channel (S30 sec 21 lesson 3)
        hang(bus, "v2", "RES_Plant", prm, "AC", node={"DCP": "RAILP", "DCN": "RAILN"}, data=dd, w=SLOT + 3); count("res")
        L(f"RES {nm:16s} at {bus:7s} {mw:7.1f} MW  S {S:7.1f}")
    # ---------------- loads, shunts, HVDC (varrlc to ground) ----------------
    PLANT_ZONES = {b for _, b, _ in RESP} | {"BAD", "WAN"}
    NET = {}
    for i_, s_ in net.sgen.iterrows():                      # RES (and dispatch shifts) of zones without a plant are netted into the load
        nm = s_["name"]
        if nm.startswith(("RES ", "DSP ")):
            z = nm.split()[-1]
            if z not in PLANT_ZONES: NET[z] = NET.get(z, (0.0, 0.0)); NET[z] = (NET[z][0] + s_.p_mw, NET[z][1] + s_.q_mvar)
    L("RES netted into loads:", {k: (round(v[0]), round(v[1])) for k, v in NET.items()})
    EXPLOAD = os.environ.get("EXPLOAD", "1") == "1"         # exponential loads driven by the bus meter (S30 sec 7)
    METB = sorted({b for b in BN.values() if " term" not in b and b not in ("FR",)})
    for bus in METB:                                        # per-bus meter: freq-meas -> F_<b> (Hz), VPU_<b> (pu of 400 kV)
        sb = lab(bus)[2:]
        hang(bus, "master", "freq-meas", dict(Ts="0.02", Vbas="400", F="50"), "N", data={"FREQ": f"F_{sb}", "Volts": f"VPU_{sb}", "PHASE": f"PH_{sb}"}, w=SLOT + 1)
        if EXPLOAD: ctl(ZOF[bus], "master", "realpole", dict(T="0.02", G="1.0", Limit="YES", Max="1.5", Min="0.5"), data={"I": f"VPU_{sb}", "O": f"VF_{sb}"})
        count("meter")
    def exp_branch(bus, kind, base, expo, tag):
        sb = lab(bus)[2:]; sig = f"{kind}{tag}"[:30]
        ctl(ZOF[bus], "master", "x_power_y", dict(y=f"{expo:.4f}"), data={"IN": f"VF_{sb}", "OUT": f"X{sig}"})
        g_, gp = ctl(ZOF[bus], "master", "gain", dict(G=f"{base:.6g}"))
        ki = [k for k in gp if k in ("I", "IN")][0]; ko = [k for k in gp if k in ("O", "OUT")][0]
        dlab(gp[ki].x, gp[ki].y, f"X{sig}")
        if REPLAY:                                           # LFDD / HVDC factor (sec 16): R, L = base * V^k / m
            dlab(gp[ko].x, gp[ko].y, f"{sig}g"); _, dp = ctl(ZOF[bus], "master", "div", None)
            dlab(dp["IN1"].x, dp["IN1"].y, f"{sig}g"); dlab(dp["IN2"].x, dp["IN2"].y, "MHV" if "HVDC" in tag else ("MZ_" + sb if CTRY(bus) == "ES" else "M_" + CTRY(bus))); dlab(dp["OUT"].x, dp["OUT"].y, sig)
        else:
            dlab(gp[ko].x, gp[ko].y, sig)
        prm = dict(Name=f"V{tag}"[:30], RLC="0" if kind == "R" else "1", X0=f"{base:.6g}"); prm["R" if kind == "R" else "L"] = sig
        hang(bus, "v2", "varrlc0", prm, "A", ground=("B",), w=6); count("varrlc_exp")   # X0: start-up value, S30 sec 9
    ALPHA, BETA = 0.8, 4.1
    LOADBUS = {}                                             # Spanish exp-load buses -> P (rooftop PV, sec 22)
    def shunt_rl(bus, Pmw, Qmvar, tag, VLL=None):
        VLL = VLL or 400.0 * V[bus]
        if Pmw > 1.0: hang(bus, "master", "varrlc", dict(Name=f"R{tag}", RLC="0", R=f"{VLL ** 2 / Pmw:.6g}"), "A", ground=("B",), w=6); count("varrlc")
        if Qmvar > 1.0: hang(bus, "master", "varrlc", dict(Name=f"L{tag}", RLC="1", L=f"{VLL ** 2 / (W50 * Qmvar):.6g}"), "A", ground=("B",), w=6); count("varrlc")
        if Qmvar < -1.0: hang(bus, "master", "varrlc", dict(Name=f"C{tag}", RLC="2", C=f"{-Qmvar / (W50 * VLL ** 2) * 1e6:.6g}"), "A", ground=("B",), w=6); count("varrlc")
    for i_, ld in net.load.iterrows():
        bus = BN[ld.bus]; z = ld["name"].split()[-1]
        P_, Q_ = net.res_load.at[i_, "p_mw"], net.res_load.at[i_, "q_mvar"]
        if ld["name"].startswith("Load ") and z in NET: P_ -= NET[z][0]; Q_ -= NET[z][1]
        tg = ld["name"].replace(" ", "_").replace("-", "_")
        if EXPLOAD and bus in METB and (ld["name"].startswith("Load ") or ld["name"].startswith("HVDC")):
            al, be = (0.0, 0.0) if ld["name"].startswith("HVDC") else (ALPHA, BETA)
            vlf = V[bus]
            if P_ > 1.0: exp_branch(bus, "R", 400.0 ** 2 / (P_ / vlf ** al), 2 - al, tg)
            if P_ > 1.0 and al > 0 and CTRY(bus) == "ES": LOADBUS[bus] = LOADBUS.get(bus, 0.0) + P_
            if Q_ > 1.0: exp_branch(bus, "L", 400.0 ** 2 / (W50 * Q_ / vlf ** be), 2 - be, tg)
            if Q_ < -1.0: shunt_rl(bus, 0.0, Q_, tg + "c")      # net capacitive remainder (netted RES) stays constant Z
        else:
            shunt_rl(bus, P_, Q_, tg)
    SH = {}
    for i_, sh in net.shunt.iterrows(): SH[BN[sh.bus]] = SH.get(BN[sh.bus], 0.0) + sh.q_mvar * sh.step   # Mvar at 1 pu
    for bus, q in SH.items():
        if abs(q) > 1.0: shunt_rl(bus, 0.0, q, f"SH_{lab(bus)[2:]}", VLL=400.0)
    # ---------------- France source at the FR hub ----------------
    # source3 voltage is Es (internal, LL rms kV, behind Z) -- Vm is ignored (S30 sec 6). Es/Ph from the load flow: the source
    # supplies the ext_grid P,Q plus the 1,000 MW the HVDC delivered to France in pandapower (in PSCAD the HVDC is a load at CAT).
    ZF = 20.0 * np.exp(1j * np.radians(85.0))
    Sx = (net.res_ext_grid.p_mw.iloc[0] + 1000.0) + 1j * net.res_ext_grid.q_mvar.iloc[0]
    Vf = 400.0 * V["FR"] * np.exp(1j * np.radians(A["FR"])); If = np.conj(Sx / (np.sqrt(3) * Vf)); Ef = Vf + np.sqrt(3) * ZF * If
    L(f"France source: S {Sx.real:.0f} MW {Sx.imag:+.0f} Mvar, terminal {abs(Vf):.1f} kV {A['FR']:+.2f} deg -> Es {abs(Ef):.2f} kV {np.degrees(np.angle(Ef)):+.3f} deg")
    if REPLAY and not (a.no_series or a.no_frchain):   # V2_EVENT_SPEC P8/P9: bus FR -- breaker3 BRKFR -- FR_B -- multimeter (A side = Iberia) -- FR_S -- source3
        hang("FR", "master", "breaker3", dict(NAME="BRKFR", BP="PBFR", OPCUR="1"), "N1", node={"N2": "FR_B"}, w=6); count("breaker_fr")
        _, Pm = hang("FR", "master", "multimeter", dict(MeasPh="1", RMS="1", MeasP="1", MeasQ="1", S="1.0", BaseV="400",
                                                         P="PFR", Q="QFR", Vrms="VFR", Ph="PHFR"), None, w=6)
        ks = sorted(Pm, key=lambda k: Pm[k].x); nlab(Pm[ks[0]].x, Pm[ks[0]].y, "FR_B"); nlab(Pm[ks[-1]].x, Pm[ks[-1]].y, "FR_S"); count("meter_fr")
        for n_ in ("PFR", "QFR", "PHFR", "VFR"):             # P > 0: Iberia -> France (export)
            _, gp = ctl("FR", "master", "pgb", dict(Name=n_)); q_ = list(gp.values())[0]; dlab(q_.x, q_.y, n_)
        hang("FR", "master", "source3", dict(Type="4", Imp="IMPEDANCE", Z1="20.0 [ohm]", Phi1="85.0 [deg]", Vm=f"{abs(Ef):.3f} [kV]", Es=f"{abs(Ef):.3f} [kV]",
                                             Ph=f"{np.degrees(np.angle(Ef)) + a.fr_dang:.4f} [deg]", F="50.0 [Hz]", F0="50.0 [Hz]"), None, node={"N3": "FR_S"}, ground=("N",), w=SLOT + 2)
        count("source3")
    else:
        hang("FR", "master", "source3", dict(Type="4", Imp="IMPEDANCE", Z1="20.0 [ohm]", Phi1="85.0 [deg]", Vm=f"{abs(Ef):.3f} [kV]", Es=f"{abs(Ef):.3f} [kV]",
                                             Ph=f"{np.degrees(np.angle(Ef)):.4f} [deg]", F="50.0 [Hz]", F0="50.0 [Hz]"), "N3", ground=("N",), w=SLOT + 2); count("source3")
    # ---------------- replay logic (V2_EVENT_SPEC, RUNLOG S30 sec 16): signals only, own area below the diagram ----------------
    if REPLAY:
        T0, TW, TC = a.t0, a.tw, 76.0                        # 12:32:00 at T0; report 0..TC compressed TW x, then 1:1 (sec 21)
        def MT(r): return T0 + r / TW if r < TC else T0 + TC / TW + (r - TC)
        L(f"replay time map: model = {T0} + r/{TW} for r < {TC} s, then real time; 12:33:16 -> {MT(TC):.3f} s, 12:33:24 -> {MT(84):.3f} s")
        LY0 = max(ZY.values()) + 80; LG = {"k": 0}
        a_ = cv.add_component("master", "annotation", 10, LY0 - 6, 0)
        a_.parameters(AL1=f"REPLAY LOGIC: defence plans (pumps, LFDD), Morocco relay, HVDC block, RES drivers; t0 = {T0:g} s = 12:32:00", AL2="")
        def lg(nm, params=None, data=None):
            """place a control block in the logic area (rows of 14 cells, 9 grid units wide, 6 high)."""
            k = LG["k"]; LG["k"] = k + 1; x = 10 + (k % 14) * 9; y_ = LY0 + (k // 14) * 6
            c_ = cv.add_component("master", nm, x, y_, 0)
            if params: c_.parameters(**params)
            P = c_.ports()
            ALIAS = {"I": ("I", "IN"), "O": ("O", "OUT"), "IN": ("IN", "I"), "OUT": ("OUT", "O")}   # gain uses IN/OUT, compare I/O
            for port, n in (data or {}).items():
                pk = next(k for k in ALIAS.get(port, (port,)) if k in P); dlab(P[pk].x, P[pk].y, n)
            return P
        lg("const", dict(Value="0.0"), {"OUT": "ZERO"}); lg("const", dict(Value="1.0"), {"OUT": "ONE_"})
        lg("time-sig", None, {"OUT": "TR"})
        lg("compare", dict(X="10.0", OL="0.0", OH="1.0"), {"I": "TR", "O": "UFEN"})   # under-frequency logic enabled at 10 s
        # test hooks, always built and inert (Y2 = 0) unless --ftest/--vtest; patched later with set_test.py (no rebuild)
        for opt, sig in ((a.ftest, "FTEST"), (a.vtest, "VTEST")):
            t1, t2, dd = (float(x) for x in opt.split(":")) if opt else (1000.0, 1001.0, 0.0)
            lg("upramp", dict(Name=f"{sig}_RAMP", X1=f"{t1:g}", X2=f"{t2:g}", Y2=f"{dd:g}"), {"I": "TR", "O": sig})
            P_ = lg("pgb", dict(Name=sig)); q_ = list(P_.values())[0]; dlab(q_.x, q_.y, sig)
            if opt: L(f"TEST INJECTION {sig}: 0 -> {dd:g} from {t1:g} to {t2:g} s (never in a real replay)")
        def ufstage(out, fsig, thr, delay=0.15):
            """out = 1 (latched) once fsig < thr for `delay` s: compare -> integral (0..1, T = delay) -> compare."""
            lg("sumjct", dict(D="ADD", F="ADD"), {"IND": fsig, "INF": "FTEST", "OUT": out + "f"}); fsig = out + "f"   # test hook (0 = inert)
            lg("compare", dict(X=f"{thr}", OL="1.0", OH="0.0"), {"I": fsig, "O": out + "b"})
            lg("mult", None, {"IN1": out + "b", "IN2": "UFEN", "OUT": out + "c"})   # enabled from 10 s: meters read 0 Hz at start
            lg("integral", dict(T=f"{delay}", YHi="1.0", YLo="0.0", Yo="0.0"), {"I": out + "c", "O": out + "i", "R": "ZERO"})
            lg("compare", dict(X="0.999", OL="0.0", OH="1.0"), {"I": out + "i", "O": out})
        def tstep(out, t):
            lg("compare", dict(X=f"{t:.3f}", OL="0.0", OH="1.0"), {"I": "TR", "O": out})
        def wsum(out, terms, base=None):
            """out = base + sum(w * sig): gains then a chain of 2-input junctions (D add, F add)."""
            acc = base
            for j, (w, sg) in enumerate(terms):
                lg("gain", dict(G=f"{w:.6g}"), {"I": sg, "O": f"{out}w{j}"})
                if acc is None: acc = f"{out}w{j}"; continue
                nxt = f"{out}s{j}"; lg("sumjct", dict(D="ADD", F="ADD"), {"IND": acc, "INF": f"{out}w{j}", "OUT": nxt}); acc = nxt
            lg("gain", dict(G="1.0"), {"I": acc, "O": out})
        # pumps (P3/P4): Spain M1/M2 at 49.5 Hz (Table 3-9: 2,168 MW of 3,031 at 49.5; the model's 2,066 MW of Spanish pump
        # units all trip there, the 588 MW 49.3 Hz step comes from the zone loads below); Portugal one unit per step (Table 3-11)
        for m_, fs, thr in (("M1", "F_PS_CYL", 49.5), ("M2", "F_PS_ARA", 49.5), ("M3", "F_PS_PT", 49.8), ("M4", "F_PS_PT", 49.7),
                            ("M5", "F_PS_PT", 49.6), ("M6", "F_PS_PT", 49.5), ("M7", "F_PS_PT", 49.3)):
            ufstage(f"BRK{m_}", fs, thr)
        # LFDD (P5/P6), actual shed fractions of total load (Tables 3-10, 3-13), Portuguese industry (3-12) and DSO generation
        # lost on frequency (3-4, adds load); Spanish pumping not in M1/M2: 588 MW at 49.3 Hz (Table 3-9)
        LOAD_ES, LOAD_PT = 25240.0, 5865.0                   # Spanish demand Fig 2-41; Portuguese consumption at 12:33:00 ([FR] p.201)
        ES = [(49.0, 0.040), (48.8, 0.056), (48.6, 0.053), (48.4, 0.051), (48.2, 0.044), (48.0, 0.043), (49.3, 588.0 / LOAD_ES)]
        PT = [(49.0, 315 / LOAD_PT), (48.8, 293 / LOAD_PT), (48.6, 315 / LOAD_PT), (48.4, 323 / LOAD_PT), (48.2, 282 / LOAD_PT),
              (48.0, 427 / LOAD_PT), (49.2, 218 / LOAD_PT), (49.8, -321 / LOAD_PT), (49.5, -575 / LOAD_PT)]
        for c_, lst, fs in (("ES", ES, "F_MAD"), ("PT", PT, "F_PT_N")):
            for j, (thr, fr) in enumerate(lst):
                ufstage(f"S{c_}{j}", fs, thr)
            wsum(f"M_{c_}x", [(-fr, f"S{c_}{j}") for j, (thr, fr) in enumerate(lst)], base="ONE_")
            lg("hardlimit", dict(UL="2.0", LL="0.05"), {"I": f"M_{c_}x", "O": f"M_{c_}"})
        lg("gain", dict(G="1.0"), {"I": "ONE_", "O": "M_MA"})  # Morocco loads are not shed by the Iberian plans
        # Morocco tie (F5): Moroccan under-frequency relay with transfer trip, 16a at 20.229 just after 49.5 Hz was crossed
        # at 20.180 ([CA] p.55-57) -> 49.4 Hz, 50 ms [inf]
        ufstage("BRKMA", "F_MA", 49.4, delay=0.05)
        # HVDC France (F7): Pmode 1, 1,000 MW export, blocked at event 51 (12:33:23.960)
        tstep("HVB", MT(83.960)); wsum("MHVx", [(-1.0, "HVB")], base="ONE_")
        lg("hardlimit", dict(UL="1.0", LL="0.001"), {"I": "MHVx", "O": "MHV"})
        # RES drivers (F1/F2): events 2a (north, wind/PV) and 2b (south) as MW steps (Table 3-1), plus the secondary-regulation
        # set-point ramp of 270 MW over 57 s pro-rata on all plants ([CA] p.88 minus the 208 MW of 2a/2b) [inf]
        PG = {}
        for nm_, b_, mw_ in RESP: PG[RESGRP(b_)] = PG.get(RESGRP(b_), 0.0) + mw_
        PSUM = sum(PG.values())
        lg("upramp", dict(X1=f"{MT(0):g}", X2=f"{MT(57):g}", Y2=f"{270.0 / PSUM:.6f}"), {"I": "TR", "O": "RRAMP"})
        E2 = {"N": [(5, 2.57), (9, 27.51), (25, 19.21), (29, 78.05), (45, 0.59), (49, 14.49), (53, 31.92)],
              "S": [(9, 7.65), (25, 3.43), (29, 2.26), (53, 20.78)]}
        for g_ in sorted(PG):
            terms = [(-1.0, "RRAMP")]
            for j, (ts_, mw_) in enumerate(E2.get(g_, [])):
                tstep(f"E{g_}{j}", MT(ts_)); terms.append((-mw_ / PG[g_], f"E{g_}{j}"))
            wsum(f"RF_{g_}", terms, base="ONE_")
        # France AC separation (P8, first version forced): event 31b Argia-Hernani 12:33:21.535
        tstep("BRKFR", MT(81.535))
        # rooftop PV < 1 MW (P2, sec 22): per Spanish load bus, a latched trip fraction s in [0, 1] that rises with the filtered
        # bus voltage across [V_lf + dv0, V_lf + dv1]; the zone load factor MZ = M_ES * (1 + PV_tripped / P_load)
        PVL = sum(LOADBUS.values()); lg("compare", dict(X=f"{MT(0):g}", OL="0.0", OH="1.0"), {"I": "TR", "O": "PVEN"})
        for b_, pl in sorted(LOADBUS.items()):
            sb = lab(b_)[2:]; v0 = (400 * V[b_] + a.pv_dv0) / 400; v1 = (400 * V[b_] + a.pv_dv1) / 400
            pvmw = a.pv_mw * a.pv_ftrip * pl / PVL                 # MW that trips at s = 1 [inf: rooftop PV in proportion to load]
            vin = f"VF_{sb}"
            lg("sumjct", dict(D="ADD", F="ADD"), {"IND": vin, "INF": "VTEST", "OUT": f"PVv_{sb}"}); vin = f"PVv_{sb}"   # test hook (0 = inert)
            lg("gain", dict(G=f"{1.0 / (v1 - v0):.6g}"), {"I": vin, "O": f"PVa_{sb}"})
            lg("const", dict(Value=f"{v0 / (v1 - v0):.6g}"), {"OUT": f"PVo_{sb}"})
            lg("sumjct", dict(D="ADD", F="SUBTRACT"), {"IND": f"PVa_{sb}", "INF": f"PVo_{sb}", "OUT": f"PVb_{sb}"})
            lg("hardlimit", dict(UL="1.0", LL="0.0"), {"I": f"PVb_{sb}", "O": f"PVt_{sb}"})       # target fraction
            lg("sumjct", dict(D="ADD", F="SUBTRACT"), {"IND": f"PVt_{sb}", "INF": f"PVs_{sb}", "OUT": f"PVe_{sb}"})
            lg("hardlimit", dict(UL="10.0", LL="0.0"), {"I": f"PVe_{sb}", "O": f"PVu_{sb}"})       # latch: only upwards
            lg("mult", None, {"IN1": f"PVu_{sb}", "IN2": "PVEN", "OUT": f"PVg_{sb}"})
            lg("integral", dict(T="0.05", YHi="1.0", YLo="0.0", Yo="0.0"), {"I": f"PVg_{sb}", "O": f"PVs_{sb}", "R": "ZERO"})
            lg("gain", dict(G=f"{pvmw / pl:.6g}"), {"I": f"PVs_{sb}", "O": f"PVm_{sb}"})
            lg("sumjct", dict(D="ADD", F="ADD"), {"IND": "ONE_", "INF": f"PVm_{sb}", "OUT": f"PVF_{sb}"})
            lg("mult", None, {"IN1": "M_ES", "IN2": f"PVF_{sb}", "OUT": f"MZ_{sb}"})
            L(f"  rooftop PV {b_:6s}: load {pl:7.1f} MW, trips {pvmw:6.1f} MW across {400 * v0:.1f}..{400 * v1:.1f} kV")
        L(f"rooftop PV: {a.pv_mw * a.pv_ftrip:.0f} MW can trip on {len(LOADBUS)} Spanish load buses")
        for nm_, b_, mw_ in RESP:
            P_ = lg("pgb", dict(Name=f"T_{nm_}")); q_ = list(P_.values())[0]; dlab(q_.x, q_.y, f"T_{nm_}")
        for n_ in ("BRKM1", "BRKM3", "BRKMA", "BRKFR", "M_ES", "M_PT", "MHV", "RF_N", "RF_S", "PVF_MAD", "PVF_CAT"):
            P_ = lg("pgb", dict(Name=n_)); q_ = list(P_.values())[0]; dlab(q_.x, q_.y, n_)
        L(f"replay logic: {LG['k']} blocks in the logic area (y from {LY0}); RES groups {{g: MW}} = {PG}")
    # ---------------- busbars, wires, named measuring stubs + voltage channels ----------------
    BUSN = {}
    for bus, pts in PORTS.items():
        yb = busy(bus); xs_ = [p_[0] for p_ in pts]; x0, x1 = min(xs_) - 3, max(xs_) + 3
        bb = cv.create_bus((x0, yb), (x1, yb))
        try:
            bp = bb.parameters(); key = "Name" if "Name" in bp else ("name" if "name" in bp else None)
            if key: bb.parameters(**{key: lab(bus)})
            if not BUSN: L("bus parameters:", bp)
        except Exception as ex: L("bus naming failed:", ex)
        BUSN[bus] = (x0, x1, yb)
        for (px, py) in pts:
            if py != yb: cv.create_wire((px, yb), (px, py))
        cv.create_wire((x0, yb), (x0 - 3, yb)); nlab(x0 - 3, yb, lab(bus), meas=True)      # named stub: far ends of lines etc.
        g_ = cv.add_component("master", "pgb", x0 - 3, yb - 3, 0); g_.parameters(Name="V_" + lab(bus)[2:])
        gp = list(g_.ports().values())[0]; dlab(gp.x, gp.y, "V_" + lab(bus)[2:]); count("vchan")
    bl = sorted(BUSN.items(), key=lambda kv: (kv[1][2], kv[1][0]))
    clash = [(b1, b2) for (b1, (a0, a1, y1)), (b2, (c0, c1, y2)) in zip(bl, bl[1:]) if y1 == y2 and a1 + 2 >= c0 - 5]
    if clash: L("BUSBAR CLASH (would merge nodes):", clash); raise SystemExit(3)
    missing = sorted(set(BN.values()) - set(PORTS) - {b for b in BN.values() if " term" in b and "Morocco" not in b})
    if missing: L("WARNING buses without hanging elements (no busbar):", missing)
    L("placed:", CNT)
    if pscad is None:                                                 # offline: write the file, then PSCAD only loads + builds
        cv.project_parameters(time_duration="2.0", time_step="20", sample_step="1000", PlotType="1", StartType="0"); cv.save()
        L(f"offline generation: {time.time() - T_GEN:.1f} s")
        if not a.nobuild: pscad = _launch(); pscad.load(PSCX); prj = pscad.project("v2")
    else:
        prj.parameters(time_duration="2.0", time_step="20", sample_step="1000", PlotType="1", StartType="0")
        prj.save()
    if not a.nobuild:
        prj.build()
        msgs = [(str(getattr(m, "status", "")), getattr(m, "text", m)) for m in prj.messages()]
        for st, tx in msgs:
            if st.lower() == "error" or any(k in str(tx).lower() for k in ("short circuit", "open circuit", "floating", "unresolved", "contention", "range", "live nodes", "dimension")):
                L("MSG", st, tx)
        mp = os.path.join(WORK, "v2.gf81_x86", "v2.map")
        if os.path.exists(mp): L("MAP:", [ln.strip() for ln in open(mp) if ln.strip().startswith(("NODES", "NNODES", "BRANCHES"))])
finally:
    if pscad is not None: pscad.quit()
