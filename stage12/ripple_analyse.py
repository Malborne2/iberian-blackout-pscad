r"""S26: structure of the collector ripple (18 Hz) in a settled window.

usage: python stage12\ripple_analyse.py <psout> <outdir> [w0 w1]
Prints, per collector bus: VDF p-p of the 20 ms mean, the un-averaged p-p, the dominant frequency
(FFT of the 20 ms-mean signal, 2-200 Hz) and its amplitude; the same for the plant P and Q.
Also: cross-bus coherence at the dominant frequency (|coherence| between bus VDF signals), and
per-plant amplitude spread (is one plant the source?).
Writes <outdir>\ripple.txt and <outdir>\ripple.png.
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

ps, out = sys.argv[1], sys.argv[2]
w0, w1 = (float(x) for x in sys.argv[3:5]) if len(sys.argv) > 4 else (30.0, 32.0)
os.makedirs(out, exist_ok=True)
r = mhi.psout.File(ps).run(0)


def get(p):
    tr = r.call(p, sep="/")
    return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)


t, _ = get("Root/Main/SyncUnit[1]/Wspd/0/1")
dt = t[1] - t[0]
n20 = max(1, int(round(0.02 / dt)))


def mm(y, n=n20):
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


W = (t >= w0) & (t <= w1)
L = []
pr = L.append
pr(f"# {ps}\n# window {w0}-{w1} s, dt {dt*1e6:.1f} us, 20 ms moving mean ({n20} samples)\n")

V = {}
for b in BUSES:
    ks = [k for k, (bb, s) in NB.items() if bb == b]
    V[b] = np.mean([get(f"Root/Main/RES_Plant[{k}]/VDF/0/1")[1] for k in ks], axis=0)


def spec(y, w):
    yy = y[w] - y[w].mean()
    fs = np.fft.rfftfreq(len(yy), dt)
    A = np.abs(np.fft.rfft(yy * np.hanning(len(yy)))) * 2 / np.sum(np.hanning(len(yy)))
    sel = (fs > 2) & (fs < 400)
    i = np.argmax(A[sel])
    return fs[sel][i], A[sel][i], fs, A


pr("bus    VDFmean   p-p(20ms)  p-p(raw)   f_peak  amp_peak[pu]  amp@1650Hz")
for b in BUSES:
    m = mm(V[b])
    f, a, fs, A = spec(m, W)
    sel = (fs > 1600) & (fs < 1700)
    pr(f"{b:>3}  {m[W].mean():9.4f}  {m[W].max()-m[W].min():9.4f}  {V[b][W].max()-V[b][W].min():9.4f}"
       f"  {f:7.1f}  {a:11.5f}  {(A[sel].max() if sel.any() else 0):11.5f}")

pr("\nper plant: bus, Sbase, VDFmean, p-p(20ms), f_peak, P_mean[MW], P p-p[MW], Q p-p[Mvar]")
for k, (b, s) in NB.items():
    v = get(f"Root/Main/RES_Plant[{k}]/VDF/0/1")[1]
    g = {c: get(f"Root/Main/RES_Plant[{k}]/{c}/0/1")[1] for c in ("VD", "VQ", "ID", "IQ")}
    P = (g["VD"] * g["ID"] + g["VQ"] * g["IQ"]) * s
    Q = (g["VQ"] * g["ID"] - g["VD"] * g["IQ"]) * s
    m = mm(v)
    f, a, _, _ = spec(m, W)
    pr(f"{k:2d} {b:>3} {s:8.1f}  {m[W].mean():.4f}  {m[W].max()-m[W].min():.4f}  {f:7.1f}"
       f"  {mm(P)[W].mean():8.0f}  {mm(P)[W].max()-mm(P)[W].min():7.0f}  {mm(Q)[W].max()-mm(Q)[W].min():7.0f}")

# coherence between bus VDF signals at the dominant frequency of bus 34
pb = "34"
f0, _, fs, A = spec(mm(V[pb]), W)
yy = {b: (mm(V[b])[W] - mm(V[b])[W].mean()) for b in BUSES}
Y = {b: np.fft.rfft(yy[b]) for b in BUSES}
i0 = int(np.argmin(np.abs(fs - f0)))
pr(f"\ncoherence at {f0:.1f} Hz (bus 34 phase reference)")
for b in BUSES:
    Ph = np.angle(Y[b][i0]) - np.angle(Y[pb][i0])
    c = np.abs(Y[b][i0]) * 2 / np.sum(np.hanning(len(yy[b])))
    pr(f"  bus {b}: |Y| {c:.5f} pu   phase vs 34 {np.degrees(np.angle(np.exp(1j*Ph))):+7.1f} deg")

open(os.path.join(out, "ripple.txt"), "w").write("\n".join(L))
print("\n".join(L))

fig, ax = plt.subplots(3, 1, figsize=(12, 10))
m = (t >= w0) & (t <= w1)
for b in BUSES:
    ax[0].plot(t[m], V[b][m], lw=0.6, label=f"bus {b}")
    ax[1].plot(t[m], mm(V[b])[m], lw=0.8, label=f"bus {b}")
ax[2].plot(fs, A, lw=0.8)
ax[0].set(ylabel="VDF raw [pu]", xlabel="t [s]")
ax[1].set(ylabel="VDF 20 ms mean [pu]", xlabel="t [s]")
ax[2].set(ylabel="|FFT| of bus-34 VDF", xlabel="f [Hz]", xlim=(0, 120))
for a in ax[:2]:
    a.grid(alpha=0.3); a.legend(fontsize=7)
ax[2].grid(alpha=0.3)
fig.suptitle(f"collector ripple, window {w0}-{w1} s: {os.path.basename(ps)}")
fig.tight_layout(); fig.savefig(os.path.join(out, "ripple.png"), dpi=110)
