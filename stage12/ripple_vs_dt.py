r"""S26: amplitude of the ~17-18 Hz collector ripple vs time step (WP7 (a) falsifier).

usage: python stage12/ripple_vs_dt.py <outdir> <label>=<psout> [...]
For each run, in the given window (default 4.5-4.98 s):
  * p-p of the 20 ms moving mean of each collector VDF,
  * amplitude (pu) of the 14-22 Hz band by FFT, and the peak frequency in that band,
  * same for the plant P of bus 34 and the unit Q of unit 32.
Writes <outdir>\ripple_vs_dt.txt and .png (amplitude vs dt on a log-log axis).
"""
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mhi.psout
import numpy as np

NB = {1: ("33", 520.0), 2: ("36", 223.6), 3: ("36", 217.1), 4: ("36", 3122.6), 5: ("34", 841.1),
      6: ("34", 210.6), 7: ("34", 735.8), 8: ("34", 526.5), 9: ("34", 440.7), 10: ("34", 306.8),
      11: ("34", 1552.2), 12: ("35", 795.6), 13: ("35", 169.0), 14: ("35", 3247.4),
      15: ("38", 765.7), 16: ("38", 452.4), 17: ("38", 4071.6), 18: ("33", 3315.0)}
BUSES = ["33", "34", "35", "36", "38"]
SB = {"32": 15292.0, "37": 12838.0, "30": 6113.0, "31": 13548.0, "FR": 200000.0}

out = sys.argv[1]
w0, w1 = 4.5, 4.98
if len(sys.argv) > 2 and sys.argv[2].startswith("--win"):
    w0, w1 = (float(x) for x in sys.argv[2].split("=")[1].split(","))
    runs = [a.split("=", 1) for a in sys.argv[3:]]
else:
    runs = [a.split("=", 1) for a in sys.argv[2:]]
os.makedirs(out, exist_ok=True)


def band(y, t, lo=14.0, hi=22.0):
    m = (t >= w0) & (t <= w1)
    yy = y[m] - y[m].mean()
    dt = t[1] - t[0]
    fs = np.fft.rfftfreq(len(yy), dt)
    win = np.hanning(len(yy))
    A = np.abs(np.fft.rfft(yy * win)) * 2 / win.sum()
    sel = (fs >= lo) & (fs <= hi)
    i = np.argmax(A[sel])
    return fs[sel][i], A[sel][i]


def mm(y, dt, sec=0.02):
    n = max(1, int(round(sec / dt)))
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


L = []
pr = L.append
pr(f"# ~17 Hz collector ripple vs time step, window {w0}-{w1} s")
pr("run     dt[us]   " + "  ".join(f"V{b}: p-p / amp17 / f" for b in BUSES) + "   P34 p-p [MW] / amp17   Q32 amp17 [Mvar]")
res = {}
for lab, p in runs:
    r = mhi.psout.File(p).run(0)

    def get(ch):
        tr = r.call(ch, sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)
    t, _ = get("Root/Main/SyncUnit[1]/Wspd/0/1")
    dt = t[1] - t[0]
    m = (t >= w0) & (t <= w1)
    row = [f"{lab:7s} {dt*1e6:7.0f}   "]
    amps = {}
    for b in BUSES:
        ks = [k for k, (bb, s) in NB.items() if bb == b]
        v = np.mean([get(f"Root/Main/RES_Plant[{k}]/VDF/0/1")[1] for k in ks], axis=0)
        pp = mm(v, dt)[m]
        f, a = band(v, t)
        amps[b] = a
        row.append(f"{pp.max()-pp.min():.4f}/{a:.5f}/{f:5.1f}")
    # bus-34 plant P
    ks = NB and [k for k, (bb, s) in NB.items() if bb == "34"]
    P = np.zeros_like(t)
    for k in ks:
        g = {c: get(f"Root/Main/RES_Plant[{k}]/{c}/0/1")[1] for c in ("VD", "VQ", "ID", "IQ")}
        P += (g["VD"] * g["ID"] + g["VQ"] * g["IQ"]) * NB[k][1]
    fp, ap = band(P, t)
    q = get("Root/Main/SyncUnit[1]/QOUT/0/1")[1]
    fq, aq = band(q, t)
    row.append(f"{mm(P, dt)[m].max()-mm(P, dt)[m].min():7.0f}/{ap:7.0f}      {aq*15292:7.0f} ({fq:4.1f} Hz)")
    pr("  ".join(row))
    res[lab] = (dt, amps)

pr("\nlinear fit of log(amplitude) vs log(dt), bus 34:")
xs = np.array([np.log(res[l][0]) for l in res])
ys = np.array([np.log(res[l][1]["34"]) for l in res])
k = np.polyfit(xs, ys, 1)[0]
pr(f"  slope = {k:.2f}  (1.0 = linear in dt, 2.0 = dt^2, 0 = dt-independent)")
open(os.path.join(out, "ripple_vs_dt.txt"), "w").write("\n".join(L))
print("\n".join(L))

fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
for b in BUSES:
    d = [res[l][0] * 1e6 for l in res]
    a = [res[l][1][b] for l in res]
    o = np.argsort(d)
    ax[0].loglog(np.array(d)[o], np.array(a)[o], "o-", label=f"bus {b}")
ax[0].set(xlabel="time step [us]", ylabel="17 Hz amplitude [pu]", title="collector VDF 17 Hz amplitude")
ax[0].grid(alpha=0.3, which="both"); ax[0].legend(fontsize=7)
ax[1].axis("off")
ax[1].text(0.02, 0.5, "\n".join(L), fontsize=7, family="monospace", va="center")
fig.tight_layout(); fig.savefig(os.path.join(out, "ripple_vs_dt.png"), dpi=110)
