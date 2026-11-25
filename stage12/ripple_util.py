r"""S27 ripple diagnostic: does the 17 Hz collector mode grow with plant utilisation (current limit Imax 1.1)?

usage: python stage12/ripple_util.py <outdir> <label>=<psout> ...
Per run and per collector bus: 14-22 Hz band amplitude of VDF (FFT, Hann) in 3.0-4.98 s and 4.0-4.98 s,
plant P, and utilisation |i| = sqrt(ID^2 + IQ^2) per plant (pu of Sbase) against Imax 1.1.
"""
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mhi.psout
import numpy as np

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
runs = [a.split("=", 1) for a in sys.argv[2:]]
PSB = {1: 3315.0, 2: 223.6, 3: 217.1, 4: 3122.6, 5: 841.1, 6: 210.6, 7: 735.8, 8: 526.5, 9: 440.7, 10: 306.8,
       11: 1552.2, 12: 795.6, 13: 169.0, 14: 3247.4, 15: 765.7, 16: 452.4, 17: 4071.6, 18: 520.0}
BUS = {"33": [1, 18], "34": [5, 6, 7, 8, 9, 10, 11], "35": [12, 13, 14], "36": [2, 3, 4], "38": [15, 16, 17]}


def band(t, y, w0, w1):
    m = (t >= w0) & (t <= w1); yy = y[m] - y[m].mean(); dt = t[1] - t[0]
    A = np.abs(np.fft.rfft(yy * np.hanning(len(yy)))) * 2 / (0.5 * len(yy)); f = np.fft.rfftfreq(len(yy), dt)
    s = (f >= 14) & (f <= 22); i = np.argmax(A[s])
    return A[s][i], f[s][i]


L = []; res = {}
for lab, ps in runs:
    r = mhi.psout.File(ps).run(0)
    g = lambda p: np.asarray(r.call(p, sep="/").data, float)
    t = np.asarray(r.call("Root/Main/RES_Plant[1]/VDF/0/1", sep="/").domain.data, float)
    L.append(f"## {lab}: {ps}  (t {t[0]:.2f}..{t[-1]:.2f})")
    res[lab] = {}
    for b, ks in BUS.items():
        v = np.mean([g(f"Root/Main/RES_Plant[{k}]/VDF/0/1") for k in ks], axis=0)
        a3, f3 = band(t, v, 3.0, 4.98); a4, f4 = band(t, v, 4.0, 4.98)
        m = (t >= 4.0) & (t <= 4.98)
        util = []; P = 0.0
        for k in ks:
            c = {x: g(f"Root/Main/RES_Plant[{k}]/{x}/0/1")[m] for x in ("ID", "IQ", "VD", "VQ")}
            util.append(float(np.sqrt(c["ID"] ** 2 + c["IQ"] ** 2).mean())); P += float((c["VD"] * c["ID"] + c["VQ"] * c["IQ"]).mean() * PSB[k])
        res[lab][b] = (a4, max(util))
        L.append(f"  bus {b}: 17 Hz amp 3-5 s {a3:.5f} pu @ {f3:.1f} Hz | 4-5 s {a4:.5f} @ {f4:.1f} | P {P:6.0f} MW | "
                 f"|i| max {max(util):.3f} pu (Imax 1.1) | VDF {v[m].mean():.4f}")
open(os.path.join(out, "ripple_util.txt"), "w").write("\n".join(L)); print("\n".join(L))
fig, ax = plt.subplots(figsize=(8, 5))
for lab in res:
    x = [res[lab][b][1] for b in BUS]; y = [res[lab][b][0] for b in BUS]
    ax.scatter(x, y, label=lab)
    for b, xx, yy in zip(BUS, x, y): ax.annotate(b, (xx, yy), fontsize=7)
ax.set(xlabel="max plant |i| on the bus [pu]", ylabel="17 Hz amplitude of collector VDF, 4-5 s [pu]", yscale="log")
ax.grid(alpha=0.3); ax.legend(); fig.tight_layout(); fig.savefig(os.path.join(out, "ripple_util.png"), dpi=110)
