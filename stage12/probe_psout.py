r"""S26: probe a PSOUT's time axis and one channel (sanity: is the file what we think it is?).

usage: python stage12/probe_psout.py <psout> [channel]
"""
import sys, numpy as np, mhi.psout

ps = sys.argv[1]
ch = sys.argv[2] if len(sys.argv) > 2 else "Root/Main/SyncUnit[1]/Wspd/0/1"
r = mhi.psout.File(ps).run(0)
tr = r.call(ch, sep="/")
t = np.asarray(tr.domain.data, float)
y = np.asarray(tr.data, float)
print("n", len(t), "t0", t[0], "t1", t[-1], "dt", t[1] - t[0], "monotonic", bool(np.all(np.diff(t) > 0)))
print("dups", int(np.sum(np.diff(t) == 0)))
for tt in (0.5, 4.9, 12.0, 16.0, 20.0, 24.0, 28.0, 30.0, 31.0, 32.0):
    k = int(np.searchsorted(t, tt))
    k = min(k, len(t) - 1)
    print(f"t={tt:7.2f}  idx={k:7d}  t[k]={t[k]:9.4f}  y={y[k]:.6f}")
