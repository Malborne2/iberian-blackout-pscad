"""Figure set for a WP3 bus (rule F1: one folder per run).

usage: python stage3\\fig_wp3.py <psout> <bus> <outdir> <name:Sbase[,name:Sbase...]>

Panels: plant P, plant Q, bus voltage, machine frequency, plant id/iq, plant TRIP.
Plants of <bus> are identified by their VDF (rule L2); the Sbase pairing is the same as
stage3\\wp3_report.py (largest P <-> largest Sbase).
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mhi.psout

PS, BUS, OUT = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
SPEC = sys.argv[4] if len(sys.argv) > 4 else ""
VDF_HINT = float(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5] != "-" else None
PLANTS = [(x.split(":")[0].strip(), float(x.split(":")[1])) for x in SPEC.split(",") if x.strip()]
OUT.mkdir(parents=True, exist_ok=True)


def mm(y, n):
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


with mhi.psout.File(PS) as f:
    r = f.run(0)

    def get(p):
        tr = r.call(p, sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)

    n = 0
    while True:
        try:
            get(f"Root/Main/RES_Plant[{n + 1}]/ID/0/1")
            n += 1
        except Exception:
            break
    D = {}
    for k in range(1, n + 1):
        for c in ("ID", "IQ", "VD", "VQ", "VDF", "TRIP"):
            try:
                D[(k, c)] = get(f"Root/Main/RES_Plant[{k}]/{c}/0/1")
            except Exception:
                pass
    t = D[(1, "ID")][0]
    n20 = int(round(0.02 / (t[1] - t[0])))
    vdf = {k: D[(k, "VDF")][1] for k in range(1, n + 1) if (k, "VDF") in D}
    vals = np.array([round(vdf[k].mean(), 4) for k in vdf])
    uniq, cnt = np.unique(vals, return_counts=True)
    if VDF_HINT is not None:
        group = float(min(uniq, key=lambda v: abs(v - VDF_HINT)))
    else:
        # no hint: the bus is the group with as many members as the caller's plant list
        cand = [v for v, c in zip(uniq, cnt) if c == len(PLANTS)]
        group = float(cand[0]) if cand else float(uniq[np.argmax(cnt)])
    mine = [k for k in vdf if abs(round(vdf[k].mean(), 4) - group) < 1e-4]

    P, Q, ID, IQ = {}, {}, {}, {}
    for k in mine:
        vd, vq = D[(k, "VD")][1], D[(k, "VQ")][1]
        idc, iq = D[(k, "ID")][1], D[(k, "IQ")][1]
        P[k] = mm(vd * idc + vq * iq, n20)
        Q[k] = mm(vd * iq - vq * idc, n20)
        ID[k], IQ[k] = idc, iq

fig, ax = plt.subplots(3, 2, figsize=(14, 10), sharex=True)
order = sorted(mine, key=lambda k: -P[k].mean())
spec = sorted(PLANTS, key=lambda s: -s[1])
names = {k: (spec[i][0], spec[i][1]) if i < len(spec) else (f"inst{k}", 1.0) for i, k in enumerate(order)}

for k in mine:
    nm, sb = names[k]
    ax[0, 0].plot(t, P[k] * sb, lw=0.8, label=f"{nm} ({sb:.0f} MVA)")
    ax[0, 1].plot(t, Q[k] * sb, lw=0.8, label=f"{nm}")
    ax[1, 0].plot(t, vdf[k], lw=0.8, label=f"{nm}")
    ax[1, 1].plot(t, ID[k], lw=0.6, label=f"{nm} id")
    ax[1, 1].plot(t, IQ[k], lw=0.6, ls="--", label=f"{nm} iq")
    if (k, "TRIP") in D:
        ax[2, 1].plot(D[(k, "TRIP")][0], D[(k, "TRIP")][1], lw=1.0, label=f"{nm}")
ax[0, 0].set_ylabel("P [MW]"); ax[0, 0].set_title(f"Plant active power, bus {BUS}")
ax[0, 1].set_ylabel("Q [Mvar] (+ = injection)"); ax[0, 1].set_title("Plant reactive power (absorbing)")
ax[1, 0].set_ylabel("V [pu]"); ax[1, 0].set_title("Bus voltage at the plants (VDF)")
ax[1, 1].set_ylabel("current [pu]"); ax[1, 1].set_title("Plant id (solid) and iq (dashed)")
ax[2, 1].set_ylabel("TRIP"); ax[2, 1].set_title("Trip flags"); ax[2, 1].set_ylim(-0.1, 1.2)

for k in range(1, 6):
    try:
        ts, ws = get(f"Root/Main/SyncUnit[{k}]/Wspd/0/1")
        f_ = mm(ws, int(round(0.02 / (ts[1] - ts[0])))) / 2 / np.pi
        ax[2, 0].plot(ts, f_, lw=0.8, label=f"unit {k}")
        ax[0, 0].plot([], [], " ", label="")
    except Exception:
        pass
ax[2, 0].set_ylabel("f [Hz]"); ax[2, 0].set_title("Machine frequency"); ax[2, 0].set_ylim(49.8, 50.2)
for a in ax.flat:
    a.grid(alpha=0.3); a.legend(fontsize=6); a.set_xlabel("t [s]")
fig.suptitle(f"WP3 / G3b — bus {BUS}: {len(mine)} plants replacing the ideal source  ({Path(PS).name})")
fig.tight_layout()
fig.savefig(OUT / "00_overview.png", dpi=110)

panels = [(0, "01_active_power"), (1, "02_reactive_power"), (2, "03_bus_voltage"),
          (3, "04_plant_currents"), (4, "05_frequency"), (5, "06_trip_flags")]
for i, nm in panels:
    a = ax.flat[i]
    f2, b = plt.subplots(figsize=(11, 4))
    for line in a.get_lines():
        b.plot(*line.get_data(), lw=0.7, label=line.get_label())
    b.set_ylim(a.get_ylim()); b.set_title(a.get_title()); b.set_ylabel(a.get_ylabel())
    b.set_xlabel("t [s]"); b.grid(alpha=0.3); b.legend(fontsize=7)
    f2.tight_layout(); f2.savefig(OUT / f"{nm}.png", dpi=110)
    plt.close(f2)

print(f"bus {BUS}: {len(mine)} plants (instances {sorted(mine)}), figures in {OUT}")
for k in mine:
    nm, sb = names[k]
    print(f"  {nm:10} P {P[k].mean() * sb:8.1f} MW  Q {Q[k].mean() * sb:8.1f} Mvar  VDF {vdf[k].mean():.4f}")
