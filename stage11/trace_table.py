r"""Diagnostic trace table for one ib5 run: machines, tie, HVDC, generation, at a coarse time step.

usage: python stage11\\trace_table.py <psout> [t0 t1 step] [--out file.txt]

Prints, at each sample time: the five machine speeds (Hz), the total Iberian unit power (MW),
the plant fleet power (MW), PTIE (MW), HVDC P (MW), the two tie angles (deg) and the collector
VDF of bus 33.  Whole-point values (no window mean) so a slip is visible (PLAN.md 2c C1/C4).
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
SB = [m[1] * KPLANT for m in NBUS.values()]
MACH = [("30", 6113.0), ("31", 13548.0), ("32", 15292.0), ("37", 12838.0), ("39F", 200000.0)]

ps = sys.argv[1]
t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.4
t1 = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
step = float(sys.argv[4]) if len(sys.argv) > 4 else 0.05

f = mhi.psout.File(ps)
r = f.run(0)


def get(p):
    tr = r.call(p, sep="/")
    return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)


def mm(y, n):
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


t, _ = get("Root/Main/SyncUnit[1]/Wspd/0/1")
dt = t[1] - t[0]
n20 = max(1, int(round(0.02 / dt)))
fr = {i: mm(get(f"Root/Main/SyncUnit[{i}]/Wspd/0/1")[1], n20) / 2 / np.pi for i in range(1, 6)}
po = {i: mm(get(f"Root/Main/SyncUnit[{i}]/POUT/0/1")[1], n20) for i in range(1, 6)}
pt = mm(get("Root/Main/PTIE/0/1")[1], n20)
ph9 = get("Root/Main/Ph9/0/1")[1]
ph39 = get("Root/Main/Ph39/0/1")[1]
hv = {c: get(f"Root/Main/HVDC_T/{c}/0/1")[1] for c in ("ID", "IQ", "VD", "VQ")}
hp = mm(hv["VD"] * hv["ID"] + hv["VQ"] * hv["IQ"], n20)
plants_p = np.zeros_like(t)
for k in range(1, 19):
    vd = get(f"Root/Main/RES_Plant[{k}]/VD/0/1")[1]
    vq = get(f"Root/Main/RES_Plant[{k}]/VQ/0/1")[1]
    idk = get(f"Root/Main/RES_Plant[{k}]/ID/0/1")[1]
    iqk = get(f"Root/Main/RES_Plant[{k}]/IQ/0/1")[1]
    plants_p += (vd * idk + vq * iqk) * SB[k - 1]
v33 = np.mean([get(f"Root/Main/RES_Plant[{k}]/VDF/0/1")[1] for k in (1, 18)], axis=0)

print(f"# {ps}\nt {t[0]:.3f}..{t[-1]:.3f}  step {step}")
hdr = (f"{'t':>6} | " + " ".join(f"{MACH[i][0]:>6}" for i in range(5)) +
       f" | {'untot':>7} {'plant':>7} {'PTIE':>7} {'HVDC':>7} | {'Ph9':>7} {'Ph39':>8} {'dV33':>6}")
print(hdr)
rows = []
for tt in np.arange(t0, min(t1, t[-1]) + 1e-9, step):
    i = int(np.argmin(np.abs(t - tt)))
    untot = sum(po[k][i] * MACH[k - 1][1] for k in range(1, 5))
    line = (f"{t[i]:6.3f} | " + " ".join(f"{fr[k][i]:6.3f}" for k in range(1, 6)) +
            f" | {untot:7.0f} {plants_p[i]:7.0f} {pt[i]:7.0f} {-hp[i]:7.0f} | "
            f"{ph9[i]:7.2f} {ph39[i]:8.2f} {v33[i]:6.3f}")
    print(line)
    rows.append(line)
if len(sys.argv) > 5 and sys.argv[5] == "--out":
    with open(sys.argv[6], "w", encoding="utf-8") as fh:
        fh.write(hdr + "\n" + "\n".join(rows) + "\n")
