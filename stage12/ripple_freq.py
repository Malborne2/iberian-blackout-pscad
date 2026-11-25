r"""S26: precise frequency and amplitude of the plant ripple in one or more runs.

usage: python stage12/ripple_freq.py <outdir> <w0> <w1> <label>=<psout> [...]
Uses a long window (default given), a Hann window and FFT with zero padding, then a parabolic
interpolation on the log-magnitude to get the peak frequency to <0.1 Hz.  Reports, per run:
the peak in 8-40 Hz and its amplitude (pu), for bus 34 VDF and the bus-34 plant P.
"""
import os, sys
import numpy as np
import mhi.psout

out = sys.argv[1]
w0, w1 = float(sys.argv[2]), float(sys.argv[3])
runs = [a.split("=", 1) for a in sys.argv[4:]]
os.makedirs(out, exist_ok=True)
NB34 = [5, 6, 7, 8, 9, 10, 11]
SB = {5: 841.1, 6: 210.6, 7: 735.8, 8: 526.5, 9: 440.7, 10: 306.8, 11: 1552.2}
L = [f"# ripple peak, window {w0}-{w1} s ({w1-w0:.2f} s)"]


def peak(y, dt, lo=8.0, hi=40.0):
    yy = y - y.mean()
    n = len(yy)
    win = np.hanning(n)
    N = 1 << int(np.ceil(np.log2(n * 16)))          # 16x zero padding
    A = np.abs(np.fft.rfft(yy * win, N)) * 2 / win.sum()
    fs = np.fft.rfftfreq(N, dt)
    sel = (fs >= lo) & (fs <= hi)
    i = np.argmax(A[sel])
    fs_, A_ = fs[sel], A[sel]
    if 0 < i < len(A_) - 1:
        a, b, c = np.log(A_[i - 1] + 1e-30), np.log(A_[i] + 1e-30), np.log(A_[i + 1] + 1e-30)
        d = 0.5 * (a - c) / (a - 2 * b + c)
        return fs_[i] + d * (fs_[1] - fs_[0]), np.exp(b - 0.25 * (a - c) * d)
    return fs_[i], A_[i]


for lab, p in runs:
    r = mhi.psout.File(p).run(0)

    def get(ch):
        tr = r.call(ch, sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)
    t, _ = get("Root/Main/SyncUnit[1]/Wspd/0/1")
    dt = t[1] - t[0]
    m = (t >= w0) & (t <= w1)
    v = np.mean([get(f"Root/Main/RES_Plant[{k}]/VDF/0/1")[1] for k in NB34], axis=0)[m]
    P = np.zeros(m.sum())
    for k in NB34:
        g = {c: get(f"Root/Main/RES_Plant[{k}]/{c}/0/1")[1][m] for c in ("VD", "VQ", "ID", "IQ")}
        P += (g["VD"] * g["ID"] + g["VQ"] * g["IQ"]) * SB[k]
    fv, av = peak(v, dt)
    fp, ap = peak(P, dt)
    L.append(f"{lab:7s} dt {dt*1e6:6.0f} us   V34: {fv:7.2f} Hz  amp {av:.5f} pu   "
             f"P34: {fp:7.2f} Hz  amp {ap:7.0f} MW   (samples {m.sum()})")

txt = "\n".join(L)
open(os.path.join(out, "ripple_freq.txt"), "w").write(txt)
print(txt)
