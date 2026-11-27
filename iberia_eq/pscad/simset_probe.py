r"""Probe (S30 sec 23, optimisation only): can ONE PSCAD instance run several EMTDC solvers in parallel (simulation set)?

usage: python iberia_eq\pscad\simset_probe.py --src C:\PSCAD_work\lt8_R\lt8.pscx --name lt8 --n 4 --dur 30
Copies the project N times as <name>a, <name>b, ... (prefix rename, skill P13) into C:\PSCAD_work\simset\, loads all into one
visible PSCAD, puts them in one simulation set, runs it, and every 5 s prints how many solver processes are alive and the
CPU use of PSCAD and of each solver. Stops after --watch seconds. Results only matter for the run strategy.
"""
import argparse, os, shutil, subprocess, time
import mhi.pscad

ap = argparse.ArgumentParser(); ap.add_argument("--src", required=True); ap.add_argument("--name", required=True)
ap.add_argument("--n", type=int, default=4); ap.add_argument("--dur", default="30"); ap.add_argument("--watch", type=int, default=60)
a = ap.parse_args()
W = r"C:\PSCAD_work\simset"; shutil.rmtree(W, ignore_errors=True); os.makedirs(W)
txt = open(a.src, encoding="utf-8").read(); names = []
for k in range(a.n):
    nm = f"{a.name}{chr(97 + k)}"; names.append(nm); d = os.path.join(W, nm); os.makedirs(d)
    open(os.path.join(d, nm + ".pscx"), "w", encoding="utf-8").write(txt.replace(f"{a.name}:", f"{nm}:").replace(f'name="{a.name}"', f'name="{nm}"'))
    os.environ["PATH"] = os.path.join(d, nm + ".gf81_x86") + os.pathsep + os.environ["PATH"]
def ps(cmd): return subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True).stdout
pscad = mhi.pscad.launch(minimize=False, splash=False, timeout=60)
try:
    if not pscad.licensed():
        c = pscad.get_available_certificates(); c = next(iter(c.values())) if isinstance(c, dict) else c[0]; pscad.get_certificate(c)
    for nm in names:
        pscad.load(os.path.join(W, nm, nm + ".pscx")); p = pscad.project(nm)
        p.parameters(time_duration=a.dur, time_step="20", sample_step="1000", PlotType="1", StartType="0", SnapType="0")
    for nm in names: pscad.project(nm).build()
    ss = pscad.create_simulation_set("probe"); ss.add_tasks(*names)
    try: print("volley", ss.volley())
    except Exception as e: print("volley n/a", e)
    t0 = time.time(); pscad.run_simulation_sets(ss)
    me = os.getpid(); print("probe PSCAD pid:", ps("(Get-CimInstance Win32_Process | ? { $_.ParentProcessId -eq " + str(me) + " -and $_.Name -eq 'Pscad.exe' }).ProcessId").strip(), flush=True)
    while time.time() - t0 < a.watch:
        time.sleep(5)
        pat = ",".join([n + "*" for n in names] + ["Pscad"])
        out = ps(f"$a=Get-Process {pat} -EA SilentlyContinue|Select Id,ProcessName,CPU; Start-Sleep 3; "
                 f"$b=Get-Process {pat} -EA SilentlyContinue|Select Id,ProcessName,CPU; foreach($x in $b){{$y=$a|?{{$_.Id -eq $x.Id}}; "
                 "if($y){{'{{0}}:{{1}}:{{2:N0}}' -f $x.ProcessName,$x.Id,(($x.CPU-$y.CPU)/3*100)}}}}")
        solvers = [l for l in out.split() if l.split(":")[0].lower() in [n.lower() for n in names]]
        print(f"[{time.time() - t0:4.0f} s] solvers alive {len(solvers)}: {solvers}  all: {out.split()}", flush=True)
    msgs = [f"{getattr(m, 'status', '')}:{getattr(m, 'text', m)}" for nm in names for m in pscad.project(nm).messages()
            if str(getattr(m, "status", "")).lower() in ("error", "warning") and "licen" in str(getattr(m, "text", m)).lower()]
    print("licence messages:", msgs[:10])
finally:
    pscad.quit()
