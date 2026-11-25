r"""Read one event run of a batch: event times, trips, relays, frequencies, voltages, powers; whole-trace figure.

usage: python stage12/batch_read.py <run folder> <T0> [<psout>]
Writes <run folder>/read.txt and read.png. T0 = snapshot time; events start at T0 + 1 (S5 window T0..T0+1).
Unit map (S26 L2): SyncUnit[1]=32, [2]=37, [3]=30, [4]=31, [5]=France. PTIE printed Spain -> France positive.
"""
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mhi.psout
import numpy as np

fold, T0 = sys.argv[1], float(sys.argv[2])
ps = sys.argv[3] if len(sys.argv) > 3 else os.path.join(fold, "ib6.gf81_x86", "ib6.psout")
r = mhi.psout.File(ps).run(0)
UN = {1: "32", 2: "37", 3: "30", 4: "31", 5: "FR"}
SB = {1: 15292.0, 2: 12838.0, 3: 6113.0, 4: 13548.0, 5: 200000.0}
PSB = {1: 3315.0, 2: 223.6, 3: 217.1, 4: 3122.6, 5: 841.1, 6: 210.6, 7: 735.8, 8: 526.5, 9: 440.7, 10: 306.8,
       11: 1552.2, 12: 795.6, 13: 169.0, 14: 3247.4, 15: 765.7, 16: 452.4, 17: 4071.6, 18: 520.0}
BUS = {1: "33", 18: "33", 2: "36", 3: "36", 4: "36", 12: "35", 13: "35", 14: "35", 15: "38", 16: "38", 17: "38",
       **{k: "34" for k in range(5, 12)}}


def g(p):
    try:
        tr = r.call(p, sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)
    except Exception:
        return None, None


t, _ = g("Root/Main/SyncUnit[1]/Wspd/0/1"); dt = t[1] - t[0]


def mm(y, s=0.02):   # centred moving mean, edge-padded (no zero-padding artefact at the ends)
    n = max(1, int(round(s / dt))); h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


def first(y, thr=0.5):
    i = np.argmax(y > thr); return t[i] if y.max() > thr else None


f = {i: g(f"Root/Main/SyncUnit[{i}]/Wspd/0/1")[1] / 2 / np.pi for i in UN}
P = {i: g(f"Root/Main/SyncUnit[{i}]/POUT/0/1")[1] * SB[i] for i in UN}
VIT = {i: g(f"Root/Main/SyncUnit[{i}]/VIT/0/1")[1] for i in UN}
ptie = -g("Root/Main/PTIE/0/1")[1]
plant = {}
for k in PSB:
    c = {x: g(f"Root/Main/RES_Plant[{k}]/{x}/0/1")[1] for x in ("VD", "VQ", "ID", "IQ", "VDF", "TRIP")}
    plant[k] = ((c["VD"] * c["ID"] + c["VQ"] * c["IQ"]) * PSB[k], c["VDF"], c["TRIP"])
L = []; pr = L.append
pr(f"# {ps}\n# t {t[0]:.3f}..{t[-1]:.3f} s, T0 {T0}, events from {T0 + 1}")
pre = (t >= T0) & (t <= T0 + 0.95)
pr("## S5 pre-event window " + f"{T0:.2f}-{T0 + 0.95:.2f} s: " +
   " ".join(f"f{UN[i]} {f[i][pre].mean():.4f} (p-p {1000 * (f[i][pre].max() - f[i][pre].min()):.1f} mHz)" for i in UN) +
   f"; PTIE {ptie[pre].mean():+.0f}; plants {sum(plant[k][0][pre].mean() for k in PSB):.0f} MW")
pr("## relays / breakers (first time > 0.5)")
for nm in ("BRK30", "BRK31", "BRK32", "BRK37", "BRKFR", "OOS1", "S1", "S2", "S3", "S4", "S5", "S6", "SP1", "SP2"):
    _, y = g(f"Root/Main/{nm}/0/1")
    if y is not None:
        pr(f"  {nm:6s} {first(y[t > T0 + 0.1] if False else np.where(t > T0 + 0.1, y, 0))}")
pr("## plant trips (TRIP first > 0.5): " + ", ".join(
    f"{k}(bus {BUS[k]}, {plant[k][0][pre].mean():.0f} MW) {first(np.where(t > T0 + 0.1, plant[k][2], 0)):.3f}"
    for k in PSB if first(np.where(t > T0 + 0.1, plant[k][2], 0)) is not None))
ev = t >= T0 + 1
pr(f"## extremes after T0+1: PTIE min {mm(ptie)[ev].min():+.0f} max {mm(ptie)[ev].max():+.0f} MW")
for i in UN:
    pr(f"  unit {UN[i]:>2}: f min {mm(f[i])[ev].min():.3f} max {mm(f[i])[ev].max():.3f} Hz; VIT max {mm(VIT[i])[ev].max():.3f} pu")
for b in ("33", "34", "35", "36", "38"):
    v = np.mean([plant[k][1] for k in PSB if BUS[k] == b], axis=0)
    pr(f"  collector {b}: VDF pre {v[pre].mean():.4f}, max {mm(v)[ev].max():.4f} pu (t {t[ev][np.argmax(mm(v)[ev])]:.2f})")
for tt in np.arange(T0 + 1, t[-1] + 1e-6, 1.0):
    m = (t > tt - 0.1) & (t <= tt)
    pr(f"  t {tt:6.2f}: f " + " ".join(f"{f[i][m].mean():.3f}" for i in UN) +
       f" | PTIE {ptie[m].mean():+6.0f} | plants {sum(plant[k][0][m].mean() for k in PSB):6.0f} | units " +
       " ".join(f"{P[i][m].mean():.0f}" for i in (1, 2, 3, 4)))
open(os.path.join(fold, "read.txt"), "w").write("\n".join(L)); print("\n".join(L))

fig, ax = plt.subplots(4, 1, figsize=(12, 13), sharex=True)
for i in UN: ax[0].plot(t, mm(f[i]), lw=0.8, label=UN[i])
ax[1].plot(t, mm(ptie), lw=0.8, label="PTIE S->F"); ax[1].plot(t, mm(sum(plant[k][0] for k in PSB)), lw=0.8, label="plants")
for b in ("33", "34", "35", "36", "38"):
    ax[2].plot(t, mm(np.mean([plant[k][1] for k in PSB if BUS[k] == b], axis=0)), lw=0.8, label=f"bus {b}")
for i in UN: ax[3].plot(t, mm(VIT[i]), lw=0.8, label=f"VIT {UN[i]}")
for a, yl in zip(ax, ["f [Hz]", "MW", "collector VDF [pu]", "unit VIT [pu]"]):
    a.set(ylabel=yl); a.grid(alpha=0.3); a.legend(fontsize=7, ncol=6); a.axvline(T0 + 1, color="k", lw=0.5)
ax[-1].set(xlabel="time [s]"); fig.suptitle(os.path.basename(fold)); fig.tight_layout()
fig.savefig(os.path.join(fold, "read.png"), dpi=110)
