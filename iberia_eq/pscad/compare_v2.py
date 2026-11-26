r"""Overlay several v2 runs (S30 sec 18): PMU voltage of chosen buses and the machine-frequency band.

usage: python iberia_eq\pscad\compare_v2.py <out_name> <tag1> <tag2> ... [--buses BAD_TS CAT] [--cycles 3] [--t 5 20]
Writes iberia_eq\pscad\figs\cmp_<out_name>.png. One colour per run; the frequency panel shows min..max of all machines.
"""
import argparse, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from legacy_out import load
from pmu import pmu
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("name"); ap.add_argument("tags", nargs="+")
ap.add_argument("--buses", nargs="+", default=["BAD_TS", "CAT"]); ap.add_argument("--cycles", type=int, default=3)
ap.add_argument("--t", nargs=2, type=float, default=(5.0, 20.0)); a = ap.parse_args()
cols = plt.get_cmap("tab10")
fig, ax = plt.subplots(len(a.buses) + 1, 1, figsize=(11, 3.2 * (len(a.buses) + 1)), sharex=True)
for j, tag in enumerate(a.tags):
    t, c = load(os.path.join(r"C:\PSCAD_work\v2_runs", tag), "v2"); m = (t >= a.t[0]) & (t <= a.t[1])
    for i, b in enumerate(a.buses):
        r = pmu(t, *(c[f"V_{b}[{k}]"] for k in (1, 2, 3)), cycles=a.cycles); w = (r["t"] >= a.t[0]) & (r["t"] <= a.t[1])
        ax[i].plot(r["t"][w], r["V"][w], color=cols(j), lw=1.0, label=f"{tag}  (std {r['V'][w].std():.2f} kV)")
    F = np.array([c[k] for k in c if k.endswith(":Wspd") and k.startswith("SyncUnit(")]) / (2 * np.pi)
    ax[-1].fill_between(t[m], F[:, m].min(axis=0), F[:, m].max(axis=0), color=cols(j), alpha=0.35, label=tag)
for i, b in enumerate(a.buses):
    ax[i].set_ylabel(f"{b.replace('_', '-')} |V| [kV]\n(PMU {a.cycles}-cycle)"); ax[i].legend(fontsize=8); ax[i].grid(alpha=0.3)
ax[-1].set_ylabel("machine f [Hz]\n(min..max)"); ax[-1].set_xlabel("t [s]"); ax[-1].legend(fontsize=8); ax[-1].grid(alpha=0.3)
ax[0].set_title(f"compare: {', '.join(a.tags)}")
fig.tight_layout(); out = os.path.join(HERE, "figs", f"cmp_{a.name}.png"); fig.savefig(out, dpi=100); print(out)
