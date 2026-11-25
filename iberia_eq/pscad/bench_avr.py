r"""Bench lt7 (v2 change A, RUNLOG S30): one SyncUnit behind a 15 % step-up on a 400 kV grid whose voltage ramps +3 %.

usage: python iberia_eq\pscad\bench_avr.py <tag> <XCc> <Kdrp> <Kiq> [duration_s]
  e.g. base 0 0 0 | ldc -0.12 0 0 | qloop -0.12 3.0 0.005
Builds C:\PSCAD_work\lt7_<tag>\lt7.pscx from the lt6 template (empty Main) + the SyncUnit definition of the S29 ib6 case,
patched with iberia_eq\pscad\add_qloop.py; runs it in its own PSCAD instance; writes <tag>.csv (t, QOUT, VIT, DVR, QERR,
VHV) and prints means over windows.

Grid: source3, R-R//L, Z1 = 16 ohm (Ssc 10 GVA), EV = 400 kV x (1 + 0.03 * clip((t - 20)/30, 0, 1)).
Unit: S 1,111 MVA, P0 1,000 MW, H 3 s, KA 40 / KF 0.03 / TF 1 (ib6 values), governor off, Tstart 0.5 s.
Expected (prediction before the run): with XCc = 0 the AVR holds the terminal and the unit absorbs most of the 12 kV
grid rise: dQ ~ dV / (X_T + X_g) ~ 0.03 / (0.15 + 0.11) ~ -0.115 pu = -128 Mvar. With XCc = -0.12 (regulated point
0.03 pu from the HV side) the unit holds the HV side harder: dQ ~ 0.03 / (0.03 + 0.11) ~ -0.21 pu = -238 Mvar, and
the HV voltage rises less. With the outer loop (Kdrp 3) the steady state is dQ = -Kdrp * dVIT, i.e. a weak droop.
"""
import csv, os, shutil, sys, time, subprocess
import xml.etree.ElementTree as ET
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
tag, XCc, Kdrp, Kiq = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
DUR = sys.argv[5] if len(sys.argv) > 5 else "80.0"
WORK = rf"C:\PSCAD_work\lt7_{tag}"; os.makedirs(WORK, exist_ok=True)
PSCX = os.path.join(WORK, "lt7.pscx")
log = open(os.path.join(WORK, "bench.log"), "w")
def L(*x): print(*x, flush=True); print(*x, file=log, flush=True)

# ---- project file: lt6 template (empty Main) renamed lt7, + patched SyncUnit ----
t = open(r"C:\PSCAD_work\lt6\lt6_template.pscx", encoding="utf-8").read().replace("lt6:", "lt7:").replace('name="lt6"', 'name="lt7"')
open(PSCX, "w", encoding="utf-8").write(t)
root = ET.parse(PSCX).getroot(); defs = root.find("definitions")
src = ET.parse(r"C:\PSCAD_work\s29\ib6.pscx").getroot()
su = [d for d in src.find("definitions") if d.get("name") == "SyncUnit"][0]
defs.append(su)
open(PSCX, "w", encoding="utf-8").write(ET.tostring(root, encoding="unicode"))
if os.environ.get("NOPATCH") != "1":
    r = subprocess.run([sys.executable, os.path.join(HERE, "add_qloop.py"), "--pscx", PSCX], capture_output=True, text=True); L(r.stdout.strip(), r.stderr.strip())
    r = subprocess.run([sys.executable, os.path.join(HERE, "add_xt.py"), "--pscx", PSCX], capture_output=True, text=True); L(r.stdout.strip(), r.stderr.strip())
else: L("NOPATCH: original SyncUnit")

