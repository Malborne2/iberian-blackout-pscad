r"""Start-up diagnostic figure: bus voltages, plant power per bus, machine speeds, tie, first N seconds.

usage: python stage11\startup_fig.py <psout> <outdir> [t_end]
Writes <outdir>\startup.png (rule F1: only into <outdir>).
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mhi.psout
import numpy as np

KPLANT = 1.30
NBUS = {1: ("33", 400.0), 2: ("36", 172.0), 3: ("36", 167.0), 4: ("36", 2402.0),
        5: ("34", 647.0), 6: ("34", 162.0), 7: ("34", 566.0), 8: ("34", 405.0),
        9: ("34", 339.0), 10: ("34", 236.0), 11: ("34", 1194.0),
        12: ("35", 612.0), 13: ("35", 130.0), 14: ("35", 2498.0),
        15: ("38", 589.0), 16: ("38", 348.0), 17: ("38", 3132.0), 18: ("33", 2550.0)}
BUSES = ["33", "34", "35", "36", "38"]
MACH = [("30", 6113.0), ("31", 13548.0), ("32", 15292.0), ("37", 12838.0), ("39F", 200000.0)]

ps, out = sys.argv[1], sys.argv[2]
tend = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
os.makedirs(out, exist_ok=True)
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
n20 = max(1, int(round(0.02 / (t[1] - t[0]))))
w = t <= tend

fig, ax = plt.subplots(4, 1, figsize=(12, 12), sharex=True)
for b in BUSES:
    ks = [k for k, (bb, s) in NBUS.items() if bb == b]
    v = np.mean([get(f"Root/Main/RES_Plant[{k}]/VDF/0/1")[1] for k in ks], axis=0)
    ax[0].plot(t[w], v[w], lw=1.0, label=f"bus {b}")
ax[0].set(ylabel="collector VDF [pu]")
ax[0].legend(ncol=5, fontsize=7)
ax[0].grid(alpha=0.3)

for b in BUSES:
    ks = [k for k, (bb, s) in NBUS.items() if bb == b]
    p = np.zeros_like(t)
    for k in ks:
        vd = get(f"Root/Main/RES_Plant[{k}]/VD/0/1")[1]
        vq = get(f"Root/Main/RES_Plant[{k}]/VQ/0/1")[1]
        idk = get(f"Root/Main/RES_Plant[{k}]/ID/0/1")[1]
        iqk = get(f"Root/Main/RES_Plant[{k}]/IQ/0/1")[1]
        p += mm(vd * idk + vq * iqk, n20) * NBUS[k][1] * KPLANT
    ax[1].plot(t[w], p[w], lw=1.0, label=f"bus {b} ({sum(NBUS[k][1] for k in ks)*KPLANT:.0f} MVA)")
ax[1].axhline(0, color="k", lw=0.5)
ax[1].set(ylabel="plant P [MW]")
ax[1].legend(ncol=5, fontsize=7)
ax[1].grid(alpha=0.3)

for i in range(1, 6):
    fs = mm(get(f"Root/Main/SyncUnit[{i}]/Wspd/0/1")[1], n20) / 2 / np.pi
    ax[2].plot(t[w], fs[w], lw=1.0, label=MACH[i - 1][0])
ax[2].set(ylabel="f [Hz]")
ax[2].legend(ncol=5, fontsize=7)
ax[2].grid(alpha=0.3)

ax[3].plot(t[w], mm(get("Root/Main/PTIE/0/1")[1], n20)[w], lw=1.0, label="PTIE [MW]")
hv = {c: get(f"Root/Main/HVDC_T/{c}/0/1")[1] for c in ("ID", "IQ", "VD", "VQ")}
hp = mm(hv["VD"] * hv["ID"] + hv["VQ"] * hv["IQ"], n20) * 1000.0
ax[3].plot(t[w], -hp[w], lw=1.0, label="-HVDC P [MW]")
ax[3].set(xlabel="time [s]", ylabel="MW")
ax[3].legend(fontsize=8)
ax[3].grid(alpha=0.3)

fig.suptitle(os.path.basename(ps) + f"  first {tend:g} s")
fig.tight_layout()
fig.savefig(os.path.join(out, "startup.png"), dpi=130)
print("wrote", os.path.join(out, "startup.png"))
