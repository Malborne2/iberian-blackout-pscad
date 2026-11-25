r"""S26: did the LFDD ladder fire, and did anything change? (WP9 evidence)

usage: python stage12\check_ladder.py <psout> [t1,t2,...]
Prints S1..S6 at the given times plus the time each first goes to 1.
"""
import sys
import numpy as np
import mhi.psout

ps = sys.argv[1]
ts = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else []
r = mhi.psout.File(ps).run(0)


def get(ch):
    tr = r.call(ch, sep="/")
    return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)


t, _ = get("Root/Main/S1/0/1")
S = {k: get(f"Root/Main/S{k}/0/1")[1] for k in range(1, 7)}
print(f"# {ps}  t {t[0]:.2f}..{t[-1]:.2f}")
for k, v in S.items():
    i = np.argmax(v > 0.5) if (v > 0.5).any() else None
    print(f"  S{k}: first 1 at {None if i is None else f'{t[i]:.3f} s'}   max {v.max():.0f}")
if ts:
    print("  t      " + "  ".join(f"S{k}" for k in S))
    for tt in ts:
        k = min(len(t) - 1, int(np.searchsorted(t, tt)))
        print(f"  {tt:6.2f} " + "  ".join(f"{S[j][k]:.0f}" for j in S))
