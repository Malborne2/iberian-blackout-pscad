r"""Time-step comparison of ib6b cold starts (S25): 20 us reference vs larger steps.

usage: python stage12\dt_compare.py <outdir> <label>=<psout> [<label>=<psout> ...]   (first one = reference)
Compares 0.1 s means at chosen times (plant MW per collector bus, collector VDF, unit P/Q, tie, HVDC)
and the ripple (p-p of 20 ms means and the dominant frequency) in the last 0.5 s before 5 s.
Writes <outdir>\dt_compare.txt and <outdir>\dt_compare.png.
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
SBI = {1: 15292.0, 2: 12838.0, 3: 6113.0, 4: 13548.0, 5: 200000.0}   # SyncUnit[i] -> 32, 37, 30, 31, France
UN = {1: "32", 2: "37", 3: "30", 4: "31", 5: "FR"}
TS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 4.9]
TEND = 5.0

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
runs = [a.split("=", 1) for a in sys.argv[2:]]


def load(path):
    r = mhi.psout.File(path).run(0)

    def get(p):
        tr = r.call(p, sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)
    t, _ = get("Root/Main/SyncUnit[1]/Wspd/0/1")
    m = t <= TEND + 1e-9
    t = t[m]
    D = {"t": t}
    for b in BUSES:
        ks = [k for k, (bb, s) in NB.items() if bb == b]
        D["V" + b] = np.mean([get(f"Root/Main/RES_Plant[{k}]/VDF/0/1")[1][m] for k in ks], axis=0)
        p = np.zeros_like(t)
        for k in ks:
            g = {c: get(f"Root/Main/RES_Plant[{k}]/{c}/0/1")[1][m] for c in ("VD", "VQ", "ID", "IQ")}
            p += (g["VD"] * g["ID"] + g["VQ"] * g["IQ"]) * NB[k][1]
        D["P" + b] = p
    for i in SBI:
        D["UP" + UN[i]] = get(f"Root/Main/SyncUnit[{i}]/POUT/0/1")[1][m] * SBI[i]
        D["UQ" + UN[i]] = get(f"Root/Main/SyncUnit[{i}]/QOUT/0/1")[1][m] * SBI[i]
        D["UV" + UN[i]] = get(f"Root/Main/SyncUnit[{i}]/VIT/0/1")[1][m]
    D["PTIE"] = -get("Root/Main/PTIE/0/1")[1][m]
    hv = {c: get(f"Root/Main/HVDC_T/{c}/0/1")[1][m] for c in ("ID", "IQ", "VD", "VQ")}
    D["HVDC"] = -(hv["VD"] * hv["ID"] + hv["VQ"] * hv["IQ"]) * 1000.0
    D["TRIP"] = max(get(f"Root/Main/RES_Plant[{k}]/TRIP/0/1")[1][m].max() for k in NB)
    return D


def mean_at(D, key, tt, w=0.1):
    m = (D["t"] > tt - w / 2) & (D["t"] <= tt + w / 2)
    return D[key][m].mean()


def mm(y, dt, n_s=0.02):
    n = max(1, int(round(n_s / dt)))
    return np.convolve(y, np.ones(n) / n, mode="same")


def ripple(D, key, w0=4.5, w1=4.98):
    t = D["t"]; dt = t[1] - t[0]
    m = (t >= w0) & (t <= w1)
    y = D[key][m]
    pp = mm(D[key], dt)[m]
    yy = y - y.mean()
    f = np.fft.rfftfreq(len(yy), dt); A = np.abs(np.fft.rfft(yy * np.hanning(len(yy))))
    sel = (f > 2) & (f < 400)
    return pp.max() - pp.min(), f[sel][np.argmax(A[sel])]


Ds = {lab: load(p) for lab, p in runs}
ref = runs[0][0]
L = []; pr = L.append
pr("# ib6b cold start, time-step comparison; reference = " + ref)
for lab, p in runs:
    pr(f"#   {lab}: {p}  (dt plot {Ds[lab]['t'][1]-Ds[lab]['t'][0]:.6f} s, plant TRIP max {Ds[lab]['TRIP']:.0f})")
keys = [("P" + b, "MW", 0) for b in BUSES] + [("V" + b, "pu", 4) for b in BUSES] + \
       [("UP" + u, "MW", 0) for u in UN.values()] + [("UQ" + u, "Mvar", 0) for u in UN.values()] + \
       [("UV" + u, "pu", 4) for u in UN.values()] + [("PTIE", "MW", 0), ("HVDC", "MW", 0)]
for tt in TS:
    pr(f"\n--- t = {tt:.2f} s (0.1 s means); columns: " + "  ".join(lab for lab, _ in runs) + "   (difference to " + ref + ")")
    for k, u, nd in keys:
        vals = [mean_at(Ds[lab], k, tt) for lab, _ in runs]
        diffs = [v - vals[0] for v in vals[1:]]
        pr(f"  {k:6s} [{u:4s}] " + "  ".join(f"{v:10.{nd}f}" for v in vals) + "   d: " + "  ".join(f"{d:+9.{nd}f}" for d in diffs))
pr("\n--- ripple 4.5-4.98 s: p-p of 20 ms means / dominant frequency [Hz]")
for k in ["V" + b for b in BUSES] + ["P" + b for b in BUSES] + ["PTIE"]:
    pr(f"  {k:6s} " + "  ".join(f"{lab}: {ripple(Ds[lab], k)[0]:9.4f} @ {ripple(Ds[lab], k)[1]:6.1f}" for lab, _ in runs))
open(os.path.join(out, "dt_compare.txt"), "w").write("\n".join(L))
print("\n".join(L))

fig, ax = plt.subplots(4, 1, figsize=(12, 12), sharex=True)
for lab, _ in runs:
    D = Ds[lab]; dt = D["t"][1] - D["t"][0]
    ax[0].plot(D["t"], mm(D["V34"], dt), lw=0.8, label=f"bus 34 VDF {lab}")
    ax[1].plot(D["t"], mm(D["P34"], dt), lw=0.8, label=f"bus 34 plant P {lab}")
    ax[2].plot(D["t"], mm(sum(D["P" + b] for b in BUSES), dt), lw=0.8, label=f"all plants {lab}")
    ax[3].plot(D["t"], mm(D["UQ32"], dt), lw=0.8, label=f"unit 32 Q {lab}")
for a, yl in zip(ax, ["pu", "MW", "MW", "Mvar"]):
    a.set(ylabel=yl); a.grid(alpha=0.3); a.legend(fontsize=7)
ax[-1].set(xlabel="time [s]")
fig.suptitle("ib6b cold start: time-step comparison (20 ms means)"); fig.tight_layout()
fig.savefig(os.path.join(out, "dt_compare.png"), dpi=110)
