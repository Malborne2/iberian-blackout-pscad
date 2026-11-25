"""Split plant currents into grid-side sum and circulating part; THD of each (Session 17).
usage: cm_check.py <psout> <t0> <t1>"""
import sys, numpy as np, mhi.psout
ps, lo, hi = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
def thd(t, y):
    s = (t >= lo) & (t < hi); tt, yy = t[s], y[s]
    h = [abs(2 * np.mean(yy * np.exp(-1j * 2 * np.pi * 50 * k * tt))) for k in range(1, 61)]
    return h[0], np.sqrt(np.sum(np.square(h[1:]))) / h[0] * 100, np.sqrt(np.mean(np.square(yy - np.mean(yy))))
with mhi.psout.File(ps) as f:
    run = f.run(0)
    get = lambda p: (np.asarray(run.call(p, sep="/").domain.data), np.asarray(run.call(p, sep="/").data))
    t, i1 = get("Root/Main/RES_Plant[1]/IsrcA/0/1")
    _, i2 = get("Root/Main/RES_Plant[2]/IsrcA/0/1")
for nm, y in (("plant 1", i1), ("plant 2", i2), ("grid = sum", i1 + i2), ("circulating = (i1-i2)/2", (i1 - i2) / 2)):
    a, d, r = thd(t, y)
    print(f"{nm:26s} I1 {a:.4f} kA  THD {d:6.2f} %  rms {r:.4f} kA")
