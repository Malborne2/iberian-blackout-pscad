r"""Run the built v2 case in its own visible PSCAD (S30). Copies the outputs to C:\PSCAD_work\v2_runs\<tag>.

usage: python iberia_eq\pscad\run_v2.py <tag> --dur 10 [--snap 8.0] [--from <snp>] [--sample 200] [--step 20] [--work C:\PSCAD_work\v2]
  --snap T : write a snapshot at T s (<tag>.snp, copied to the run folder)
  --from F : start from snapshot file F (copied into the build folder after the build; skill P10)
Completion = the last .out sample reaches the end time; the EMTDC log is printed on error (S30 sec 1 fault capture).
"""
import argparse, glob, os, shutil, sys, time
import mhi.pscad

ap = argparse.ArgumentParser()
ap.add_argument("tag"); ap.add_argument("--dur", type=float, default=10.0); ap.add_argument("--snap", type=float)
ap.add_argument("--from", dest="frm"); ap.add_argument("--sample", default="200"); ap.add_argument("--step", default="20")
ap.add_argument("--work", default=r"C:\PSCAD_work\v2sld")
a = ap.parse_args()
OUTD = os.path.join(r"C:\PSCAD_work\v2_runs", a.tag); os.makedirs(OUTD, exist_ok=True)
BUILD = os.path.join(a.work, "v2.gf81_x86")
log = open(os.path.join(OUTD, "run.log"), "w")
def L(*x): print(*x, flush=True); print(*x, file=log, flush=True)
os.environ["PATH"] = BUILD + os.pathsep + os.environ.get("PATH", "")      # S30 run-environment fix
pscad = mhi.pscad.launch(minimize=False, splash=False, timeout=60)
try:
    if not pscad.licensed():
        c = pscad.get_available_certificates(); c = next(iter(c.values())) if isinstance(c, dict) else c[0]; pscad.get_certificate(c)
    pscad.load(os.path.join(a.work, "v2.pscx")); prj = pscad.project("v2")
    prm = dict(time_duration=str(a.dur), time_step=a.step, sample_step=a.sample, PlotType="1")
    if a.frm:
        prm.update(StartType="1", startup_filename=os.path.basename(a.frm))
    else:
        prm.update(StartType="0")
    if a.snap:
        prm.update(SnapType="1", SnapTime=str(a.snap), snapshot_filename=f"{a.tag}.snp")
    else:
        prm.update(SnapType="0")
    prj.parameters(**prm); L("run parameters:", {k: prj.parameters().get(k) for k in prm})
    prj.build()
    errs = [getattr(m, "text", m) for m in prj.messages() if str(getattr(m, "status", "")).lower() == "error"]
    if errs: L("BUILD ERRORS:", errs[:10]); raise SystemExit(1)
    if a.frm: shutil.copy(a.frm, os.path.join(BUILD, os.path.basename(a.frm)))
    t0 = time.time(); prj.run(); last = -1
    while True:
        time.sleep(10)
        txt = prj.output() or ""
        if "stopped unexpectedly" in txt or ("error" in txt.lower() and "simulation has ended" not in txt.lower() and "run completed" not in txt.lower()):
            L("EMTDC OUTPUT (tail):"); L(txt[-3000:]); raise SystemExit(2)
        outs = sorted(glob.glob(os.path.join(BUILD, "v2_*.out")))
        tl = None
        if outs and os.path.getmtime(outs[0]) > t0:
            try: tl = float(open(outs[0]).read().rstrip().split("\n")[-1].split()[0])
            except Exception: tl = None
        if tl is not None and int(tl) != last and int(time.time() - t0) % 60 < 10:
            L(f"[{time.time() - t0:5.0f} s wall] simulated {tl:.2f} s"); last = int(tl)
        if tl is not None and tl >= a.dur - 1e-3 and not pscad.is_busy(): break
        if "run completed" in txt.lower() and tl is not None and tl >= a.dur - 0.01: break
    L(f"run done: {a.dur} s simulated in {time.time() - t0:.0f} s wall ({(time.time() - t0) / a.dur:.1f} s per simulated s)")
finally:
    pscad.quit()
for f in glob.glob(os.path.join(BUILD, "v2_*.out")) + glob.glob(os.path.join(BUILD, "v2.infx")) + glob.glob(os.path.join(BUILD, "*.snp")):
    shutil.copy(f, OUTD)
L("outputs copied to", OUTD)
