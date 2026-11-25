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
ap.add_argument("--work", default=r"C:\PSCAD_work\v2")
a = ap.parse_args()
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
v1res = {p.get("name"): p.get("value") for e in [x for x in src.find("definitions") if x.get("name") == "Main"][0].iter("User")
         if e.get("defn") == "ib6:RES_Plant" for p in e.findall("./paramlist/param")}

# ---------------- data from the accepted pandapower state ----------------
net = pp.from_pickle(os.path.join(IEQ, "cal_s29", "base_vk3_net.p"))
BN = dict(zip(net.bus.index, net.bus.name)); V = dict(zip(net.bus.name, net.res_bus.vm_pu)); A = dict(zip(net.bus.name, net.res_bus.va_degree))
lab = lambda b: "B_" + b.replace("-", "_").replace(" ", "_")
W50 = 2 * math.pi * 50

import mhi.pscad
os.environ["PATH"] = os.path.join(WORK, "v2.gf81_x86") + os.pathsep + os.environ.get("PATH", "")   # S30 run-env fix
pscad = mhi.pscad.launch(minimize=False, splash=False, timeout=60)
try:
    if not pscad.licensed():
        c = pscad.get_available_certificates(); c = next(iter(c.values())) if isinstance(c, dict) else c[0]; pscad.get_certificate(c)
    pscad.load(PSCX); prj = pscad.project("v2"); cv = prj.canvas("Main")
    L("Main canvas parameters:", cv.parameters() if hasattr(cv, "parameters") else "?")
    if a.probe:
        for k, (lib, nm) in enumerate((("v2", "SyncUnit"), ("v2", "RES_Plant"), ("v2", "PumpUnit"), ("master", "breaker3"),
                                       ("master", "xfmr-3p2w"), ("master", "ground"))):
            cmp_ = cv.add_component(lib, nm, 20, 20 + 15 * k, 0)
            L(f"{lib}:{nm} at (20,{20 + 15 * k}) ports", {p: (v.x, v.y) for p, v in cmp_.ports().items()})
            L("   params", list(cmp_.parameters().keys()) if nm in ("SyncUnit", "RES_Plant", "PumpUnit") else "")
        raise SystemExit(0)

    # ---------------- placement helpers: labels on read-back ports ----------------
    POS = {"x": 6, "y": 6}
    def cell(w=14, h=9):
        x, y = POS["x"], POS["y"]; POS["x"] += w
        if POS["x"] > 200: POS["x"] = 6; POS["y"] += h
        return x, y
    def nlab(x, y, n): c_ = cv.add_component("master", "nodelabel", x, y, 0); c_.parameters(Name=n)
    def dlab(x, y, n): c_ = cv.add_component("master", "datalabel", x, y, 0); c_.parameters(Name=n)
    def gnd(x, y): cv.add_component("master", "ground", x, y, 0)
    def put(lib, nm, params, node=None, data=None, ground=(), w=14, h=9):
        x, y = cell(w, h); c_ = cv.add_component(lib, nm, x, y, 0)
        if params: c_.parameters(**params)
        P = c_.ports()
        for port, n in (node or {}).items(): nlab(P[port].x, P[port].y, n)
        for port, n in (data or {}).items(): dlab(P[port].x, P[port].y, n)
        for port in ground: gnd(P[port].x, P[port].y)
        return c_, P
    def const(v, n):
        c_, P = put("master", "const", dict(Value=str(v)), w=8); dlab(list(P.values())[0].x, list(P.values())[0].y, n)
    CNT = {}
    def count(k): CNT[k] = CNT.get(k, 0) + 1

    # ---------------- lines (pi sections, SI values) ----------------
    for i_, ln in net.line.iterrows():
        fa, fb = BN[ln.from_bus], BN[ln.to_bus]; nc = ln.parallel; Lkm = ln.length_km
        R = ln.r_ohm_per_km * Lkm / nc; X = ln.x_ohm_per_km * Lkm / nc; C = ln.c_nf_per_km * Lkm * nc * 1e-3   # ohm, ohm, uF
        put("master", "pi_section", dict(Name=f"L{i_}", PU="4", F="50.0", len="1.0", Rp1=f"{R:.6g}", Lp1=f"{X / W50:.6g}", Cp1=f"{max(C, 1e-6):.6g}",
                                          Rz1=f"{3 * R:.6g}", Lz1=f"{3 * X / W50:.6g}", Cz1=f"{max(0.6 * C, 1e-6):.6g}"),
            node={"N1": lab(fa), "N2": lab(fb)}); count("line")
    # ---------------- transformers kept: pump stations, Morocco ----------------
    for i_, tr in net.trafo.iterrows():
        if not (tr["name"].startswith("T PS") or tr["name"] == "T Morocco"): continue
        put("master", "xfmr-3p2w", dict(Tmva=f"{tr.sn_mva:.1f}", Xl=f"{tr.vk_percent / 100:.4f} [pu]", V1="400", V2="400", NLL="0.0016 [pu]",
                                         Im1="2.0 [%]", Sat="0", YD1="0", YD2="0", f="50"),
            node={"N1": lab(BN[tr.hv_bus]), "N2": lab(BN[tr.lv_bus])}, ground=("G1",)); count("xfmr")
    # ---------------- synchronous units ----------------
    H_ES, H_PT = 5.25, 5.3          # [inf] uniform H so that sum H*S meets Table 2-4 (Spain 97,590, Portugal 21,884 MW s)
    TERM = {BN[tr.lv_bus]: BN[tr.hv_bus] for _, tr in net.trafo.iterrows() if tr["name"].startswith("T G")}   # unit term -> zone (direct)
    QHV = {tr["name"][2:]: -net.res_trafo.at[i_, "q_hv_mvar"] for i_, tr in net.trafo.iterrows() if tr["name"].startswith("T G")}
    XT_UNIT = 0.15                  # step-up reactance lumped into the machine (S30 sec 5: bench xreal vs xlump, swing 1.695 Hz both)
    def unit(name, bus, Pmw, Qmvar, S, H, XCc, Kdrp, Kiq, Kgov, gov=True, xt=XT_UNIT):
        prm = dict(Sbase=f"{S:.1f}", Vbase="400", VbaseLN="230.9401", Ibase=f"{S / (3 ** 0.5 * 400):.4f}", H=f"{H}", P0=f"{Pmw:.1f}",
                   Q0=f"{Qmvar:.1f}", V0=f"{V[bus]:.5f}", Ph0=f"{math.radians(A[bus]):.6f}", Vctl="0", Tstart="0.5", Pmec="0.0",
                   Kgov=f"{Kgov}", Tgov="2.0", GovLim="0.054" if gov else "0.0", KA="40", KF="0.03", TF="1.0", Ttrip="1e6", Ptrip="0.0",
                   XCc=f"{XCc}", Kdrp=f"{Kdrp}", Kiq=f"{Kiq}",
                   XmD=f"{1.79 + xt}", XmD1=f"{0.169 + xt}", XmD2=f"{0.135 + xt}", XmQ=f"{1.71 + xt}", XmQ1=f"{0.228 + xt}", XmQ2=f"{0.2 + xt}", XmP=f"{0.130 + xt}")
        put("v2", "SyncUnit", prm, node={"T": lab(bus)}); count("syncunit"); L(f"unit {name:22s} at {bus:12s} P {Pmw:7.1f} Q {Qmvar:+7.1f} S {S:6.0f} V {V[bus]:.4f} ang {A[bus]:+7.2f}")
    for i_, g in net.gen.iterrows():
        nm = g["name"]; gb = BN[g.bus]
        if nm.startswith("G"):
            zone = TERM[gb]; S = [tr.sn_mva for _, tr in net.trafo.iterrows() if tr["name"] == "T " + nm][0]
            unit(nm, zone, g.p_mw, QHV[nm], S, H_PT if "PT" in nm else H_ES, 0.05 if "PT" in nm else 0.03, 4.0, 0.005, 5.726)
        elif nm == "Morocco":
            unit(nm, gb, g.p_mw, net.res_gen.at[i_, "q_mvar"], 5556.0, 4.0, 0.0, 0.0, 0.0, 5.726, xt=0.0)   # real 15 % transformer kept
    for i_, s in net.sgen.iterrows():                       # embedded synchronous generation: constant Q (outer loop, no droop)
        if s["name"].startswith("E"):
            bus = BN[s.bus]; unit(s["name"], bus, s.p_mw, s.q_mvar, s.p_mw / 0.9, H_ES, 0.0, 0.0, 0.05, 0.0, gov=False)
    # ---------------- pumps: one PumpUnit per stage behind breaker3 ----------------
    PUMPS = [("M1", "PS-CYL", 1049.0), ("M2", "PS-ARA", 1017.0), ("M3", "PS-PT", 381.0), ("M4", "PS-PT", 450.0), ("M5", "PS-PT", 438.0),
             ("M6", "PS-PT", 470.0), ("M7", "PS-PT", 359.0)]
    QP = {BN[g.bus]: (net.res_gen.at[i_, "q_mvar"], -g.p_mw) for i_, g in net.gen.iterrows() if g["name"].startswith("M")}
    const(0.0, "BRKOFF"); const(0.0, "PLD0")
    for k, (m_, bus, mw) in enumerate(PUMPS):
        S = mw / 0.863; q = QP[bus][0] * mw / QP[bus][1]
        put("master", "breaker3", dict(NAME=f"BRK{m_}", BP=f"PB{m_}", OPCUR="1"), node={"N1": lab(bus), "N2": f"P_{m_}"}, w=8)
        dlab(*cell(6), f"BRK{m_}") if False else None
        put("v2", "PumpUnit", dict(Sbase=f"{S:.1f}", Vbase="400", VbaseLN="230.9401", Ibase=f"{S / (3 ** 0.5 * 400):.4f}", H=f"{H_PT if 'PT' in bus else H_ES}",
                                    P0=f"{-mw:.1f}", Q0=f"{q:.1f}", V0=f"{V[bus]:.5f}", Ph0=f"{math.radians(A[bus]):.6f}", Vctl="0", Tstart="0.5",
                                    Pmec=f"{-mw / S:.6f}", Kgov="0.0", Tgov="5.0", GovLim="0.0", KA="40", KF="0.03", TF="1.0", Ttrip="1e6", Ptrip="0.0"),
            node={"T": f"P_{m_}"}, data={"PLD": "PLD0"}); count("pump")
        const(0.0, f"BRK{m_}")
    # ---------------- RES plants (21) ----------------
    RESP = [("R1_Granada", "GRA", 355.0), ("R10_Malaga", "GRA", 154.0), ("A5_GRA", "GRA", 1706 + 82 - 509),
            ("R2_Badajoz4a", "BAD-TS", 582.0), ("R3_Badajoz4b", "BAD-TS", 145.0), ("R4_Badajoz5b1", "BAD-TS", 118.0), ("R7_BadajozTS3", "BAD-TS", 108.0),
            ("A2_BAD", "BAD", 1585 - 202), ("R6_Sevilla", "WAN-TS", 550.0), ("R9_Cadiz", "WAN-TS", 153.0), ("A1_WAN", "WAN", 1857 - 145),
            ("R8_Caceres", "CAC", 78.5), ("A3_CAC", "CAC", 1692 - 226 - 78.5), ("A4_SCE", "SCE", 3687 - 97), ("R5_Segovia", "CYL", 117.0),
            ("A6_CYL", "CYL", 1010 + 6 - 117), ("R11_Cuenca", "VAL", 530.0), ("A7_VAL", "VAL", 2449 - 105 - 530), ("A7b_SE_R12", "SE", 1524 - 176),
            ("A8_PTS", "PT-S", 2681.0), ("A9_ARA", "ARA", 1370 + 236)]
    c1, P1 = put("master", "source1", dict(ACDC="1", Esd="800 [kV]", Ia="IDC"), node=None, w=10)   # shared DC rail (v1 pattern)
    pe = sorted([v for v in P1.values() if getattr(v, "dim", 1) != 0], key=lambda v: v.x) or sorted(P1.values(), key=lambda v: v.x)
    L("source1 ports", {k: (v.x, v.y) for k, v in P1.items()})
    nlab(pe[0].x, pe[0].y, "RAILP"); nlab(pe[-1].x, pe[-1].y, "RAILN")
    const(0.0, "FRC")
    ts_, tsp = put("master", "time-sig", None, w=8); dlab(list(tsp.values())[0].x, list(tsp.values())[0].y, "TT")   # shared time for the ramps
    KPF = -0.135
    for k, (nm, bus, mw) in enumerate(RESP):
        S = mw / 0.9; prm = dict(v1res); prm = {kk: vv for kk, vv in prm.items() if kk in ("Sbase", "Kv", "Ki", "Lf", "Cf", "Rf", "Kmod", "Kpf", "CarrPh", "Imax",
                                    "RampLim", "Vt1", "Tt1", "Vt2", "Tt2", "Vt3", "Tt3", "Nsub", "Share1", "Share2", "Share3", "MeasSide", "Qmode", "Vset", "Tforce", "Trel")}
        prm.update(Sbase=f"{S:.2f}", Lf=f"{76.394 / S:.6g}", Cf=f"{0.001167 * S:.6g}", Ki=f"{489.9 / S:.6g}", Kpf=f"{KPF}",
                   Vt1="1.5", Vt2="1.5", Vt3="1.5", Nsub="1", Share1="1.0", Share2="0.0", Share3="0.0", CarrPh=f"{(k * 17.0) % 360:.1f}")
        x, y = cell(16, 9)
        up = cv.add_component("master", "upramp", x, y, 0); up.parameters(X1="0.3", X2="1.5", Y2="0.9"); upp = up.ports()
        po = max(upp.values(), key=lambda v: v.x); dlab(po.x, po.y, f"PR{k + 1}"); pi_ = min(upp.values(), key=lambda v: v.x); dlab(pi_.x, pi_.y, "TT")
        if k == 0: L("upramp ports", {kk: (v.x, v.y) for kk, v in upp.items()})
        put("v2", "RES_Plant", prm, node={"AC": lab(bus), "DCP": "RAILP", "DCN": "RAILN"}, data={"Pref": f"PR{k + 1}", "Force": "FRC"}); count("res")
        L(f"RES {nm:16s} at {bus:7s} {mw:7.1f} MW  S {S:7.1f}")
    # ---------------- loads, shunts, HVDC (varrlc to ground) ----------------
    PLANT_ZONES = {b for _, b, _ in RESP} | {"BAD", "WAN"}
    NET = {}
    for i_, s in net.sgen.iterrows():                       # RES (and dispatch shifts) of zones without a plant are netted into the load
        nm = s["name"]
        if nm.startswith(("RES ", "DSP ")):
            z = nm.split()[-1]
            if z not in PLANT_ZONES: NET[z] = NET.get(z, (0.0, 0.0)); NET[z] = (NET[z][0] + s.p_mw, NET[z][1] + s.q_mvar)
    L("RES netted into loads:", {k: (round(v[0]), round(v[1])) for k, v in NET.items()})
    def shunt_rl(bus, Pmw, Qmvar, tag):
        VLL = 400.0 * V[bus]
        if Pmw > 1.0: put("master", "varrlc", dict(Name=f"R{tag}", RLC="0", R=f"{VLL ** 2 / Pmw:.6g}"), node={"A": lab(bus)}, ground=("B",), w=8); count("varrlc")
        if Qmvar > 1.0: put("master", "varrlc", dict(Name=f"L{tag}", RLC="1", L=f"{VLL ** 2 / (W50 * Qmvar):.6g}"), node={"A": lab(bus)}, ground=("B",), w=8); count("varrlc")
        if Qmvar < -1.0: put("master", "varrlc", dict(Name=f"C{tag}", RLC="2", C=f"{-Qmvar / (W50 * VLL ** 2) * 1e6:.6g}"), node={"A": lab(bus)}, ground=("B",), w=8); count("varrlc")
    for i_, ld in net.load.iterrows():
        bus = BN[ld.bus]; z = ld["name"].split()[-1]
        P_, Q_ = net.res_load.at[i_, "p_mw"], net.res_load.at[i_, "q_mvar"]
        if ld["name"].startswith("Load ") and z in NET: P_ -= NET[z][0]; Q_ -= NET[z][1]
        shunt_rl(bus, P_, Q_, ld["name"].replace(" ", "_").replace("-", "_"))
    SH = {}
    for i_, sh in net.shunt.iterrows(): SH[BN[sh.bus]] = SH.get(BN[sh.bus], 0.0) + sh.q_mvar * sh.step * V[BN[sh.bus]] ** 0   # Mvar at 1 pu
    for bus, q in SH.items():
        if abs(q) > 1.0:
            VLL = 400.0
            if q > 0: put("master", "varrlc", dict(Name=f"SHL_{lab(bus)}", RLC="1", L=f"{VLL ** 2 / (W50 * q):.6g}"), node={"A": lab(bus)}, ground=("B",), w=8)
            else: put("master", "varrlc", dict(Name=f"SHC_{lab(bus)}", RLC="2", C=f"{-q / (W50 * VLL ** 2) * 1e6:.6g}"), node={"A": lab(bus)}, ground=("B",), w=8)
            count("varrlc")
    # ---------------- France source at the FR hub ----------------
    # source3 voltage is Es (internal, LL rms kV, behind Z) -- Vm is ignored (S30 sec 6: a default Es 230 kV collapsed the
    # first settle). Es/Ph from the load flow: the source supplies the ext_grid P,Q plus the 1,000 MW the HVDC delivered to
    # France in pandapower (in PSCAD the HVDC is a 1,000 MW load at CAT). E = V + sqrt3 Z I, I = conj(S / (sqrt3 V)).
    ZF = 20.0 * np.exp(1j * np.radians(85.0))
    Sx = (net.res_ext_grid.p_mw.iloc[0] + 1000.0) + 1j * net.res_ext_grid.q_mvar.iloc[0]
    Vf = 400.0 * V["FR"] * np.exp(1j * np.radians(A["FR"])); If = np.conj(Sx / (np.sqrt(3) * Vf)); Ef = Vf + np.sqrt(3) * ZF * If
    L(f"France source: S {Sx.real:.0f} MW {Sx.imag:+.0f} Mvar, terminal {abs(Vf):.1f} kV {A['FR']:+.2f} deg -> Es {abs(Ef):.2f} kV {np.degrees(np.angle(Ef)):+.3f} deg")
    put("master", "source3", dict(Type="4", Imp="IMPEDANCE", Z1="20.0 [ohm]", Phi1="85.0 [deg]", Vm=f"{abs(Ef):.3f} [kV]", Es=f"{abs(Ef):.3f} [kV]",
                                  Ph=f"{np.degrees(np.angle(Ef)):.4f} [deg]", F="50.0 [Hz]", F0="50.0 [Hz]"), node={"N3": lab("FR")}, ground=("N",)); count("source3")
    # ---------------- bus voltage channels: measuring node label (0 nodes) -> pgb ----------------
    for bus in sorted(set(BN.values())):
        if " term" in bus and "Morocco" not in bus: continue
        vn = "V_" + lab(bus)[2:]
        x, y = cell(10, 9); c_ = cv.add_component("master", "nodelabel", x, y, 0); c_.parameters(Name=lab(bus), MeasV="YES", VName=vn, PU="NO")
        g_ = cv.add_component("master", "pgb", x + 4, y + 2, 0); g_.parameters(Name=vn); gp = list(g_.ports().values())[0]; dlab(gp.x, gp.y, vn)
        count("vchan")
    L("placed:", CNT)
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
    pscad.quit()
