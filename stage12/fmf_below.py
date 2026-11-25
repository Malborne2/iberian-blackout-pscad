r"""S26: print FMF at chosen times and the dwell below a threshold.

usage: python stage12\fmf_below.py <psout> <threshold> [t1,t2,...]
"""
import sys
import numpy as np
import mhi.psout

ps, th = sys.argv[1], float(sys.argv[2])
ts = [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else []
r = mhi.psout.File(ps).run(0)
tr = r.call("Root/Main/FMF/0/1", sep="/")
t = np.asarray(tr.domain.data, float)
y = np.asarray(tr.data, float)
m = y < th
print(f"# {ps}: FMF min {y.min():.3f} at t={t[np.argmin(y)]:.3f}; samples below {th}: {m.sum()}")
if m.any():
    print(f"  first below at {t[np.argmax(m)]:.3f} s, last below at {t[len(m)-1-np.argmax(m[::-1])]:.3f} s")
for tt in ts:
    k = min(len(t) - 1, int(np.searchsorted(t, tt)))
    print(f"  t={tt:6.3f}  FMF={y[k]:8.3f}")
