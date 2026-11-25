"""Compare two psouts in detail: time grids, sample counts, max deviation."""
import sys
import numpy as np
import mhi.psout

A, B = sys.argv[1], sys.argv[2]


def get(path, chan):
    with mhi.psout.File(path) as f:
        r = f.run(0)
        tr = r.call(chan, sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)


for chan in ("Root/Main/Pg5/0/1", "Root/Main/multimeter[1]/2/Pd", "Root/Main/RES_Plant[1]/ID/0/1"):
    ta, ya = get(A, chan)
    tb, yb = get(B, chan)
    print(f"{chan}\n  pre  n={ya.size} t={ta[0]:.6f}..{ta[-1]:.6f} dt={ta[1]-ta[0]:.4g}")
    print(f"  post n={yb.size} t={tb[0]:.6f}..{tb[-1]:.6f} dt={tb[1]-tb[0]:.4g}")
    if ya.size == yb.size:
        d = np.abs(ya - yb)
        print(f"  max|diff| {d.max():.3e} at t={ta[int(d.argmax())]:.4f}; rms(pre) {np.sqrt(np.mean(ya**2)):.4g}")
    else:
        n = min(ya.size, yb.size)
        d = np.abs(ya[:n] - yb[:n])
        print(f"  (different length) first {n} samples max|diff| {d.max():.3e}")