S, P0 = 1111.0, 1000.0
import mhi.pscad
# This session sets NoDefaultCurrentDirectoryInExePath=1, which stops EMTDC's batch file from starting <case>.exe from its
# own folder ('lt7.exe' is not recognized). The protection is kept; the build folder is put on the PATH of the PSCAD
# we launch instead (RUNLOG S30).
os.environ['PATH'] = os.path.join(WORK, 'lt7.gf81_x86') + os.pathsep + os.environ.get('PATH', '')
pscad = mhi.pscad.launch(minimize=False, splash=False, timeout=60)   # visible (owner request, S30)
try:
    if not pscad.licensed():
        c = pscad.get_available_certificates(); c = next(iter(c.values())) if isinstance(c, dict) else c[0]; pscad.get_certificate(c)
    pscad.load(PSCX); prj = pscad.project("lt7"); cv = prj.canvas("Main")
    def lab(x, y, n): d = cv.add_component("master", "datalabel", x, y, 0); d.parameters(Name=n); return d
    def const(x, y, v, n): c = cv.add_component("master", "const", x, y, 0); c.parameters(Value=v); q = list(c.ports().values())[0]; lab(q.x, q.y, n)
    def summ(x, y, a_, b_, o, fsign="SUBTRACT"):
        s = cv.add_component("master", "sumjct", x, y, 0); s.parameters(F=fsign); P = s.ports()
        lab(P["IND"].x, P["IND"].y, a_); lab(P["INF"].x, P["INF"].y, b_); lab(P["OUT"].x, P["OUT"].y, o)
    def blk(nm, x, y, i, o, **pv):
        b = cv.add_component("master", nm, x, y, 0); b.parameters(**pv); P = b.ports()
        ki = [k for k in P if k in ("I", "IN")][0]; ko = [k for k in P if k in ("O", "OUT")][0]
        lab(P[ki].x, P[ki].y, i); lab(P[ko].x, P[ko].y, o); return b
    def pgb(x, y, n):
        lab(x, y, n); g = cv.add_component("master", "pgb", x + 6, y, 0); g.parameters(Name=n); q = list(g.ports().values())[0]; cv.create_wire((x, y), (q.x, q.y))
    # grid source, external V
    sr = cv.add_component("master", "source3", 10, 20, 0)
    sr.parameters(Ctrl="EXTERNAL"); sr.parameters(Type="4", Imp="IMPEDANCE", Z1="16.0 [ohm]", Phi1="85.0 [deg]", Vm="400.0 [kV]", F="50.0 [Hz]", F0="50.0 [Hz]")
    P = sr.ports(); L("source ports", {k: (v.x, v.y) for k, v in P.items()}); L("source", {k: sr.parameters().get(k) for k in ("Ctrl", "Type", "Imp", "Z1", "Phi1")})
    lab(P["EV"].x, P["EV"].y, "EVS"); lab(P["EF"].x, P["EF"].y, "FREQ"); lab(P["EP"].x, P["EP"].y, "EPH")
    cv.add_component("master", "ground", 8, 22, 0); cv.create_wire((8, 20), (8, 22))
    const(20, 44, "50.0", "FREQ")
    if os.environ.get("PHSTEP") == "1":                    # grid phase step +10 deg at 60 s: excites the rotor swing (S30 sec 5)
        ts2 = cv.add_component("master", "time-sig", 20, 34, 0); q2 = list(ts2.ports().values())[0]; lab(q2.x, q2.y, "TT2")
        blk("compare", 30, 34, "TT2", "STP", X="60.0", OL="0.0", OH="1.0"); blk("gain", 40, 34, "STP", "EPH", G=f"{np.radians(10.0):.6f}")
    else:
        const(20, 40, "0.0", "EPH")
    ts = cv.add_component("master", "time-sig", 20, 50, 0); q = list(ts.ports().values())[0]; lab(q.x, q.y, "TT")
    const(20, 54, "20.0", "K20"); summ(30, 50, "TT", "K20", "T20")
    blk("gain", 40, 50, "T20", "R0", G=f"{1 / 30:.6f}"); blk("hardlimit", 50, 50, "R0", "RMP", LL="0.0", UL="1.0")
    blk("gain", 60, 50, "RMP", "R12", G="12.0"); const(60, 56, "400.0", "K400"); summ(70, 50, "K400", "R12", "EVS", fsign="ADD")
    # multimeter on the HV side, then the step-up, then the unit
    mm = cv.add_component("master", "multimeter", 18, 20, 0); MP = mm.ports(); L("multimeter ports", {k: (v.x, v.y) for k, v in MP.items()})
    mm.parameters(MeasPh="0", RMS="1", Vrms="VHV", MeasP="1", P="PHV", MeasQ="1", Q="QHV", S="1.0", BaseV="400")
    L("multimeter", {k: mm.parameters().get(k) for k in ("RMS", "Vrms", "MeasP", "P", "MeasQ", "Q", "S", "BaseV")})
    DIRECT = os.environ.get("DIRECT") == "1"                  # v2: Spanish units directly on the 400 kV bus, no step-up (S30, owner decision)
    xf = None if DIRECT else cv.add_component("master", "xfmr-3p2w", 30, 20, 0); XP = {} if DIRECT else xf.ports(); L("xfmr ports", {k: (v.x, v.y) for k, v in XP.items()})
    if xf is not None: xf.parameters(Tmva=f"{S}", Xl="0.15 [pu]", V1="400", V2="400", NLL="0.0016 [pu]", Im1="2.0 [%]", Sat="0", YD1="0", YD2="0")
    su = cv.add_component("lt7", "SyncUnit", 50, 20, 0); UP = su.ports(); L("SyncUnit ports", {k: (v.x, v.y) for k, v in UP.items()})
    ph0 = np.arcsin(P0 * ((0.0 if DIRECT else 0.15) * 400 ** 2 / S + 16.0) / 400 ** 2)
    su.parameters(Sbase=f"{S}", Vbase="400", VbaseLN="230.9401", Ibase=f"{S / (3 ** 0.5 * 400):.4f}", H="3.0", P0=f"{P0}", Q0="0.0",
                  V0="1.0", Ph0=f"{ph0:.5f}", Vctl="0", Tstart="0.5", Pmec="0.0", Kgov="0.0", Tgov="2.0", GovLim="0.0",
                  KA="40", KF="0.03", TF="1.0", Ttrip="1e6", Ptrip="0.0", **({} if os.environ.get("NOPATCH") == "1" else dict(XCc=XCc, Kdrp=Kdrp, Kiq=Kiq)))
    XT = float(os.environ.get("XT", 0.0))                  # lumped step-up reactance (pu machine base) added to every machine reactance
    if XT and os.environ.get("NOPATCH") != "1":
        su.parameters(XmD=f"{1.79 + XT}", XmD1=f"{0.169 + XT}", XmD2=f"{0.135 + XT}", XmQ=f"{1.71 + XT}", XmQ1=f"{0.228 + XT}",
                      XmQ2=f"{0.2 + XT}", XmP=f"{0.130 + XT}")
        L("lumped Xt", XT, {k: su.parameters().get(k) for k in ("XmD", "XmD2", "XmQ2")})
    L("SyncUnit", {k: su.parameters().get(k) for k in ("Sbase", "P0", "Ph0")})
    pS, pM1, pM2 = P["N3"] if "N3" in P else list(P.values())[-1], MP[list(MP)[0]], MP[list(MP)[1]]
    L("direct" if DIRECT else "via step-up")
    # wiring from the read-back ports (probe run, RUNLOG S30): N3 (12,20) -> mm A (17,20); mm B (19,20) -> xf N1 (27,20);
    # xf N2 (32,20) -> unit T (53,20); xf neutrals G1 (29,22), G2 (30,20) grounded
    assert (pS.x, pS.y) == (12, 20) and (MP["A"].x, MP["A"].y) == (17, 20) and (UP["T"].x, UP["T"].y) == (53, 20)
    cv.create_wire((12, 20), (17, 20))
    if DIRECT:
        cv.create_wire((19, 20), (53, 20))
    else:
        assert (XP["N1"].x, XP["N1"].y) == (27, 20)
        cv.create_wire((19, 20), (27, 20)); cv.create_wire((32, 20), (53, 20))
        cv.add_component("master", "ground", 29, 24, 0); cv.create_wire((29, 22), (29, 24))
    cv.add_component("master", "ground", 31, 24, 0); cv.create_wire((30, 20), (30, 21), (31, 21), (31, 24)) if False else None
    for i, n in enumerate(("VHV", "QHV", "PHV", "EVS")): pgb(80, 20 + 4 * i, n)
    prj.parameters(time_duration=DUR, time_step="20", sample_step="1000", PlotType="1", StartType="0")
    prj.save(); prj.build()
    msgs = [(str(getattr(m, "status", "")), getattr(m, "text", m)) for m in prj.messages() if str(getattr(m, "status", "")).lower() in ("error", "warning")]
    for m in msgs: L("MSG", m)
    if any(s_.lower() == "error" for s_, _ in msgs): raise SystemExit(1)
    OUT = os.path.join(WORK, "lt7.gf81_x86"); t0 = time.time(); prj.run()
    while True:
        time.sleep(5)
        txt = prj.output() or ""
        if int(time.time() - t0) % 30 < 5: L(f"[{time.time() - t0:.0f} s] run log tail:", txt[-600:].replace(chr(10), " | "))
        if any(k in txt.lower() for k in ("error", "terminated", "abort", "fatal")) and "simulation has ended" not in txt.lower():
            L("EMTDC OUTPUT (tail):"); L(txt[-3000:]); raise SystemExit(2)
        outs = [os.path.join(OUT, f) for f in os.listdir(OUT) if f.endswith(".out")] if os.path.isdir(OUT) else []
        if outs and all(os.path.getmtime(f) > t0 for f in outs) and not pscad.is_busy():
            try:
                if float(open(sorted(outs)[0]).read().split("\n")[-2].split()[0]) >= float(DUR) - 0.01: break
            except Exception: pass
        if time.time() - t0 > float(os.environ.get("RUNTIMEOUT", 1800)): L("TIMEOUT; log:", txt[-2000:]); raise RuntimeError("timeout")
    L("run done", round(time.time() - t0), "s")
finally:
    pscad.quit()

# ---- results (legacy output, PlotType 1) ----
r_ = subprocess.run([sys.executable, os.path.join(HERE, "bench_avr_read.py"), tag], capture_output=True, text=True)
L(r_.stdout.strip(), r_.stderr.strip()[-500:])
