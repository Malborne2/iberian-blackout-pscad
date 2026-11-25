"""WP5 (Session 19b) figure set + numbers from one run's own .psout.

usage: python stage5\\fig_wp5.py <psout> <out_dir>

Writes only into <out_dir> (rule F1: a figure script writes to its own run's folder) and prints the
numbers the figures show, so figures and text come from the same pass over the same file:

  00_bus_voltages.png   five collector-bus voltages (plant VDF) + five machine terminal voltages (VIT)
  01_machine_q.png      the five machines' Q [Mvar] -- the independent meter for the AVR (rule M3)
  02_plant_p.png        plant active power summed per collector bus
  03_frequency.png      the five machine frequencies, 25 mHz smoothing

Bus/instrance map: stage3\\wp5_state.py (measured, S19b).
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mhi.psout

NBUS = {1: ("33", 400.0), 2: ("36", 172.0), 3: ("36", 167.0), 4: ("36", 2402.0),
        5: ("34", 647.0), 6: ("34", 162.0), 7: ("34", 566.0), 8: ("34", 405.0),
        9: ("34", 339.0), 10: ("34", 236.0), 11: ("34", 1194.0),
        12: ("35", 612.0), 13: ("35", 130.0), 14: ("35", 2498.0),
        15: ("38", 589.0), 16: ("38", 348.0), 17: ("38", 3132.0),
        18: ("33", 2550.0)}
BUSES = ["33", "34", "35", "36", "38"]
MACH_SBASE = {1: 6113.0, 2: 13548.0, 3: 15292.0, 4: 12838.0, 5: 200000.0}

PS, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)


def mm(y, n):
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


with mhi.psout.File(PS) as f:
    r = f.run(0)

    def get(p):
        tr = r.call(p, sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)

    t = get("Root/Main/RES_Plant[1]/VDF/0/1")[0]
    dt = t[1] - t[0]
    n20 = int(round(0.02 / dt))
    n25 = int(round(0.025 / dt))
    w = t >= max(0.0, t[-1] - 1.0)

    fig, ax = plt.subplots(figsize=(10, 5))
    vdf = {}
    for b in BUSES:
        ks = [k for k in NBUS if NBUS[k][0] == b]
        y = np.mean([get(f"Root/Main/RES_Plant[{k}]/VDF/0/1")[1] for k in ks], axis=0)
        vdf[b] = y
        ax.plot(t, y, label=f"bus {b}")
        print(f"bus {b}: V {y[w].mean():.4f} pu at {t[w][0]:.2f}-{t[w][-1]:.2f} s "
              f"(min {y.min():.4f}, max {y.max():.4f})")
    for k in range(1, 6):
        vit = get(f"Root/Main/SyncUnit[{k}]/VIT/0/1")[1]
        ax.plot(t, vit, "--", lw=1, label=f"machine {k} VIT")
        print(f"machine {k}: VIT {vit[w].mean():.4f} pu")
    ax.axhline(1.0, color="0.6", lw=0.8)
    ax.set(xlabel="t [s]", ylabel="voltage [pu]", title="Collector-bus and machine terminal voltages")
    ax.grid(alpha=0.3); ax.legend(ncol=2, fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "00_bus_voltages.png"), dpi=130); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    q = {}
    for k in range(1, 6):
        q[k] = get(f"Root/Main/SyncUnit[{k}]/QOUT/0/1")[1] * MACH_SBASE[k]
        ax.plot(t, q[k], label=f"machine {k}")
        print(f"machine {k}: Q {q[k][w].mean():+8.1f} Mvar (P "
              f"{get(f'Root/Main/SyncUnit[{k}]/POUT/0/1')[1][w].mean() * MACH_SBASE[k]:+8.1f} MW)")
    tot = sum(q.values())
    print(f"machines total Q at {t[w][0]:.2f}-{t[w][-1]:.2f} s: {tot[w].mean():+.1f} Mvar")
    ax.axhline(0, color="0.6", lw=0.8)
    ax.set(xlabel="t [s]", ylabel="Q [Mvar]", title="Machine reactive output (the AVR's own meter)")
    ax.grid(alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "01_machine_q.png"), dpi=130); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    for b in BUSES:
        ks = [k for k in NBUS if NBUS[k][0] == b]
        p = np.zeros_like(t)
        for k in ks:
            vd = get(f"Root/Main/RES_Plant[{k}]/VD/0/1")[1]
            idk = get(f"Root/Main/RES_Plant[{k}]/ID/0/1")[1]
            try:
                vq = get(f"Root/Main/RES_Plant[{k}]/VQ/0/1")[1]
                iqk = get(f"Root/Main/RES_Plant[{k}]/IQ/0/1")[1]
            except Exception:
                vq = np.zeros_like(vd); iqk = np.zeros_like(vd)
            p += mm(vd * idk + vq * iqk, n20) * NBUS[k][1]
        ax.plot(t, p, label=f"bus {b}")
        print(f"bus {b}: plants {p[w].mean():+8.1f} MW at {t[w][0]:.2f}-{t[w][-1]:.2f} s")
        if b == BUSES[0]:
            tot_p = np.zeros_like(p)
        tot_p += p
    print(f"plants total: {tot_p[w].mean():+.1f} MW  (rating 16,549 MVA)")
    ax.set(xlabel="t [s]", ylabel="P [MW]", title="Plant active power per collector bus")
    ax.grid(alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "02_plant_p.png"), dpi=130); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    for k in range(1, 6):
        fs = mm(get(f"Root/Main/SyncUnit[{k}]/Wspd/0/1")[1], n25) / 2 / np.pi
        ax.plot(t, fs, label=f"machine {k}")
        print(f"machine {k}: f {fs[w].mean():.5f} Hz, p-p {np.ptp(fs[w]) * 1000:.1f} mHz")
    ax.axhline(50.0, color="0.6", lw=0.8)
    ax.set(xlabel="t [s]", ylabel="frequency [Hz]", title="Machine frequencies")
    ax.grid(alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_frequency.png"), dpi=130); plt.close(fig)

print("figures ->", OUT)
