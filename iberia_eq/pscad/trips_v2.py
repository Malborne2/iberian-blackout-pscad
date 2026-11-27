r"""List the RES plant trips of a v2 replay run (S30 sec 24): first time each T_<plant> channel goes to 1.

usage: python iberia_eq\pscad\trips_v2.py <tag> [--t0 30] [--tw 5]
Prints model time and the report time (inverse of the replay time map: r = (t - t0) * tw before 12:33:16, then 1:1),
plus the PMU voltage of the plant's zone bus at the trip (V_<bus> channel, kV, 1-cycle).
"""
import argparse, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from legacy_out import load

ap = argparse.ArgumentParser(); ap.add_argument("tag"); ap.add_argument("--t0", type=float, default=30.0); ap.add_argument("--tw", type=float, default=5.0)
a = ap.parse_args()
t, d = load(os.path.join(r"C:\PSCAD_work\v2_runs", a.tag), "v2")
TC = 76.0; tc = a.t0 + TC / a.tw
def RT(x): return (x - a.t0) * a.tw if x < tc else TC + (x - tc)
T = {n.split(":")[-1]: d[n] for n in d if re.search(r"(^|:)T_", n)}
print(f"{a.tag}: {len(T)} trip channels; time map t0 {a.t0} s, tw {a.tw}")
for k in sorted(T, key=lambda k: (np.argmax(T[k] > 0.5) if (T[k] > 0.5).any() else 1e12)):
    on = T[k] > 0.5
    if on.any():
        i = int(np.argmax(on)); print(f"  {k:22s} trips at t = {t[i]:8.3f} s  (report {RT(t[i]):7.2f} s after 12:32:00)")
    else: print(f"  {k:22s} no trip")
