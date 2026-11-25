r"""S26: read the tranche branch currents ILF1..6 from the PSOUT (mhi.psout run.call paths).

usage: python stage12\check_tranches.py <psout> [w0 w1]
The varrlc `I` field publishes one channel per phase; the pgb on the label `ILFk` gives a single
channel at Root/Main/ILFk/0/1.  Both are tried.
"""
import sys
import numpy as np
import mhi.psout

ps = sys.argv[1]
w0, w1 = (float(x) for x in sys.argv[2:4]) if len(sys.argv) > 3 else (10.0, 12.0)
r = mhi.psout.File(ps).run(0)
print(f"# {ps}  window {w0}-{w1} s")
for k in range(1, 7):
    for path in (f"Root/Main/ILF{k}/0/1", f"Root/Main/LF{k}/I/0/1"):
        try:
            tr = r.call(path, sep="/")
            t = np.asarray(tr.domain.data, float)
            y = np.asarray(tr.data, float)
            w = (t >= w0) & (t <= w1)
            print(f"  LF{k}: {path:26s} mean|I| {np.abs(y[w]).mean():8.4f}  rms {np.sqrt((y[w]**2).mean()):8.4f} kA")
            break
        except Exception:
            continue
    else:
        print(f"  LF{k}: not recorded")
