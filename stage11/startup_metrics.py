r"""Start-up metrics for one ib5 run: the numbers behind the WP7 step-0 bisection.

usage: python stage11\startup_metrics.py <psout> [t0 t1]
prints, for the whole run and for the last 0.5 s: collector VDF per bus (mean/min/max/p-p),
the plant fleet and unit totals, the five machine speeds, the tie range, and the dominant
oscillation frequency of the bus-33 collector voltage (0-6 Hz band).
"""
import sys

import mhi.psout
import numpy as np

KPLANT = 1.30
NBUS = {1: ("33", 400.0), 2: ("36", 172.0), 3: ("36", 167.0), 4: ("36", 2402.0),
        5: ("34", 647.0), 6: ("34", 162.0), 7: ("34", 566.0), 8: ("34", 405.0),
        9: ("34", 339.0), 10: ("34", 236.0), 11: ("34", 1194.0),
        12: ("35", 612.0), 13: ("35", 130.0), 14: ("35", 2498.0),
        15: ("38", 589.0), 16: ("38", 348.0), 17: ("38", 3132.0), 18: ("33", 2550.0)}
BUSES = ["33", "34", "35", "36", "38"]
MACH = [6113.0, 13548.0, 15292.0, 12838.0, 200000.0]

ps = sys.argv[1]
f = mhi.psout.File(ps)
r = f.run(0)


def g(p):
    tr = r.call("Root/Main/" + p, sep="/")
    return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)


t, _ = g("RES_Plant[1]/VDF/0/1")
dt = t[1] - t[0]
w = (t >= t[-1] - 0.5)
print(f"{ps}\nt {t[0]:.3f}..{t[-1]:.3f} s   window (last 0.5 s) {t[-1]-0.5:.2f}..{t[-1]:.2f} s")

print(f"{'bus':4} {'VDF mean':>9} {'min':>7} {'max':>7} {'p-p':>7} {'p-p last .5s':>13}")
for b in BUSES:
    ks = [k for k, (bb, s) in NBUS.items() if bb == b]
    v = np.mean([g(f"RES_Plant[{k}]/VDF/0/1")[1] for k in ks], axis=0)
    print(f"{b:>4} {v[w].mean():9.4f} {v.min():7.4f} {v.max():7.4f} {np.ptp(v):7.4f} {np.ptp(v[w]):13.4f}")

pw = np.zeros_like(t)
for k in range(1, 19):
    vd = g(f"RES_Plant[{k}]/VD/0/1")[1]
    vq = g(f"RES_Plant[{k}]/VQ/0/1")[1]
    idk = g(f"RES_Plant[{k}]/ID/0/1")[1]
    iqk = g(f"RES_Plant[{k}]/IQ/0/1")[1]
    pw += (vd * idk + vq * iqk) * NBUS[k][1] * KPLANT
unt = np.zeros_like(t)
for i in range(1, 6):
    unt += g(f"SyncUnit[{i}]/POUT/0/1")[1] * MACH[i - 1]
pt = g("PTIE/0/1")[1]
print(f"\nplant fleet P  {pw[w].mean():8.0f} MW (last 0.5 s), range {pw.min():.0f}..{pw.max():.0f}")
print(f"unit total  P  {unt[w].mean():8.0f} MW (incl. France 200 GVA)")
print(f"PTIE           {pt[w].mean():+8.0f} MW (last 0.5 s), range {pt.min():+.0f}..{pt.max():+.0f}")
print("machine f (last 0.5 s): " + ", ".join(
    f"{g(f'SyncUnit[{i}]/Wspd/0/1')[1][w].mean()/2/np.pi:.3f}" for i in range(1, 6)))

# oscillation frequency of the bus-33 collector voltage, 0-6 Hz
v33 = np.mean([g(f"RES_Plant[{k}]/VDF/0/1")[1] for k in (1, 18)], axis=0)
seg = v33 - v33.mean()
n = len(seg)
win = np.hanning(n)
sp = np.abs(np.fft.rfft(seg * win))
fr = np.fft.rfftfreq(n, dt)
band = fr <= 6.0
k = np.argmax(sp[band])
print(f"V33 dominant oscillation: {fr[band][k]:.3f} Hz, peak amplitude "
      f"{2*sp[k]/np.sum(win):.4f} pu (whole run)")
seg2 = seg[w]
sp2 = np.abs(np.fft.rfft(seg2 * np.hanning(len(seg2))))
fr2 = np.fft.rfftfreq(len(seg2), dt)
b2 = (fr2 >= 0.2) & (fr2 <= 6.0)
print(f"V33 last 0.5 s: dominant {fr2[b2][np.argmax(sp2[b2])]:.3f} Hz, p-p {np.ptp(v33[w]):.4f} pu")
