"""Probe how the multimeter channels are sampled in two runs."""
import sys
import numpy as np
import mhi.psout

A, B = sys.argv[1], sys.argv[2]
CH = "Root/Main/multimeter[9]/2/Pd"
for p in (A, B):
    with mhi.psout.File(p) as f:
        r = f.run(0)
        tr = r.call(CH, sep="/")
        t = np.asarray(tr.domain.data, float)
        y = np.asarray(tr.data, float)
    print(p)
    print(f"  n={t.size}  t={t[0]:.6f}..{t[-1]:.6f}")
    print(f"  dt: min {np.diff(t).min():.6g} max {np.diff(t).max():.6g} mean {np.diff(t).mean():.6g}")
    print("  first 8:", np.round(t[:8], 5))
    print("  last 4 :", np.round(t[-4:], 5))
    m = (t >= 2.0) & (t <= 3.0)
    print(f"  mean 2-3 s ({m.sum()} samples) = {y[m].mean():.6f}; y range {y[m].min():.6f}..{y[m].max():.6f}")
