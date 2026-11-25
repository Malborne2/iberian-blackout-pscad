r"""Bench lt8 (S30): units of a constant-valued master:varrlc shunt (R / L / C) as used by build_v2.py.

usage: python iberia_eq\pscad\bench_varrlc.py <R|L|C>
Stiff 400 kV source (source3, R 0.01 ohm) -> multimeter (P, Q 3-phase totals, S30) -> varrlc to ground, sized by the
build_v2 formulas for 100 MW / 100 Mvar / -100 Mvar at 400 kV:  R = V^2/P = 1,600 ohm, L = V^2/(w Q) = 5.093 H,
C = Q/(w V^2) * 1e6 = 1.989 uF (if the C field is in uF). Prints the measured P and Q over 0.3-0.5 s.
"""
import os, sys, time, glob, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
kind = sys.argv[1]
WORK = rf"C:\PSCAD_work\lt8_{kind}"; os.makedirs(WORK, exist_ok=True); PSCX = os.path.join(WORK, "lt8.pscx")
t = open(r"C:\PSCAD_work\lt6\lt6_template.pscx", encoding="utf-8").read().replace("lt6:", "lt8:").replace('name="lt6"', 'name="lt8"')
open(PSCX, "w", encoding="utf-8").write(t)
import mhi.pscad
os.environ["PATH"] = os.path.join(WORK, "lt8.gf81_x86") + os.pathsep + os.environ.get("PATH", "")
pscad = mhi.pscad.launch(minimize=False, splash=False, timeout=60)
try:
    if not pscad.licensed():
        c = pscad.get_available_certificates(); c = next(iter(c.values())) if isinstance(c, dict) else c[0]; pscad.get_certificate(c)
    pscad.load(PSCX); prj = pscad.project("lt8"); cv = prj.canvas("Main")
    def lab(x, y, n): d = cv.add_component("master", "datalabel", x, y, 0); d.parameters(Name=n)
    sr = cv.add_component("master", "source3", 10, 20, 0); sr.parameters(Type="R", R1s="0.01 [ohm]", Vm="400.0 [kV]", F="50.0 [Hz]", F0="50.0 [Hz]")
    cv.add_component("master", "ground", 8, 22, 0); cv.create_wire((8, 20), (8, 22))
    mm = cv.add_component("master", "multimeter", 18, 20, 0)
    mm.parameters(MeasPh="0", RMS="1", Vrms="VB", MeasP="1", P="PB", MeasQ="1", Q="QB", S="1.0", BaseV="400")
    cv.create_wire((12, 20), (17, 20))
    W = 2 * math.pi * 50; val = {"R": ("0", dict(R=f"{400 ** 2 / 100:.6g}")), "L": ("1", dict(L=f"{400 ** 2 / (W * 100):.6g}")),
                                  "C": ("2", dict(C=f"{100 / (W * 400 ** 2) * 1e6:.6g}"))}[kind]
    v = cv.add_component("master", "varrlc", 26, 20, 0); v.parameters(RLC=val[0], **val[1]); print("varrlc", v.parameters())
    cv.create_wire((19, 20), (26, 20)); cv.add_component("master", "ground", 28, 22, 0); cv.create_wire((28, 20), (28, 22))
    for i, n in enumerate(("VB", "PB", "QB")):
        lab(40, 20 + 4 * i, n); g = cv.add_component("master", "pgb", 46, 20 + 4 * i, 0); g.parameters(Name=n)
        q = list(g.ports().values())[0]; cv.create_wire((40, 20 + 4 * i), (q.x, q.y))
    prj.parameters(time_duration="0.5", time_step="20", sample_step="200", PlotType="1", StartType="0")
    prj.save(); prj.build()
    errs = [getattr(m, "text", m) for m in prj.messages() if str(getattr(m, "status", "")).lower() == "error"]
    if errs: print("BUILD ERRORS", errs); raise SystemExit(1)
    t0 = time.time(); prj.run(); OUT = os.path.join(WORK, "lt8.gf81_x86")
    while True:
        time.sleep(3)
        outs = glob.glob(os.path.join(OUT, "lt8_*.out"))
        if outs and os.path.getmtime(outs[0]) > t0 and not pscad.is_busy():
            try:
                if float(open(outs[0]).read().rstrip().split("\n")[-1].split()[0]) >= 0.499: break
            except Exception: pass
        if time.time() - t0 > 300: raise RuntimeError("timeout")
finally:
    pscad.quit()
from legacy_out import load
tt, ch = load(OUT, "lt8"); m = (tt > 0.3)
print(f"{kind}: V {ch['VB'][m].mean():.4f} pu  P {ch['PB'][m].mean():+.2f} MW  Q {ch['QB'][m].mean():+.2f} Mvar   (expected "
      + {"R": "P +100, Q 0", "L": "P 0, Q +100", "C": "P 0, Q -100 if C is in uF"}[kind] + ")")
