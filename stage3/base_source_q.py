"""What did each ideal source supply at its collector bus in the pre-WP3 baseline? (bus voltage + P + Q)

usage: python stage3/base_source_q.py <psout>   (the 5-ideal-source baseline iberia4_flat_20s_base.psout)
Window 15-20 s, pu base 410.4 MVA (as in stage3\\wp3_report.py).
"""
import sys
import numpy as np
import mhi.psout

PS = sys.argv[1]
W = (15.0, 20.0)
SB = 410.4   # MVA, the source/multimeter pu base used since S10

with mhi.psout.File(PS) as f:
    r = f.run(0)

    def get(p):
        tr = r.call(p, sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)

    tm = None
    print(f"{PS}")
    print(f"{'meter':>6} {'Vd pu':>7} {'Pd pu':>8} {'Qd pu':>8} {'P MW':>8} {'Q Mvar':>8}")
    for k in range(1, 10):
        try:
            t, v = get(f"Root/Main/multimeter[{k}]/4/Vd")
            _, p = get(f"Root/Main/multimeter[{k}]/2/Pd")
            _, q = get(f"Root/Main/multimeter[{k}]/3/Qd")
        except Exception:
            break
        w = (t >= W[0]) & (t <= W[1])
        print("%6d %7.4f %+8.4f %+8.4f %8.1f %8.1f" % (
            k, v[w].mean(), p[w].mean(), q[w].mean(), p[w].mean() * SB, q[w].mean() * SB))
    print("\nsource P channels:")
    for nm in ("Pg5", "Pg6", "Pg7", "Pg8", "Pg9"):
        try:
            t, y = get(f"Root/Main/{nm}/0/1")
        except Exception:
            continue
        w = (t >= W[0]) & (t <= W[1])
        print("  %-4s %+8.4f pu  = %8.1f MW" % (nm, y[w].mean(), y[w].mean() * SB))
