r"""Run the built v2 case in its own visible PSCAD (S30). Copies the outputs to C:\PSCAD_work\v2_runs\<tag>.

usage: python iberia_eq\pscad\run_v2.py <tag> --dur 10 [--snap 8.0] [--from <snp>] [--sample 200] [--step 20] [--work C:\PSCAD_work\v2]
  --snap T : write a snapshot at T s (<tag>.snp, copied to the run folder)
  --from F : start from snapshot file F (copied into the build folder after the build; skill P10)
Completion = the last .out sample reaches the end time and EMTDC ends with status code 0.
Error capture (S30 sec 9; the old check missed "Abnormal termination ... Status code = 2000" because that output also
contains "Simulation has ended"): after the build and on every poll the PSCAD message list is read (status error, and the
warnings skill P6.3 treats as errors), the EMTDC output is parsed for its status code and abort lines, and a run with no
new samples for --stall minutes is stopped. Any of these: messages + output tail to run.log, exit code 2.
"""
import argparse, glob, os, re, shutil, subprocess, sys, time
import mhi.pscad

ap = argparse.ArgumentParser()
ap.add_argument("tag"); ap.add_argument("--dur", type=float, default=10.0); ap.add_argument("--snap", type=float)
ap.add_argument("--from", dest="frm"); ap.add_argument("--step", default="20")
ap.add_argument("--sample", default="1000")   # us; S30 sec 23: at 200 us each PSCAD process used 1.2-1.9 cores
ap.add_argument("--work", default=r"C:\PSCAD_work\v2sld"); ap.add_argument("--stall", type=float, default=10.0)
ap.add_argument("--set", nargs="*", default=[])       # extra project settings key=value (S30 sec 23: compileF_opt_level, threads, ...)
ap.add_argument("--affinity")                          # logical CPUs for the solver, e.g. "0" or "8,10" (0-7 = fast Zen 5 cores)
ap.add_argument("--priority")                          # solver priority class: High / AboveNormal / Normal
ap.add_argument("--gui-affinity")                      # logical CPUs for this run's PSCAD window, e.g. "8-23" (compact cores)
ap.add_argument("--health-until", type=float)        # stop if the machines' frequency spread exceeds --hspread before this model time
ap.add_argument("--hspread", type=float, default=0.5) # Hz (S30 sec 21 lesson 1)
a = ap.parse_args()
LOCK = os.path.join(a.work, "run_v2.lock")                           # one run per work folder (S30: duplicate launches
if os.path.exists(LOCK):                                              # wrote into the same build folder)
    try:
        opid = int(open(LOCK).read().split()[0])
        import subprocess as _sp
        alive = str(opid) in _sp.run(["tasklist", "/FI", f"PID eq {opid}", "/NH"], capture_output=True, text=True).stdout
    except Exception: alive = False
    if alive: print(f"REFUSED: {a.work} is in use by run_v2 PID {opid}"); raise SystemExit(6)
open(LOCK, "w").write(f"{os.getpid()} {a.tag}")
import atexit; atexit.register(lambda: os.path.exists(LOCK) and open(LOCK).read().split()[0] == str(os.getpid()) and os.remove(LOCK))
OUTD = os.path.join(r"C:\PSCAD_work\v2_runs", a.tag); os.makedirs(OUTD, exist_ok=True)
BUILD = os.path.join(a.work, "v2.gf81_x86")
log = open(os.path.join(OUTD, "run.log"), "w")
def L(*x): print(*x, flush=True); print(*x, file=log, flush=True)
L("work:", a.work)                                                    # read by run_dashboard.py
L(f"start: {time.time():.0f}")                                         # dashboard: Windows keeps a rewritten run.log's creation time
for _f in glob.glob(os.path.join(BUILD, "v2_*.out")): os.remove(_f)   # no stale samples from the previous run
def _hook(et, ev, tb):                                                # S30: any crash is visible in run.log (dashboard)
    import traceback; L("RUN FAILED: " + "".join(traceback.format_exception_only(et, ev)).strip())
    traceback.print_exception(et, ev, tb)
