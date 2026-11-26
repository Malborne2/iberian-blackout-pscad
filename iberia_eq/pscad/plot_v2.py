r"""Readable figures of a v2 run (S30 sec 13): smoothed bus voltages, machine frequency, unit P against the load flow.

usage: python iberia_eq\pscad\plot_v2.py <tag> [--ref <tag2>] [--build build_v2.out] [--t1 8]
Writes iberia_eq\pscad\figs\plot_<tag>.png (and plot_<tag>_vs_<tag2>.png with --ref: mean bus V and frequency band of
both runs on the same axes). Bus V is measured like a PMU (pmu.py: one-cycle DFT positive-sequence
phasor, 50 frames/s), which rejects the converter switching ripple as the report's PMU/SCADA data do. Units are matched to the build-log unit list as in read_v2.py, over the last 1 s.
"""
import argparse, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from legacy_out import load
from pmu import pmu
from scipy.optimize import linear_sum_assignment
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("tag"); ap.add_argument("--ref"); ap.add_argument("--build", default="build_v2.out")
ap.add_argument("--t1", type=float); a = ap.parse_args()

def run(tag):
    t, c = load(os.path.join(r"C:\PSCAD_work\v2_runs", tag), "v2")
    n = max(1, int(round(0.02 / (t[1] - t[0])))); k = np.ones(n) / n
    sm = lambda x: np.convolve(np.pad(x, (n // 2, n - 1 - n // 2), mode="edge"), k, mode="valid")
    vb = {}
    for key in c:
        m = re.match(r"V_(.+)\[1\]$", key)
        if m:                                   # PMU-style 1-cycle DFT positive-sequence magnitude (pmu.py), S30 sec 13
            b = m.group(1); r = pmu(t, *(c[f"V_{b}[{j}]"] for j in (1, 2, 3))); vb[b] = np.interp(t, r["t"], r["V"])
    inst = sorted({key.split(":")[0] for key in c if key.startswith("SyncUnit(")}, key=lambda s: int(re.search(r"\d+", s).group()))
    f = {i: c[f"{i}:Wspd"] / (2 * np.pi) for i in inst}
    return t, c, vb, inst, f, sm

units = []
for ln in open(os.path.join(HERE, a.build), encoding="utf-8", errors="replace"):
    m = re.match(r"unit (.+?)\s+at (\S+(?: term)?)\s+P\s+(-?[\d.]+) Q\s+([-+\d.]+) S\s+([\d.]+) V ([\d.]+)", ln.strip())
    if m: units.append(dict(name=m.group(1).strip(), P=float(m.group(3)), S=float(m.group(5)), V=float(m.group(6))))
t, c, vb, inst, f, sm = run(a.tag); t1 = a.t1 or t[-1]; m1 = (t > t1 - 1.0) & (t <= t1)
C = np.array([[abs(c[f"{i}:POUT"][m1].mean() - u["P"] / u["S"]) / 0.05 + abs(c[f"{i}:VIT[1]"][m1].mean() - u["V"]) / 0.01 for u in units] for i in inst])
r_, c_ = linear_sum_assignment(C); U = {inst[i]: units[j] for i, j in zip(r_, c_)}
cm = plt.get_cmap("tab20")
fig, ax = plt.subplots(3, 1, figsize=(11, 11), sharex=True)
for j, b in enumerate(sorted(vb)): ax[0].plot(t, vb[b], lw=0.9, color=cm(j % 20), label=b.replace("_", "-"))
ax[0].set_ylabel("bus voltage, line-to-line [kV]\n(20 ms mean)"); ax[0].set_ylim(300, 460)
ax[0].legend(ncol=6, fontsize=7, loc="lower right")
for j, i in enumerate(inst): ax[1].plot(t, f[i], lw=0.9, color=cm(j % 20), label=U[i]["name"])
ax[1].set_ylabel("machine frequency [Hz]"); ax[1].legend(ncol=4, fontsize=7, loc="upper left")
for j, i in enumerate(inst):
    ax[2].plot(t, sm(c[f"{i}:POUT"]) * U[i]["S"], lw=0.9, color=cm(j % 20))
    ax[2].hlines(U[i]["P"], t[0], t[-1], colors=[cm(j % 20)], linestyles="dotted", lw=0.8)
ax[2].set_ylabel("unit P [MW] (dotted: load flow)"); ax[2].set_xlabel("t [s]")
for x, lab in ((2.0, "machines take over"), (2.1, ""), (5.0, "rotors released")):
    for a_ in ax: a_.axvline(x, color="gray", lw=0.6, ls="--")
    if lab: ax[0].text(x + 0.05, 452, lab, fontsize=8, color="gray", va="top")
for a_ in ax: a_.grid(alpha=0.3)
ax[0].set_title(f"v2 run {a.tag}")
os.makedirs(os.path.join(HERE, "figs"), exist_ok=True); fig.tight_layout()
out1 = os.path.join(HERE, "figs", f"plot_{a.tag}.png"); fig.savefig(out1, dpi=100); print(out1)
if a.ref:
    t2, c2, vb2, inst2, f2, _ = run(a.ref)
    fig, ax = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    for (tt, vv, ff, lab, col) in ((t2, vb2, f2, a.ref, "tab:red"), (t, vb, f, a.tag, "tab:blue")):
        V = np.array(list(vv.values())); F = np.array(list(ff.values()))
        ax[0].plot(tt, V.mean(axis=0), color=col, lw=1.2, label=f"{lab}: mean of 24 buses")
        ax[0].fill_between(tt, V.min(axis=0), V.max(axis=0), color=col, alpha=0.15)
        ax[1].fill_between(tt, F.min(axis=0), F.max(axis=0), color=col, alpha=0.35, label=f"{lab}: min..max of 17 machines")
    ax[0].set_ylabel("bus voltage [kV]\n(mean, band = min..max)"); ax[0].set_ylim(0, 600); ax[0].legend(fontsize=8)
    ax[1].set_ylabel("machine frequency [Hz]"); ax[1].set_ylim(44, 56); ax[1].legend(fontsize=8); ax[1].set_xlabel("t [s]")
    for a_ in ax: a_.grid(alpha=0.3)
    ax[0].set_title(f"before ({a.ref}) and after ({a.tag})")
    fig.tight_layout(); out2 = os.path.join(HERE, "figs", f"plot_{a.tag}_vs_{a.ref}.png"); fig.savefig(out2, dpi=100); print(out2)
