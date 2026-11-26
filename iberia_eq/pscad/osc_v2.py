r"""Bus-voltage oscillation table of v2 runs (S30 sec 15): PMU voltage peak-to-peak and dominant frequency per bus.

usage: python iberia_eq\pscad\osc_v2.py <tag> [<tag2> ...] [--win 4 6]
PMU measurement as pmu.py (one-cycle DFT positive sequence, 50 frames/s). Dominant frequency = largest FFT peak of
the de-meaned PMU magnitude between 0.2 and 24 Hz. One column pair per run.
"""
import argparse, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from legacy_out import load
from pmu import pmu

ap = argparse.ArgumentParser(); ap.add_argument("tags", nargs="+"); ap.add_argument("--win", nargs=2, type=float, default=(4.0, 6.0))
a = ap.parse_args()
res = {}
for tag in a.tags:
    t, c = load(os.path.join(r"C:\PSCAD_work\v2_runs", tag), "v2"); res[tag] = {}
    for k in c:
        m = re.match(r"V_(.+)\[1\]$", k)
        if not m: continue
        b = m.group(1); r = pmu(t, *(c[f"V_{b}[{j}]"] for j in (1, 2, 3)))
        w = (r["t"] >= a.win[0]) & (r["t"] <= a.win[1]); v = r["V"][w]
        if len(v) < 10: continue
        sp = np.abs(np.fft.rfft(v - v.mean())); fr = np.fft.rfftfreq(len(v), r["t"][1] - r["t"][0])
        band = (fr > 0.2) & (fr < 24); fd = fr[band][np.argmax(sp[band])] if band.any() else np.nan
        res[tag][b] = (v.mean(), np.ptp(v), fd)
buses = sorted({b for d in res.values() for b in d}, key=lambda b: -max(res[t_].get(b, (0, 0, 0))[1] for t_ in res))
print(f"window {a.win[0]}-{a.win[1]} s; PMU |V| mean / peak-to-peak [kV] @ dominant Hz")
print("bus          " + "".join(f"{t_:>28s}" for t_ in a.tags))
for b in buses:
    print(f"{b:12s} " + "".join("{:>28s}".format(f"{res[t_][b][0]:6.1f} / {res[t_][b][1]:5.1f} @ {res[t_][b][2]:4.1f}" if b in res[t_] else "-") for t_ in a.tags))
