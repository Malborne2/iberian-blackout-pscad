r"""Measure the simulation speed of running cases from their growing .out files, then stop them (S30 sec 23).

usage: python iberia_eq\pscad\rate_probe.py smk_a smk_b ... [--dt 20] [--n 3] [--kill]
Every --dt s it reads the last simulated time of C:\PSCAD_work\<case>\v2.gf81_x86\v2_01.out and prints the speed as wall s per
simulated s over the last interval. A case is done after --n consecutive readings within 10 % of each other; with --kill
its run_v2 / PSCAD / solver processes are then stopped (smoke tests only). Ends when all cases are done.
"""
import argparse, os, subprocess, time

ap = argparse.ArgumentParser(); ap.add_argument("cases", nargs="+"); ap.add_argument("--dt", type=float, default=20)
ap.add_argument("--n", type=int, default=3); ap.add_argument("--kill", action="store_true"); a = ap.parse_args()
def last_t(c):
    f = os.path.join(r"C:\PSCAD_work", c, "v2.gf81_x86", "v2_01.out")
    try:
        with open(f, "rb") as fh:
            fh.seek(0, 2); n = fh.tell(); fh.seek(max(0, n - 3000)); return float(fh.read().decode(errors="replace").strip().split("\n")[-2].split()[0])
    except Exception: return None
def kill(c):
    ps = ("$p=Get-CimInstance Win32_Process; $py=$p|?{ $_.Name -eq 'python.exe' -and $_.CommandLine -like '*run_v2.py " + c + " *' }; "
          "foreach($x in $py){ $k=$p|?{$_.ParentProcessId -eq $x.ProcessId -and $_.Name -eq 'Pscad.exe'}; foreach($q in $k){ "
          "$p|?{$_.ParentProcessId -eq $q.ProcessId}|%{ $p|?{$_.ParentProcessId -eq $_.ProcessId}|%{Stop-Process -Id $_.ProcessId -Force -EA 0}; "
          "Stop-Process -Id $_.ProcessId -Force -EA 0 }; Stop-Process -Id $q.ProcessId -Force -EA 0 }; Stop-Process -Id $x.ProcessId -Force -EA 0 }")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True)
    lk = os.path.join(r"C:\PSCAD_work", c, "run_v2.lock")
    if os.path.exists(lk): os.remove(lk)
prev = {c: (None, None) for c in a.cases}; hist = {c: [] for c in a.cases}; done = {}
while len(done) < len(a.cases):
    time.sleep(a.dt); now = time.time()
    for c in a.cases:
        if c in done: continue
        t = last_t(c); t0, w0 = prev[c]
        if t is not None and t0 is not None and t > t0:
            r = (now - w0) / (t - t0); hist[c].append(r)
            h = hist[c][-a.n:]
            if len(h) == a.n and max(h) / min(h) < 1.10:
                done[c] = sum(h) / len(h); print(f"{c}: {done[c]:.0f} s wall per simulated s (readings {', '.join(f'{x:.0f}' for x in h)})", flush=True)
                if a.kill: kill(c)
        prev[c] = (t, now) if t is not None else (None, None)
print("RESULT " + "  ".join(f"{c}={v:.0f}" for c, v in done.items()))
