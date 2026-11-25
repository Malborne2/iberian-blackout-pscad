r"""Read the lt7 AVR bench cases (bench_avr.py) and compare them; writes iberia_eq\pscad\figs\bench_avr.png.

usage: python iberia_eq\pscad\bench_avr_read.py base ldcneg ldcpos qloop
Windows: 15-20 s (before the grid ramp), 48-50 s (end of the 30 s ramp, +12 kV), 75-80 s (20-30 s after it).
QOUT is machine pu (x 1,111 MVA); QHV is the 3-phase total (Mvar, + = grid to unit; checked PHV = -1,095 vs unit 1,097 MW, S30) at the 400 kV side; VHV is LN pu; VIT[1] = |Vt| pu.
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from legacy_out import load
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

S = 1111.0
tags = sys.argv[1:] or ["base", "ldcneg", "ldcpos", "qloop"]
fig, ax = plt.subplots(3, 1, figsize=(9, 9), sharex=True)
for tag in tags:
    fo = rf"C:\PSCAD_work\lt7_{tag}\lt7.gf81_x86"
    if not os.path.exists(os.path.join(fo, "lt7.infx")): print(tag, "no output yet"); continue
    t, c = load(fo, "lt7")
    q, vit, vhv, qhv, dvr = c["SyncUnit(0):QOUT"] * S, c["SyncUnit(0):VIT[1]"], c["VHV"], c["QHV"], c["SyncUnit(0):DVR"]
    row = []
    for a, b in ((15, 20), (48, 50), (75, 80)):
        m = (t >= a) & (t < b)
        row.append((q[m].mean(), qhv[m].mean(), vit[m].mean(), 400 * vhv[m].mean(), dvr[m].mean()))
    d = [r - row[0][i] for i, r in enumerate(row[2])]
    print(f"{tag:7s} pre: Qgen {row[0][0]:+6.0f}  QHV {row[0][1]:+6.0f} Mvar  Vt {row[0][2]:.4f}  VHV {row[0][3]:6.1f} kV | "
          f"end of ramp: Qgen {row[1][0]:+6.0f}  VHV {row[1][3]:6.1f} | settled: Qgen {row[2][0]:+6.0f}  QHV {row[2][1]:+6.0f}  "
          f"Vt {row[2][2]:.4f}  VHV {row[2][3]:6.1f} kV  DVR {row[2][4]:+.4f} | change: dQgen {row[2][0] - row[0][0]:+.0f} Mvar, "
          f"dVHV {row[2][3] - row[0][3]:+.2f} kV, dVt {row[2][2] - row[0][2]:+.4f}")
    w = c.get("SyncUnit(0):Wspd")
    if w is not None and t[-1] > 65:                         # swing after the 60 s phase step: frequency and damping (log decrement)
        m = (t > 60.02) & (t < 72); x = w[m] - np.median(w[(t > 70) & (t < 72)]); tt = t[m]
        pk = [i for i in range(1, len(x) - 1) if x[i] > x[i - 1] and x[i] >= x[i + 1] and x[i] > 0.05 * np.abs(x).max()]
        if len(pk) >= 3:
            per = np.diff(tt[pk]).mean(); dl = np.log(x[pk[0]] / x[pk[2]]) / 2; zeta = dl / np.sqrt(4 * np.pi ** 2 + dl ** 2)
            print(f"{tag:7s} swing after 60 s step: f {1 / per:.3f} Hz, damping ratio {zeta:.3f}, first peak {x[pk[0]]:.2e} pu speed")
        else: print(f"{tag:7s} swing: fewer than 3 peaks")
    k = max(1, len(t) // 4000)
    ax[0].plot(t[::k], q[::k], label=tag); ax[1].plot(t[::k], 400 * vhv[::k], label=tag); ax[2].plot(t[::k], vit[::k], label=tag)
ax[0].set_ylabel("unit Q [Mvar]"); ax[1].set_ylabel("V 400 kV side [kV]"); ax[2].set_ylabel("V terminal [pu]"); ax[2].set_xlabel("t [s]")
for a_ in ax: a_.grid(alpha=0.3); a_.legend(fontsize=8)
ax[0].set_title("lt7 bench: grid EV +3 % ramp 20-50 s (S30)")
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"), exist_ok=True)
fig.tight_layout(); fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs", "bench_avr.png"), dpi=110)
