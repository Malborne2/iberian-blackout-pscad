r"""Check the France-tie P/Q from the breaker (BRKFR BP/BQ, S30 sec 23 default) against the old series multimeter.

usage: python iberia_eq\pscad\chk_frpq.py <tag_meter> <tag_breaker>
Reads PFR/QFR of both runs (C:\PSCAD_work\v2_runs\<tag>), prints mean / max difference after the first 0.05 s and writes
iberia_eq\pscad\figs\chk_frpq.png. Pass: same sign and the 20 ms means within 1 %.
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from legacy_out import load
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

tm, tb = sys.argv[1:3]; R = r"C:\PSCAD_work\v2_runs"
def get(tag):
    t, d = load(os.path.join(R, tag), "v2")
    k = {n.split(":")[-1].split("\\")[-1].upper(): n for n in d}
    return t, d[k["PFR"]], d[k["QFR"]]
fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
res = {}
for tag, lab in ((tm, "multimeter (old)"), (tb, "breaker BP/BQ (new)")):
    t, p, q = get(tag); m = t > 0.05
    w = max(1, int(round(0.02 / np.median(np.diff(t)))))
    pm = np.convolve(p, np.ones(w) / w, "valid"); qm = np.convolve(q, np.ones(w) / w, "valid"); tt = t[w - 1:]
    res[lab] = (tt, pm, qm)
    ax[0].plot(tt, pm, label=lab); ax[1].plot(tt, qm, label=lab)
    print(f"{lab:22s} P mean {p[m].mean():8.1f}  Q mean {q[m].mean():8.1f}  (t > 0.05 s)")
(t1, p1, q1), (t2, p2, q2) = res.values(); n = min(len(p1), len(p2)); s = t1[:n] > 0.05
print(f"20 ms means: max |dP| {np.abs(p1[:n] - p2[:n])[s].max():.1f}, max |dQ| {np.abs(q1[:n] - q2[:n])[s].max():.1f}")
ax[0].set_ylabel("P France tie (+ = export)"); ax[1].set_ylabel("Q France tie"); ax[1].set_xlabel("t [s]")
for x in ax: x.grid(alpha=.3); x.legend()
fig.suptitle("France tie P/Q: series multimeter vs breaker BP/BQ (20 ms mean)"); fig.tight_layout()
os.makedirs(os.path.join(os.path.dirname(__file__), "figs"), exist_ok=True)
fig.savefig(os.path.join(os.path.dirname(__file__), "figs", "chk_frpq.png"), dpi=110); print("figs/chk_frpq.png")
