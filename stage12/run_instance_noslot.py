r"""Run one PSCAD case in its OWN PSCAD instance (parallel runs; Educational allows 8 simultaneous EMTDC runs).

Each case lives in its own folder with the project name kept as `ib6`, so the build makes `ib6.map` and a
snapshot of ib6 stays valid (a renamed project cannot read it). Snapshot workflow (S26 §4): build first, then
copy the .snp into the build folder (a rebuild wipes it), then run, and check `-start-snap` in the config.

usage: python stage12/run_instance.py <folder> [--snap <path to .snp>] [--set k=v,...] [--build-only]
  --set: project run settings written before the build (e.g. time_duration=4,StartType=1,startup_filename=x.snp)
Writes <folder>/run_instance.log; the PSOUT stays in <folder>/ib6.gf81_x86/.
"""
import argparse, os, shutil, sys, time
import mhi.pscad

ap = argparse.ArgumentParser()
ap.add_argument("folder"); ap.add_argument("--snap"); ap.add_argument("--set", default="")
ap.add_argument("--build-only", action="store_true")
a = ap.parse_args()
fold = os.path.abspath(a.folder); bld = os.path.join(fold, "ib6.gf81_x86")
logf = open(os.path.join(fold, "run_instance.log"), "a", buffering=1)


def log(*m):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in m); print(s); logf.write(s + "\n")


os.environ.pop("NoDefaultCurrentDirectoryInExePath", None)   # else cmd will not run ib6.exe from its folder
log("launch PSCAD instance for", fold)
pscad = mhi.pscad.launch(minimize=True, splash=False, timeout=60)
try:
    log("licensed:", pscad.licensed())
    if not pscad.licensed():
        certs = pscad.get_available_certificates()
        log("certificates:", certs)
        c = next(iter(certs.values())) if isinstance(certs, dict) else certs[0]
        pscad.get_certificate(c); log("licensed after acquire:", pscad.licensed())
    pscad.load(os.path.join(fold, "ib6.pscx"))
    prj = pscad.project("ib6")
    if a.set:
        kv = dict(x.split("=", 1) for x in a.set.split(","))
        prj.parameters(**kv)
        if "StartType" not in kv:
            log("note: StartType not given (set_project_parameters may reset it)")
    log("settings:", {k: prj.parameters()[k] for k in ("time_duration", "time_step", "StartType", "SnapType",
                                                        "snapshot_filename", "startup_filename")})
    prj.save()
    prj.build()
    msgs = [m for m in prj.messages() if str(getattr(m, "status", "")).lower() == "error"]
    log("build errors:", len(msgs), [getattr(m, "text", m) for m in msgs[:5]])
    if msgs or a.build_only:
        sys.exit(0)
    if a.snap:
        shutil.copy(a.snap, bld); log("snapshot copied:", os.path.basename(a.snap))
    t0 = time.time(); log("run start")
    prj.run()
    time.sleep(15)
    n = 0
    while pscad.is_busy() or str(prj.run_status()).lower() not in ("none", "(none, none)", "(none,none)"):
        time.sleep(30); n += 1
        if n % 10 == 0:
            log("running:", prj.run_status())
    log(f"run end, wall {(time.time() - t0) / 60:.1f} min")
    for f in os.listdir(bld):
        if f.endswith(".config"):
            log("config:", open(os.path.join(bld, f)).read().replace("\n", " | "))
finally:
    try:
        pscad.quit()
    except Exception as e:
        log("quit:", e)
