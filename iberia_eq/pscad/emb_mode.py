r"""Relative-speed mode of the machines (S30 sec 20/24): which unit drifts from the fleet and does its swing grow?

usage: python iberia_eq\pscad\emb_mode.py <tag> [<tag2> ...] [--t0 30] [--win 10]
For each run: every SyncUnit speed (Wspd [rad/s] -> Hz) minus the mean of all units; the unit with the largest
peak-to-peak in the last window is reported with its p-p per window, dominant frequency (FFT of the last 30 s) and
mean POUT / QOUT. Writes iberia_eq\pscad\figs\emb_mode.png (relative speed of the worst unit of each run, and p-p per
window). Instances are numbered per build: compare units by their POUT, not the number.
"""
import argparse, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from legacy_out import load
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

ap = argparse.ArgumentParser(); ap.add_argument("tags", nargs="+"); ap.add_argument("--t0", type=float, default=30.0)
ap.add_argument("--win", type=float, default=10.0)
ap.add_argument("--pout", type=float)   # follow the unit whose mean POUT [pu] is closest to this (e.g. E3 CAT 0.904)
a = ap.parse_args()
fig, ax = plt.subplots(2, 1, figsize=(10, 7))
for tag in a.tags:
    t, d = load(os.path.join(r"C:\PSCAD_work\v2_runs", tag), "v2")
    ws = {re.search(r"SyncUnit\((\d+)\)", n).group(1): n for n in d if "SyncUnit(" in n and n.endswith(":Wspd")}
    def ch(k, q): return d[ws[k].replace(":Wspd", ":" + q)] if ws[k].replace(":Wspd", ":" + q) in d else None
    m = t >= a.t0; tt = t[m]
    W = np.array([d[ws[k]][m] for k in ws]) / (2 * np.pi); rel = W - W.mean(axis=0); keys = list(ws)
    edges = np.arange(tt[0], tt[-1] + 1e-9, a.win)
    pp = np.array([[np.ptp(r[(tt >= e0) & (tt < e0 + a.win)]) if ((tt >= e0) & (tt < e0 + a.win)).sum() > 10 else np.nan
                    for e0 in edges[:-1]] for r in rel])
    k = int(np.nanargmax(pp[:, -1]))
    if a.pout is not None: k = int(np.argmin([abs(ch(q, "POUT")[m].mean() - a.pout) for q in keys]))
    r = rel[k]; u = keys[k]
    seg = (tt >= tt[-1] - 30); x = r[seg] - r[seg].mean(); dt = np.median(np.diff(tt))
    F = np.fft.rfftfreq(len(x), dt); S = np.abs(np.fft.rfft(x * np.hanning(len(x)))); band = (F > 0.03) & (F < 5)
    fdom = F[band][np.argmax(S[band])]
    po, qo = ch(u, "POUT"), ch(u, "QOUT")
    print(f"{tag}: unit SyncUnit({u})  POUT {po[m].mean():.3f} pu  QOUT {qo[m].mean():+.3f} pu  "
          f"p-p per {a.win:g} s [mHz]: {' '.join(f'{v * 1000:.0f}' for v in pp[k])}  f_dom {fdom:.3f} Hz  "
          f"fleet max p-p last window {np.nanmax(pp[:, -1]) * 1000:.0f} mHz")
    ax[0].plot(tt, r * 1000, lw=.8, label=f"{tag}: SyncUnit({u})")
    ax[1].plot(edges[:-1] + a.win / 2, pp[k] * 1000, "o-", label=tag)
ax[0].set_ylabel("speed - fleet mean [mHz]"); ax[0].set_xlabel("t [s]"); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
ax[1].set_ylabel(f"p-p per {a.win:g} s window [mHz]"); ax[1].set_xlabel("window centre [s]"); ax[1].legend(fontsize=8); ax[1].grid(alpha=.3)
ax[0].set_title("Worst machine's speed relative to the fleet (growing = unstable relative mode)", fontsize=10)
fig.tight_layout(); out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs", "emb_mode.png"); fig.savefig(out, dpi=110); print(out)
