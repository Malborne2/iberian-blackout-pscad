r"""Replay figure of a v2 replay run against the report targets (S30 sec 19). Report clock: t0 = 30 s = 12:32:00.

usage: python iberia_eq\pscad\replay_fig.py <tag> [<tag2> ...] [--t0 30]
Writes iberia_eq\pscad\figs\replay_<tag>[_vs_...].png with panels:
  1 France tie: AC (multimeter PFR, + = export) and total = AC + 1,000 MW HVDC x MHV; [CA] p.104 targets
    (≈1,500 MW total at 12:32:00, ≈450 just before event 3, ≈0 after it) and the 12:33:19.62 AC import peak 4,609 MW;
  2 400 kV max / mean bus voltage (PMU, 3-cycle) with Fig 3-7a points (421.8 -> 427.8 kV between events 3 and 4a;
    432.7 / 435.6 / 441.6 kV at 76.9 / 77.6 / 78.4 s) and the event-3 Granada trip time;
  3 machine frequency min..max with the defence-plan thresholds;
  4 control signals: RES driver factors, load factors M_ES/M_PT, pump / Morocco breakers.
"""
import argparse, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from legacy_out import load
from pmu import pmu
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("tags", nargs="+"); ap.add_argument("--t0", type=float, default=30.0); a = ap.parse_args()
cols = plt.get_cmap("tab10")
fig, ax = plt.subplots(4, 1, figsize=(12, 14), sharex=True)
for j, tag in enumerate(a.tags):
    t, c = load(os.path.join(r"C:\PSCAD_work\v2_runs", tag), "v2"); tr = t - a.t0; col = cols(j)
    def g(n): return next((c[k] for k in c if k == n or k.endswith(":" + n)), None)
    pfr, mhv = g("PFR"), g("MHV")
    if pfr is not None:
        ax[0].plot(tr, pfr, color=col, lw=0.6, alpha=0.5, label=f"{tag}: AC tie")
        if mhv is not None:
            n = 1000; tot = np.convolve(pfr + 1000.0 * mhv, np.ones(n) / n, mode="same")
            ax[0].plot(tr, tot, color=col, lw=1.6, label=f"{tag}: AC + HVDC (0.2 s mean)")
    V = []
    for k in c:
        if k.startswith("V_") and k.endswith("[1]"):
            b = k[2:-3]; r = pmu(t, c[f"V_{b}[1]"], c[f"V_{b}[2]"], c[f"V_{b}[3]"], cycles=3); V.append(np.interp(t, r["t"], r["V"]))
    V = np.array(V); ax[1].plot(tr, V.max(axis=0), color=col, lw=1.2, label=f"{tag}: max of 24 buses")
    ax[1].plot(tr, V.mean(axis=0), color=col, lw=0.9, ls="--", label=f"{tag}: mean")
    F = np.array([c[k] for k in c if k.endswith(":Wspd") and k.startswith("SyncUnit(")]) / (2 * np.pi)
    ax[2].fill_between(tr, F.min(axis=0), F.max(axis=0), color=col, alpha=0.4, label=f"{tag}: machines min..max")
    for n_, ls in (("RF_N", "-"), ("RF_S", "--"), ("M_ES", ":"), ("M_PT", "-.")):
        v = g(n_)
        if v is not None: ax[3].plot(tr, v, color=col, ls=ls, lw=1.1, label=f"{tag}: {n_}")
    for n_, mk in (("BRKM1", 0.0), ("BRKM3", 0.02), ("BRKMA", 0.04)):
        v = g(n_)
        if v is not None and v.max() > 0.5: ax[3].plot(tr, v * 0.3 + 0.6 + mk, color=col, lw=1.0, label=f"{tag}: {n_} (open = up)")
ax[0].plot([0, 56.5, 58], [1500, 450, 0], "k*", ms=10, label="[CA] p.104 total export")
ax[0].plot([79.62], [-4609], "kv", ms=9, label="[CA] AC import peak 12:33:19.62")
ax[0].set_ylabel("France tie [MW]\n+ export"); ax[0].legend(fontsize=7, ncol=2)
ax[1].plot([57.2, 76.0, 76.9, 77.6, 78.4], [421.8, 427.8, 432.7, 435.6, 441.6], "k*", ms=10, label="Fig 3-7a 400 kV max")
ax[1].set_ylabel("400 kV bus |V| [kV]\n(PMU 3-cycle)"); ax[1].legend(fontsize=7, ncol=2); ax[1].set_ylim(380, 470)
for f_ in (49.8, 49.5, 49.3, 49.0, 48.0): ax[2].axhline(f_, color="gray", lw=0.5, ls=":")
ax[2].set_ylabel("frequency [Hz]"); ax[2].legend(fontsize=7)
ax[3].set_ylabel("control signals"); ax[3].legend(fontsize=7, ncol=3); ax[3].set_xlabel("report time [s after 12:32:00]  (t0 = %g s model time)" % a.t0)
for a_ in ax:
    a_.grid(alpha=0.3); a_.axvline(57.22, color="red", lw=0.6, ls="--")
ax[0].text(57.5, ax[0].get_ylim()[1] * 0.9, "event 3 Granada 12:32:57.22", color="red", fontsize=7)
ax[0].set_title("v2 replay: " + ", ".join(a.tags))
fig.tight_layout(); out = os.path.join(HERE, "figs", "replay_" + "_vs_".join(a.tags) + ".png"); fig.savefig(out, dpi=100); print(out)
