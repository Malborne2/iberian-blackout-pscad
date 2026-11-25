r"""S26: print a few channels' stats (used to check RPOS vs FMF after the ladder repair).

usage: python stage12\chan_stats.py <psout> <chan> [<chan> ...]
"""
import sys
import numpy as np
import mhi.psout

ps = sys.argv[1]
r = mhi.psout.File(ps).run(0)
for ch in sys.argv[2:]:
    try:
        tr = r.call(f"Root/Main/{ch}/0/1", sep="/")
        t = np.asarray(tr.domain.data, float)
        y = np.asarray(tr.data, float)
        print(f"{ch:6s} n={len(t):5d} t {t[0]:.3f}-{t[-1]:.3f} first {y[0]:+10.4f} last {y[-1]:+10.4f} "
              f"min {y.min():+10.4f} max {y.max():+10.4f}")
    except Exception as e:  # noqa: BLE001
        print(f"{ch:6s} ERROR {type(e).__name__}: {e}")
