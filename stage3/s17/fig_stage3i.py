"""Figure set for Stage 3i: first converter plants in the network (Session 17).

Run: C:\\PSCAD_work\\iberia4 (copy stage3\\s17\\iberia4_b33.pscx), 20 s at 5 us.
Bus 33's ideal source replaced by two RES_Plant instances on one 800 kV rail:
  RES_Plant[1] = bulk-33, 2550 MVA, Pref ramp 0 -> 0.890 (0.1-0.6 s), CarrPh 90
  RES_Plant[2] = Granada, 400 MVA, Pref ramp 0 -> 0.8875,               CarrPh 0
SyncUnit[n] order is PSCAD's; each row prints VIT so the bus can be checked (G2b table).
usage: python fig_stage3i.py <psout>
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mhi.psout

PS = sys.argv[1]
OUT = Path(__file__).resolve().parents[2] / "results" / "stage3i_network_b33"
OUT.mkdir(parents=True, exist_ok=True)
SB = {1: 2550.0, 2: 400.0}
NAME = {1: "bulk-33 (2550 MVA)", 2: "Granada (400 MVA)"}


def mm(y, n):
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


def get(r, p):
    tr = r.call(p, sep="/")
    return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)


pl, su = {}, {}
with mhi.psout.File(PS) as f:
    r = f.run(0)
    for k in (1, 2):
        for c in ("VD", "VQ", "ID", "IQ", "VDF", "TRIP", "THETA_TR"):
            t, pl[(k, c)] = get(r, f"Root/Main/RES_Plant[{k}]/{c}/0/1")
    for k in range(1, 6):
        for c in ("VIT", "POUT", "QOUT", "Wspd"):
            try:
                ts, su[(k, c)] = get(r, f"Root/Main/SyncUnit[{k}]/{c}/0/1")
            except Exception:
                pass
n20 = int(round(0.02 / (t[1] - t[0])))
n20s = int(round(0.02 / (ts[1] - ts[0])))
P = {k: mm(pl[(k, "VD")] * pl[(k, "ID")] + pl[(k, "VQ")] * pl[(k, "IQ")], n20) * SB[k] for k in (1, 2)}
Q = {k: mm(pl[(k, "VD")] * pl[(k, "IQ")] - pl[(k, "VQ")] * pl[(k, "ID")], n20) * SB[k] for k in (1, 2)}
F = {k: mm(np.gradient(np.unwrap(pl[(k, "THETA_TR")]), t) / (2 * np.pi), n20) for k in (1, 2)}

fig, ax = plt.subplots(2, 2, figsize=(14, 8), sharex=True)
for k in (1, 2):
    ax[0, 0].plot(t, pl[(k, "VDF")], lw=0.7, label=f"bus 33 seen by {NAME[k]}")
for k in range(1, 6):
    if (k, "VIT") in su:
        ax[0, 0].plot(ts, su[(k, "VIT")], lw=0.7, label=f"SyncUnit[{k}] VIT")
ax[0, 0].set_ylabel("V [pu]"); ax[0, 0].set_title("Voltages"); ax[0, 0].set_ylim(0.85, 1.12)
for k in (1, 2):
    ax[0, 1].plot(t, P[k], lw=0.7, label=NAME[k])
ax[0, 1].set_ylabel("P [MW]"); ax[0, 1].set_title("Plant active power (20 ms mean)")
for k in (1, 2):
    ax[1, 0].plot(t, Q[k], lw=0.7, label=NAME[k])
ax[1, 0].set_ylabel("Q [Mvar] (+ = injection)"); ax[1, 0].set_title("Plant reactive power: fixed PF absorbing")
for k in (1, 2):
    ax[1, 1].plot(t, F[k], lw=0.7, label=f"PLL {NAME[k]}")
for k in range(1, 6):
    if (k, "Wspd") in su:
        ax[1, 1].plot(ts, mm(su[(k, "Wspd")], n20s) / (2 * np.pi), lw=0.7, label=f"SyncUnit[{k}]")
ax[1, 1].set_ylabel("f [Hz]"); ax[1, 1].set_title("Frequency"); ax[1, 1].set_ylim(49.8, 50.2)
for a in ax.flat:
    a.grid(alpha=0.3); a.legend(fontsize=6)
for a in ax[-1]:
    a.set_xlabel("t [s]")
fig.suptitle("Stage 3i - bus 33 ideal source replaced by two switching plants on one rail (20 s)")
fig.tight_layout(); fig.savefig(OUT / "00_overview.png", dpi=110)
for i, nm in enumerate(("01_voltage", "02_active_power", "03_reactive_power", "04_frequency")):
    a = ax.flat[i]
    f2, b = plt.subplots(figsize=(11, 4))
    for line in a.get_lines():
        b.plot(*line.get_data(), lw=0.7, label=line.get_label())
    b.set_ylim(a.get_ylim()); b.set_title(a.get_title()); b.set_ylabel(a.get_ylabel()); b.set_xlabel("t [s]")
    b.grid(alpha=0.3); b.legend(fontsize=7); f2.tight_layout(); f2.savefig(OUT / f"{nm}.png", dpi=110); plt.close(f2)

w = lambda tt, lo, hi: (tt >= lo) & (tt <= hi)
for k in (1, 2):
    a, b = w(t, 5, 6), w(t, 19, 20)
    print(f"{NAME[k]:20s} P {P[k][a].mean():8.1f} -> {P[k][b].mean():8.1f} MW | Q {Q[k][a].mean():7.1f} -> {Q[k][b].mean():7.1f} Mvar"
          f" | V {pl[(k,'VDF')][a].mean():.4f} -> {pl[(k,'VDF')][b].mean():.4f} | f {F[k][b].mean():.4f} Hz | TRIP {pl[(k,'TRIP')].max():.0f}")
for k in range(1, 6):
    if (k, "VIT") in su:
        a, b = w(ts, 5, 6), w(ts, 19, 20)
        ws = su[(k, "Wspd")]
        print(f"SyncUnit[{k}] VIT {su[(k,'VIT')][a].mean():.4f} -> {su[(k,'VIT')][b].mean():.4f} | POUT {su[(k,'POUT')][a].mean():.4f}"
              f" -> {su[(k,'POUT')][b].mean():.4f} | f {ws[b].mean()/2/np.pi:.4f} Hz, f p-p 15-20 s {np.ptp(mm(ws, n20s)[w(ts,15,20)])/2/np.pi*1000:.1f} mHz")
print("written", OUT)
