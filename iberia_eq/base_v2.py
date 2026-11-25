"""Run pp_v2.py in the adopted base configuration: R2 (RUNLOG S28 sec 13) + OPEN_LINES + PUMP_PT_V + EMB_KPF + UNITQ_HV (S29 sec 2-6).

usage:
  python iberia_eq/base_v2.py                      # resume from the base state, ~10 s
  python iberia_eq/base_v2.py --cold --state X.pkl # full cold fit, saved to X.pkl (never overwrites the base state)
  python iberia_eq/base_v2.py --env OPEN_LINES=1 --cold --state s29_open.pkl   # base + extra flags

Works the same on Windows and macOS (no shell syntax). The base configuration lives here and nowhere else, so
pp_v2.py's own defaults (the S27 behaviour) stay reproducible. Any change to the base is logged in RUNLOG.
"""
import argparse, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_STATE = "pp_v2_state_s29_EU.pkl"      # R2 alone: pp_v2_state_s28_R2.pkl with the two S29 flags off
BASE_ENV = {"FAST": "1", "OBJ": "2", "TRIPCAL": "1", "PT_TIE_SW": "2.6", "CORR": "v2", "CHG": "phys", "SH_ARA_NW": "0",
            "OPEN_LINES": "1", "PUMP_PT_V": "1", "EMB_KPF": "fig42", "UNITQ_HV": "1"}
BASE_ARGS = ["--frsc", "1500", "--kres", "0.2", "--route", "1.0", "--flowcal", "--mincirc", "2", "--vkg", "5"]

ap = argparse.ArgumentParser()
ap.add_argument("--cold", action="store_true", help="full continuation from scratch instead of a resume")
ap.add_argument("--state", default=None, help="state file to write (default: a scratch copy of the base state)")
ap.add_argument("--env", nargs="*", default=[], help="extra KEY=VALUE flags on top of the base")
ap.add_argument("--log", default=None, help="write stdout+stderr to this file as well")
a, extra = ap.parse_known_args()

env = {**os.environ, **BASE_ENV, **dict(kv.split("=", 1) for kv in a.env)}   # later entries override (base flags can be switched off)
if a.cold:
    env.pop("RESUME", None)
    env["STATE"] = a.state or "pp_v2_state_cold.pkl"
else:
    # resume: work on a copy so the committed base state is never modified by the run
    work = a.state or "pp_v2_state_base_work.pkl"
    if not os.path.exists(os.path.join(HERE, work)):
        shutil.copy(os.path.join(HERE, BASE_STATE), os.path.join(HERE, work))
    env["STATE"] = work; env["RESUME"] = "1"
cmd = [sys.executable, os.path.join(HERE, "pp_v2.py")] + BASE_ARGS + extra
print("env:", " ".join(f"{k}={env[k]}" for k in sorted(set(BASE_ENV) | {kv.split('=')[0] for kv in a.env} | {"STATE"} | ({"RESUME"} if "RESUME" in env else set()))))
print("cmd:", " ".join(cmd), flush=True)
p = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
out = p.stdout + p.stderr
if a.log: open(a.log, "w", encoding="utf-8").write(out)
sys.stdout.write(out); sys.exit(p.returncode)
