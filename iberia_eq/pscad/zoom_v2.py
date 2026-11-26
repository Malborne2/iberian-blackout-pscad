r"""Zoom on bus voltages of a v2 run (S30 sec 16): PMU |V| of chosen buses over a short window, plus its spectrum.

usage: python iberia_eq\pscad\zoom_v2.py <tag> [--buses BAD_TS PT_S WAN SE CAT] [--win 20 21] [--spec 10 26]
Writes iberia_eq\pscad\figs\zoom_<tag>.png.
"""
import argparse, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from legacy_out import load
from pmu import pmu
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("tag"); ap.add_argument("--buses", nargs="+", default=["BAD_TS", "PT_S", "WAN", "SE", "CAT", "NW"])
ap.add_argument("--win", nargs=2, type=float, default=(20.0, 21.0)); ap.add_argument("--spec", nargs=2, type=float, default=(10.0, 26.0))
a = ap.parse_args()
t, c = load(os.path.join(r"C:\PSCAD_work\v2_runs", a.tag), "v2")
fig, ax = plt.subplots(2, 1, figsize=(11, 8))
for b in a.buses:
    if f"V_{b}[1]" not in c: continue
    r = pmu(t, *(c[f"V_{b}[{j}]"] for j in (1, 2, 3)))
    w = (r["t"] >= a.win[0]) & (r["t"] <= a.win[1]); ax[0].plot(r["t"][w], r["V"][w], lw=1.2, label=b.replace("_", "-"))
    s = (r["t"] >= a.spec[0]) & (r["t"] <= a.spec[1]); v = r["V"][s] - r["V"][s].mean()
    sp = np.abs(np.fft.rfft(v * np.hanning(len(v)))) * 4 / len(v); fr = np.fft.rfftfreq(len(v), r["t"][1] - r["t"][0])
    ax[1].plot(fr, sp, lw=1.0, label=b.replace("_", "-"))
ax[0].set_xlabel("t [s]"); ax[0].set_ylabel("bus |V| LL [kV] (PMU, 50 frames/s)"); ax[0].legend(ncol=6, fontsize=8); ax[0].grid(alpha=0.3)
ax[0].set_title(f"{a.tag}: zoom {a.win[0]:g}-{a.win[1]:g} s")
ax[1].set_xlabel("frequency [Hz]"); ax[1].set_ylabel(f"|V| amplitude [kV] ({a.spec[0]:g}-{a.spec[1]:g} s)"); ax[1].set_xlim(0, 25)
ax[1].legend(ncol=6, fontsize=8); ax[1].grid(alpha=0.3)
fig.tight_layout(); out = os.path.join(HERE, "figs", f"zoom_{a.tag}.png"); fig.savefig(out, dpi=100); print(out)