sys.excepthook = _hook
FREE_MIN_GB = 15.0                                                    # owner rule 2026-11-26: C: reached 0 MB with 6 runs
free_gb = shutil.disk_usage(r"C:\PSCAD_work").free / 1e9
if free_gb < FREE_MIN_GB:
    L(f"RUN FAILED: only {free_gb:.1f} GB free on C: (floor {FREE_MIN_GB:.0f} GB); delete recorded run outputs first"); raise SystemExit(4)
BADW = ("short circuit", "open circuit", "floating", "unresolved", "source contention", "below range", "above range", "too small")
def check_msgs(prj):
    """-> (error texts, {warning text: count}) from PSCAD's message list; warnings in BADW count as errors (skill P6.3)."""
    errs, warns = [], {}
    for m in prj.messages():
        st = str(getattr(m, "status", "")).lower(); tx = f"{getattr(m, 'component', '') or ''} {getattr(m, 'text', m)}".strip()
        if st == "error": errs.append(tx)
        elif st == "warning":
            warns[tx] = warns.get(tx, 0) + 1
            if any(b in tx.lower() for b in BADW) and tx not in errs: errs.append(tx)
    return errs, warns
# Snapshot restarts must keep the clock (S25 trap, RUNLOG S30 sec 14): bit 32 of the project's `Advanced` flags is
# remove_time_offset. Set (default) = the clock restarts at 0 and the start-up switches (S2M 2 s, L2N 5 s) fire again on
# top of the restored state. --from clears it; cold runs set it. Edited in the .pscx before loading (P12);
# pscad_set_project_parameters rejects the flag.
PSCX = os.path.join(a.work, "v2.pscx"); txt_ = open(PSCX, encoding="utf-8").read()
m_ = re.search(r'(<param name="Advanced" value=")(\d+)(")', txt_)
if m_:
    adv = int(m_.group(2)); new_ = (adv & ~32) if a.frm else (adv | 32)
    if new_ != adv:
        open(PSCX, "w", encoding="utf-8").write(txt_[:m_.start(2)] + str(new_) + txt_[m_.end(2):])
    L(f"Advanced {adv} -> {new_} (remove_time_offset {'off: time continues from the snapshot' if a.frm else 'on'})")
os.environ["PATH"] = BUILD + os.pathsep + os.environ.get("PATH", "")      # S30 run-environment fix
import subprocess
def _pscad_pids():
    """Pscad.exe processes started by THIS script (children of this python): a failed launch must not close the
    PSCAD of another run that happened to start at the same time (rp_cascade was killed that way, S30 sec 19)."""
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='Pscad.exe'\" | Where-Object { $_.ParentProcessId -eq "
          + str(os.getpid()) + " } | ForEach-Object { $_.ProcessId }")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True).stdout
    return {int(x) for x in out.split() if x.strip().isdigit()}
# Stage watchdog (S30 sec 23, owner: a run that does not start must not wait for the 10-min stall check): every stage
# has a deadline; past it the run is logged as failed, this script's PSCAD and solver are killed and the script exits.
import threading as _thw
_STAGE = ["launch", time.time(), 300.0]                               # name, start, limit [s]
def stage(name, limit=None):
    _STAGE[:] = [name, time.time(), limit]
    if name: L(f"stage: {name} (limit {limit:.0f} s)" if limit else f"stage: {name}")
def _kill_own():
    ps = ("$p=Get-CimInstance Win32_Process; $k=$p|?{$_.ParentProcessId -eq " + str(os.getpid()) + "}; foreach($q in $k){ "
          "$p|?{$_.ParentProcessId -eq $q.ProcessId}|%{Stop-Process -Id $_.ProcessId -Force -EA 0}; Stop-Process -Id $q.ProcessId -Force -EA 0 }; "
          "$e='" + os.path.join(BUILD, "v2.exe").replace("/", "\\") + "'; $p|?{$_.Name -eq 'v2.exe' -and $_.ExecutablePath -eq $e}|%{Stop-Process -Id $_.ProcessId -Force -EA 0}")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True)
