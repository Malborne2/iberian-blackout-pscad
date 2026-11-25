"""What each remaining ideal source delivers at 15-20 s (WP3 bus targets)."""
import sys
import numpy as np
import mhi.psout

PS = sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\s19\iberia4_flat_20s_base.psout"
SB = 410.4
with mhi.psout.File(PS) as f:
    r = f.run(0)

    def get(c):
        tr = r.call(f"Root/Main/{c}/0/1", sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)

    print(f"{'chan':6} {'10-15 s':>10} {'15-20 s':>10} {'MW (15-20)':>11}")
    for k in (5, 6, 7, 9):
        t, y = get(f"Pg{k}")
        a, b = (t >= 10) & (t < 15), (t >= 15) & (t <= 20)
        print(f"Pg{k:<4} {y[a].mean():10.5f} {y[b].mean():10.5f} {y[b].mean() * SB:11.1f}")
    for k in (5, 6, 7, 9):
        t, y = get(f"Vg{k}")
        b = (t >= 15) & (t <= 20)
        print(f"Vg{k:<4} {y[b].mean():10.4f} kV = {y[b].mean() / 400:.4f} pu")
    for k in range(1, 6):
        try:
            t, y = get(f"SyncUnit[{k}]/Wspd")
            b = (t >= 15) & (t <= 20)
            print(f"unit {k}: f 15-20 {y[b].mean() / 2 / np.pi:.5f} Hz, p-p {np.ptp(y[b]) / 2 / np.pi * 1000:.2f} mHz")
        except Exception as e:
            print("unit", k, e)
    for k in (1, 2):
        t, y = get(f"RES_Plant[{k}]/ID")
        b = (t >= 15) & (t <= 20)
        print(f"plant {k}: ID {y[b].mean():.5f}")
