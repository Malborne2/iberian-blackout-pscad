r"""Exit as soon as any PSCAD run needs attention (S30 sec 23, owner: be told of problems at once, without polling).

usage: python iberia_eq\pscad\run_watch.py [--dt 20] [--stall 300] [--build-min 12] [--done]
Watches every run the dashboard knows (run_dashboard.runs) and exits with one line per event when a run
  - failed (BUILD ERRORS / RUN FAILED / traceback, incl. run_v2's stage watchdog), or was stopped (process gone),
  - shows no new sample for --stall s while its process lives,
  - is still building / starting --build-min min after its start (solver not started),
  - finished (only with --done; default: also reported, since a finished test needs reading).
Run it in the background; its exit is the notification. Events already present at start are listed once and ignored.
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_dashboard as D

ap = argparse.ArgumentParser(); ap.add_argument("--dt", type=float, default=20); ap.add_argument("--stall", type=float, default=300)
ap.add_argument("--build-min", type=float, default=12); a = ap.parse_args()

def events():
    ev = {}; now = time.time()
    for r in D.runs(filtered=False):
        k = (r["tag"], r.get("t0"))
        if r["state"] in ("failed", "stopped"): ev[k] = f"{r['tag']}: {r['state'].upper()} {r.get('why') or ''}".strip()
        elif r["state"] == "done": ev[k] = f"{r['tag']}: DONE ({r['wall']:.0f} s wall)"
        elif r["state"] in ("running", "stalled?") and r["age"] is not None and r["age"] > a.stall:
            ev[k] = f"{r['tag']}: STALLED no sample for {r['age']:.0f} s at t = {r['t']}"
        elif r["state"] == "building" and r.get("t0") and now - r["t0"] > 60 * a.build_min:
            ev[k] = f"{r['tag']}: NOT STARTED {(now - r['t0']) / 60:.0f} min after launch"
    return ev

seen = events()
print("watching; already present:", "; ".join(seen.values()) or "none", flush=True)
while True:
    time.sleep(a.dt)
    new = {k: v for k, v in events().items() if k not in seen}
    if new:
        live = [f"{r['tag']} t={r['t']}" for r in D.runs() if r["state"] == "running"]
        print("EVENT", " | ".join(new.values()), flush=True); print("live:", ", ".join(live) or "none"); break
