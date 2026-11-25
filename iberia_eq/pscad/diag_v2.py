r"""Diagnose a v2 run in time steps (S30 sec 9): RES plants (trip, Id/Iq, V), SyncUnit Q/Vt/Ef, bus voltages.

usage: python iberia_eq\pscad\diag_v2.py <tag> [--step 0.25] [--t1 6]
"""
import argparse, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from legacy_out import load

ap = argparse.ArgumentParser(); ap.add_argument("tag"); ap.add_argument("--step", type=float, default=0.25); ap.add_argument("--t1", type=float, default=6.0)
a = ap.parse_args()
t, c = load(os.path.join(r"C:\PSCAD_work\v2_runs", a.tag), "v2")
res = sorted({k.split(":")[0] for k in c if k.startswith("RES_Plant(")}, key=lambda s: int(re.search(r"\d+", s).group()))
syn = sorted({k.split(":")[0] for k in c if k.startswith("SyncUnit(")}, key=lambda s: int(re.search(r"\d+", s).group()))
print("SyncUnit channels:", sorted({k.split(":")[1] for k in c if k.startswith("SyncUnit(0)")}))
print("RES channels:", sorted({k.split(":")[1] for k in c if k.startswith("RES_Plant(0)")}))
def at(k, j): return c[k][j] if k in c else np.nan
print("   t   RES trip#  RES Vpu min/max   RES Id min/max   RES Iq min/max |  Sync Q pu min/max   Sync Vt min/max")
for t_ in np.arange(0.0, min(a.t1, t[-1]) + 1e-9, a.step):
    j = min(len(t) - 1, np.searchsorted(t, t_))
    tr = sum(at(f"{r}:TRIP", j) > 0.5 for r in res)
    va = np.array([at(f"{r}:VA_PU", j) for r in res]); idd = np.array([at(f"{r}:ID", j) for r in res]); iq = np.array([at(f"{r}:IQ", j) for r in res])
    q = np.array([at(f"{s}:QOUT", j) for s in syn]); vt = np.array([at(f"{s}:VIT[1]", j) if f"{s}:VIT[1]" in c else at(f"{s}:VIT", j) for s in syn])
    print(f"  {t_:4.2f}  {tr:3d}      {np.nanmin(va):5.2f} {np.nanmax(va):5.2f}     {np.nanmin(idd):6.2f} {np.nanmax(idd):6.2f}    "
          f"{np.nanmin(iq):6.2f} {np.nanmax(iq):6.2f}   | {np.nanmin(q):6.2f} {np.nanmax(q):6.2f}      {np.nanmin(vt):5.2f} {np.nanmax(vt):5.2f}")