def _watchdog():
    while True:
        time.sleep(5)
        nm, ts, lim = _STAGE
        if nm and lim and time.time() - ts > lim:
            L(f"RUN FAILED: stage '{nm}' took more than {lim:.0f} s (hung launch / dialog / solver not starting)")
            _kill_own()
            if os.path.exists(LOCK): os.remove(LOCK)
            os._exit(6)
_thw.Thread(target=_watchdog, daemon=True).start()
stage("launch", 300)
for k_ in range(4):                                                  # S30: launch races when several start together
    before_ = _pscad_pids()
    try: pscad = mhi.pscad.launch(minimize=False, splash=False, timeout=60); break
    except (ConnectionRefusedError, OSError) as e_:
        orphans = _pscad_pids() - before_                            # the failed attempt's window would stay open
        for pid_ in orphans: subprocess.run(["taskkill", "/PID", str(pid_), "/F"], capture_output=True)
        L(f"launch attempt {k_ + 1} failed: {e_!r}; closed orphan PSCAD {sorted(orphans)}"); time.sleep(30 + 30 * k_)
else:
    L("RUN FAILED: PSCAD launch failed 4 times"); raise SystemExit(3)
try:
    # S30 sec 25: PSCAD's ip_address setting was the Tailscale address, so EMTDC connected back over Tailscale: with the
    # Cisco AnyConnect VPN up (or Tailscale down) the solver never started. Loopback works in every network state.
    if pscad.settings().get("ip_address") != "127.0.0.1": pscad.settings(ip_address="127.0.0.1")
    L("PSCAD ip_address:", pscad.settings().get("ip_address"))
    if not pscad.licensed():
        c = pscad.get_available_certificates(); c = next(iter(c.values())) if isinstance(c, dict) else c[0]; pscad.get_certificate(c)
    stage("load", 300); pscad.load(os.path.join(a.work, "v2.pscx")); prj = pscad.project("v2")
    # With the clock kept on a restart, time_duration is the length ADDED (sld_snapchk ran on past 32 s, S30 sec 14):
    # --dur stays the END time; the snapshot time is read from the run.log next to the .snp ('SnapTime').
    tsnap = 0.0
    if a.frm:
        rl = os.path.join(os.path.dirname(a.frm), "run.log")
        ms = re.search(r"'SnapTime': '?([\d.]+)", open(rl).read()) if os.path.exists(rl) else None
        if not ms: L("RUN FAILED: snapshot time unknown (no run.log with SnapTime next to the .snp)"); raise SystemExit(5)
        tsnap = float(ms.group(1)); L(f"snapshot time {tsnap} s: run {tsnap} -> {a.dur} s")
    prm = dict(time_duration=f"{a.dur - tsnap:g}", time_step=a.step, sample_step=a.sample, PlotType="1")
    if a.frm:
        prm.update(StartType="1", startup_filename=os.path.basename(a.frm))
    else:
        prm.update(StartType="0")
    if a.snap:
        prm.update(SnapType="1", SnapTime=str(a.snap), snapshot_filename=f"{a.tag}.snp")
    else:
        prm.update(SnapType="0")
    for kv in a.set: k_, v_ = kv.split("=", 1); prm[k_] = v_
    prj.parameters(**prm); L("run parameters:", {k: prj.parameters().get(k) for k in prm})
    stage("build", 900); prj.build(); stage(None)
    errs, warns = check_msgs(prj)
    for w, k in warns.items(): L(f"build warning x{k}: {w}")
    if errs: L("BUILD ERRORS:"); [L("  ", e) for e in errs[:20]]; raise SystemExit(1)
    if a.frm: shutil.copy(a.frm, os.path.join(BUILD, os.path.basename(a.frm)))
    # S30 sec 23: prj.run() BLOCKS until the run ends (and rebuilds first); prj.start() after prj.build() does not start
    # the solver at all. Before this fix the progress / stall / health loop and the solver pin acted only after the run.
    # Now prj.run() runs in a thread and the loop below watches the output files only (no PSCAD calls during the run);
    # to stop a bad run it kills this run's solver, which ends prj.run().
    import threading as _th
    _rerr = []
    def _runner():
        try: prj.run()
        except Exception as e_: _rerr.append(repr(e_))
    stage("rebuild + solver start", 600); t0 = time.time(); _rt = _th.Thread(target=_runner, daemon=True); _rt.start()
    last = -1; t_prog = time.time(); tl_prev = None; t_first = None; tl_first = None
    if a.affinity or a.priority or a.gui_affinity:                                      # pin / prioritise this run's solver (S30 sec 23)
        import subprocess as _sp
        exe = os.path.join(BUILD, "v2.exe").replace("/", "\\")
        mask = sum(1 << int(x) for x in a.affinity.split(",")) if a.affinity else None
        ps_ = ("$t=(Get-Date).AddSeconds(900); do { $q=Get-CimInstance Win32_Process -Filter \"Name='v2.exe'\" | ? { $_.ExecutablePath -eq '"
               + exe + "' }; Start-Sleep -Milliseconds 500 } until ($q -or (Get-Date) -gt $t); if($q){ $pp=Get-Process -Id $q.ProcessId; "
               + (f"$pp.ProcessorAffinity=[IntPtr]{mask}; " if mask else "") + (f"$pp.PriorityClass='{a.priority}'; " if a.priority else "")
               + "'pinned ' + $q.ProcessId + ' mask ' + $pp.ProcessorAffinity + ' prio ' + $pp.PriorityClass } else { 'PIN FAILED: no v2.exe in 900 s' }")
        if a.gui_affinity:                                            # S30 sec 23: keep the GUI off the solver's fast core
            cpus = [x for s in a.gui_affinity.split(",") for x in (range(int(s.split("-")[0]), int(s.split("-")[1]) + 1) if "-" in s else [int(s)])]
            ps_ += ("; Get-CimInstance Win32_Process -Filter \"Name='Pscad.exe'\" | ? { $_.ParentProcessId -eq " + str(os.getpid())
                    + " } | % { $g=Get-Process -Id $_.ProcessId; $g.ProcessorAffinity=[IntPtr]" + str(sum(1 << c for c in cpus)) + "; ' gui ' + $g.Id + ' mask ' + $g.ProcessorAffinity }")
        def _pin():                                                   # in a thread: the progress loop must not wait for it
            _r = _sp.run(["powershell", "-NoProfile", "-Command", ps_], capture_output=True, text=True)
            L("solver:", (_r.stdout.strip() or "PIN FAILED: " + _r.stderr.strip()[-300:]), f"after {time.time() - t0:.0f} s")
        import threading as _th; _th.Thread(target=_pin, daemon=True).start()
    import xml.etree.ElementTree as ETx
    WS = []                                                           # (file no, column) of every SyncUnit Wspd channel
    def _ws_index():
        names = []
        for an in ETx.parse(os.path.join(BUILD, "v2.infx")).getroot().iter("Analog"):
            d = int(an.get("dim", "1")); n = an.get("name")
            names += [n] if d == 1 else [f"{n}[{k + 1}]" for k in range(d)]
        return [(i // 10 + 1, i % 10 + 1) for i, n in enumerate(names) if "SyncUnit(" in n and n.endswith(":Wspd")]
    def _spread():
        """frequency spread [Hz] of all machines at the latest common sample (S30 sec 21 lesson 1)."""
        if not WS:
            try: WS.extend(_ws_index())
            except Exception: return None
        fs = []
        for fno, col in WS:
            try:
                with open(os.path.join(BUILD, f"v2_{fno:02d}.out"), "rb") as fh:
                    fh.seek(0, 2); n = fh.tell(); fh.seek(max(0, n - 4000))
                    ln = fh.read().decode(errors="replace").strip().split("\n")[-2].split()
                fs.append(float(ln[col]) / (2 * 3.14159265))
            except Exception: return None
        return (max(fs) - min(fs)) if fs else None
    hbad = 0
    def kill_solver():
        exe_ = os.path.join(BUILD, "v2.exe").replace("/", "\\")
        subprocess.run(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_Process -Filter \"Name='v2.exe'\" | ? { $_.ExecutablePath -eq '"
                        + exe_ + "' } | % { Stop-Process -Id $_.ProcessId -Force }"], capture_output=True)
        _rt.join(120)
    def fail(why, txt=None):
        L("RUN FAILED:", why)
        if _rt.is_alive(): kill_solver()
        if txt is None:
            try: txt = prj.output() or ""
            except Exception: txt = ""
        try:
            e_, w_ = check_msgs(prj)
            for e in e_: L("  error:", e)
            for w, k in w_.items(): L(f"  warning x{k}: {w}")
        except Exception as x_: L("  (messages unavailable:", repr(x_), ")")
        L("EMTDC OUTPUT (tail):"); L(txt[-3000:]); raise SystemExit(2)
    while True:
        _rt.join(10)
        outs = sorted(glob.glob(os.path.join(BUILD, "v2_*.out")))
        tl = None
        if outs and os.path.getmtime(outs[0]) > t0:
            try:
                with open(outs[0], "rb") as fh:
                    fh.seek(0, 2); n_ = fh.tell(); fh.seek(max(0, n_ - 3000))
                    tl = float(fh.read().decode(errors="replace").strip().split("\n")[-2].split()[0])
            except Exception: tl = None
        if tl is not None and t_first is None: t_first, tl_first = time.time(), tl; L(f"solver writing after {t_first - t0:.0f} s (t = {tl:.3f} s)"); stage(None)
        if tl is not None and tl != tl_prev: t_prog = time.time(); tl_prev = tl
        if not _rt.is_alive():                                        # prj.run() returned: judge the end
            txt = prj.output() or ""
            sc = re.findall(r"Status code\s*=\s*(-?\d+)", txt)
            bad = [k for k in ("Abnormal termination", "Runtime Error", "stopped unexpectedly", "Simulation stopped", "ERROR:") if k in txt]
            if _rerr or bad or (sc and sc[-1] != "0"): fail(f"EMTDC: {bad} status code {sc[-1] if sc else '?'} {_rerr}", txt)
            e_, _ = check_msgs(prj)
            if e_: fail("PSCAD error messages", txt)
            outs = sorted(glob.glob(os.path.join(BUILD, "v2_*.out")))
            try: tl = float(open(outs[0]).read().rstrip().split("\n")[-1].split()[0])
            except Exception: tl = None
            if tl is None or tl < a.dur - 0.01: fail(f"run ended early at t = {tl}", txt)
            break
        if time.time() - t_prog > 60 * a.stall: fail(f"no new samples for {a.stall} min (last t = {tl_prev})")
        sp = _spread() if tl is not None else None
        if sp is not None and int(time.time() - t0) % 60 < 10: L(f"health: t = {tl:.2f} s, machine frequency spread {sp * 1000:.1f} mHz")
        if a.health_until and sp is not None and 8.0 < tl < a.health_until:
            hbad = hbad + 1 if sp > a.hspread else 0
            if hbad >= 2: fail(f"health: machine frequency spread {sp * 1000:.0f} mHz > {a.hspread * 1000:.0f} mHz at t = {tl:.2f} s")
        if tl is not None and int(tl) != last and int(time.time() - t0) % 60 < 10:
            L(f"[{time.time() - t0:5.0f} s wall] simulated {tl:.2f} s"); last = int(tl)
    if t_first is not None and tl - tl_first > 0:
        L(f"solver speed: {(time.time() - t_first) / (tl - tl_first):.1f} s wall per simulated s (from the first sample, build excluded)")
    L(f"run done: {a.dur} s simulated in {time.time() - t0:.0f} s wall ({(time.time() - t0) / a.dur:.1f} s per simulated s)")
finally:
    stage("quit", 120); pscad.quit(); stage(None)
for f in glob.glob(os.path.join(BUILD, "v2_*.out")) + glob.glob(os.path.join(BUILD, "v2.infx")) + glob.glob(os.path.join(BUILD, "*.snp")):
    dst = os.path.join(OUTD, os.path.basename(f))
    if os.path.exists(dst): os.remove(dst)                            # rerun of the same tag
    (shutil.move if f.endswith(".out") else shutil.copy)(f, OUTD)   # S30: no duplicate .out (disk full 2026-11-26)
L("outputs copied to", OUTD)
