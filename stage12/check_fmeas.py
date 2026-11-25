r"""S26/WP9: ladder + frequency-meter check on a short run.

usage: python stage12/check_fmeas.py <psout>
Prints FMF / FMV / FMP (the three freq-meas outputs) and S1..S6, plus when each first fires.
"""
import sys
import numpy as np
import mhi.psout

ps = sys.argv[1]
r = mhi.psout.File(ps).run(0)


def get(ch):
    tr = r.call(ch, sep="/")
    return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)


t, _ = get("Root/Main/S1/0/1")
print(f"# {ps}  t {t[0]:.3f}..{t[-1]:.3f}  ({len(t)} samples)")
for ch in ("FMF", "FMV", "FMP"):
    try:
        d = get(f"Root/Main/{ch}/0/1")[1]
        print(f"  {ch}: first {d[0]:+10.4f}  last {d[-1]:+10.4f}  min {d.min():+10.4f}  max {d.max():+10.4f}")
    except Exception as e:  # noqa: BLE001
        print(f"  {ch}: NOT RECORDED ({type(e).__name__})")
for k in range(1, 7):
    v = get(f"Root/Main/S{k}/0/1")[1]
    print(f"  S{k}: max {v.max():5.1f}  first>0.5 {t[np.argmax(v > 0.5)] if (v > 0.5).any() else None}")
