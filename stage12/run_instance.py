r"""Run one PSCAD case in its OWN PSCAD instance (parallel runs; Educational allows 8 simultaneous EMTDC runs).

Each case lives in its own folder with the project name kept as `ib6`, so the build makes `ib6.map` and a
snapshot of ib6 stays valid (a renamed project cannot read it). Snapshot workflow (S26 §4): build first, then
copy the .snp into the build folder (a rebuild wipes it), then run, and check `-start-snap` in the config.

usage: python stage12/run_instance.py <folder> [--snap <path to .snp>] [--set k=v,...] [--build-only]
  --set: project run settings written before the build (e.g. time_duration=4,StartType=1,startup_filename=x.snp)
Writes <folder>/run_instance.log; the PSOUT ends up in <folder>/ib6.gf81_x86/.

Slots (S27): the build/run happens in one of 8 FIXED folders C:\PSCAD_work\slots\slot1..8 (a lock file per slot),
and the build folder is moved back to <folder> at the end. Reason: each ib6.exe listens on 0.0.0.0, and Windows
Firewall asks once per exe PATH - a fixed set of paths means at most 8 prompts ever instead of one per experiment.
Blocking or allowing does not affect the run (measured: c2/c5 blocked, same progress). --noslot runs in <folder>.
"""
import argparse, os, shutil, sys, time
import mhi.pscad

ap = argparse.ArgumentParser()
ap.add_argument("folder"); ap.add_argument("--snap"); ap.add_argument("--set", default="")
ap.add_argument("--build-only", action="store_true"); ap.add_argument("--noslot", action="store_true")
a = ap.parse_args()
fold = os.path.abspath(a.folder)
logf = open(os.path.join(fold, "run_instance.log"), "a", buffering=1)
SLOTS = r"C:\PSCAD_work\slots"


def pid_alive(pid):
    import subprocess
    return str(pid) in subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout


def take_slot():
    os.makedirs(SLOTS, exist_ok=True)
    while True:
        for k in range(1, 9):
            lk = os.path.join(SLOTS, f"slot{k}.lock")
            if os.path.exists(lk):
                try:
                    if pid_alive(int(open(lk).read().split()[0])): continue
                    os.remove(lk)                         # stale lock (its runner is gone)
                except Exception:
                    continue
            try:
                fd = os.open(lk, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                continue
            os.write(fd, f"{os.getpid()} {fold}".encode()); os.close(fd)
            return k, lk
        time.sleep(20)


def log(*m):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in m); print(s); logf.write(s + "\n")


os.environ.pop("NoDefaultCurrentDirectoryInExePath", None)   # else cmd will not run ib6.exe from its folder
lock = None
if a.noslot:
    work = fold
else:
    k, lock = take_slot(); work = os.path.join(SLOTS, f"slot{k}")
    os.makedirs(work, exist_ok=True)
    if os.path.isdir(os.path.join(work, "ib6.gf81_x86")): shutil.rmtree(os.path.join(work, "ib6.gf81_x86"))
    for f in os.listdir(work):
        if os.path.isfile(os.path.join(work, f)): os.remove(os.path.join(work, f))
    shutil.copy(os.path.join(fold, "ib6.pscx"), work)
    log(f"slot {k}: {work}")
bld = os.path.join(work, "ib6.gf81_x86")
log("launch PSCAD instance for", fold)
pscad = mhi.pscad.launch(minimize=True, splash=False, timeout=60)
try:
    log("licensed:", pscad.licensed())
    if not pscad.licensed():
        certs = pscad.get_available_certificates()
        log("certificates:", certs)
        c = next(iter(certs.values())) if isinstance(certs, dict) else certs[0]
        pscad.get_certificate(c); log("licensed after acquire:", pscad.licensed())
    pscad.load(os.path.join(work, "ib6.pscx"))
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
    if lock:
        time.sleep(5)
        dst = os.path.join(fold, "ib6.gf81_x86")
        try:
            if os.path.isdir(dst): shutil.rmtree(dst)
            if os.path.isdir(bld): shutil.move(bld, dst)
            shutil.copy(os.path.join(work, "ib6.pscx"), os.path.join(fold, "ib6_as_run.pscx"))
            log("results moved back to", dst)
        except Exception as e:
            log("move back failed:", e)
        os.remove(lock)
