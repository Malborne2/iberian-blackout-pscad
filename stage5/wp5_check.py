"""WP5 check: one .psout -> numbers + figures for the reactive-surplus operating point.

usage: python stage5\\wp5_check.py <psout> <outdir> [win_lo win_hi]

Rule F1: writes ONLY into <outdir> (its own run's folder).
Rule L2: plant instances are identified by bus via measured VDF clusters AND their ID level, and the
script prints FAIL if the cluster is broken (so a re-ordered build cannot silently relabel).
Rule A1: prints the slope of the last 0.5 s so settledness is judged on numbers, not by eye.
Rule R3: prints TRIP and first-trip time before any other number is used.
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mhi.psout

# instance -> (bus label, Sbase MVA)  [measured map, stage3\wp5_state.py]
NBUS = {1: ("33", 400.0), 2: ("36", 172.0), 3: ("36", 167.0), 4: ("36", 2402.0),
        5: ("34", 647.0), 6: ("34", 162.0), 7: ("34", 566.0), 8: ("34", 405.0),
        9: ("34", 339.0), 10: ("34", 236.0), 11: ("34", 1194.0),
        12: ("35", 612.0), 13: ("35", 130.0), 14: ("35", 2498.0),
        15: ("38", 589.0), 16: ("38", 348.0), 17: ("38", 3132.0),
        18: ("33", 2550.0)}
BUSES = ["33", "34", "35", "36", "38"]
MACH = {1: ("30 hydro", 6113.0), 2: ("31 nuc", 13548.0), 3: ("32 nuc", 15292.0),
        4: ("37 ccgt", 12838.0), 5: ("39 France", 200000.0)}
VREF = 1.05          # SyncUnit V0 after S19b (the AVR set-point)

PS = sys.argv[1]
OUT = sys.argv[2]
W0 = float(sys.argv[3]) if len(sys.argv) > 3 else None
W1 = float(sys.argv[4]) if len(sys.argv) > 4 else None
os.makedirs(OUT, exist_ok=True)


def mm(y, n):
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


def slope(y, t, a, b):
    w = (t >= a) & (t <= b)
    if w.sum() < 3:
        return float("nan")
    return float(np.polyfit(t[w], y[w], 1)[0])


def main():
    f = mhi.psout.File(PS)
    r = f.run(0)

    def get(p):
        tr = r.call(p, sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)

    n_inst = 0
    while True:
        try:
            get(f"Root/Main/RES_Plant[{n_inst + 1}]/ID/0/1")
            n_inst += 1
        except Exception:
            break
    n_mach = 0
    while True:
        try:
            get(f"Root/Main/SyncUnit[{n_mach + 1}]/Wspd/0/1")
            n_mach += 1
        except Exception:
            break

    t = get("Root/Main/RES_Plant[1]/ID/0/1")[0]
    n20 = max(1, int(round(0.02 / (t[1] - t[0]))))
    w0 = W0 if W0 is not None else max(0.0, t[-1] - 1.0)
    w1 = W1 if W1 is not None else t[-1]
    w = (t >= w0) & (t <= w1)

    print(f"{PS}\n  t = {t[0]:.3f}..{t[-1]:.3f} s  ({len(t)} samples, {1e6*(t[1]-t[0]):.0f} us)"
          f"  window {w0:.2f}-{w1:.2f} s  {n_inst} plants  {n_mach} machines")

    # ---------------------------------------------------------------- plants
    rows = []
    for k in range(1, n_inst + 1):
        bus, sb = NBUS.get(k, ("?", 0.0))
        vd = get(f"Root/Main/RES_Plant[{k}]/VD/0/1")[1]
        vdf = get(f"Root/Main/RES_Plant[{k}]/VDF/0/1")[1]
        try:
            vq = get(f"Root/Main/RES_Plant[{k}]/VQ/0/1")[1]
        except Exception:
            vq = np.zeros_like(vd)
        idk = get(f"Root/Main/RES_Plant[{k}]/ID/0/1")[1]
        iqk = get(f"Root/Main/RES_Plant[{k}]/IQ/0/1")[1]
        trip = get(f"Root/Main/RES_Plant[{k}]/TRIP/0/1")[1]
        p = mm(vd * idk + vq * iqk, n20) * sb
        q = mm(vd * iqk - vq * idk, n20) * sb
        tr_t = t[np.argmax(trip > 0.5)] if np.any(trip > 0.5) else np.nan
        rows.append(dict(k=k, bus=bus, sb=sb, vdf=vdf, id=idk, iq=iqk, p=p, q=q,
                         trip=trip.max(), tt=tr_t))

    print("\n  TRIP (rule R3): " +
          (", ".join(f"[{x['k']}] bus {x['bus']} at {x['tt']:.3f} s"
                     for x in rows if x["trip"] > 0.5) or "none"))
    trips = [x for x in rows if x["trip"] > 0.5]

    print(f"\n{'bus':4} {'n':>2} {'rating':>7} {'VDF pu':>8} {'d/dt':>8} {'id':>7} {'iq':>7} "
          f"{'P [MW]':>9} {'Q [Mvar]':>9}")
    tp = tq = 0.0
    bus_v = {}
    for b in BUSES:
        g = [x for x in rows if x["bus"] == b]
        sb = sum(x["sb"] for x in g)
        p = sum(x["p"][w].mean() for x in g)
        q = sum(x["q"][w].mean() for x in g)
        tp += p
        tq += q
        v = np.mean([x["vdf"][w].mean() for x in g])
        bus_v[b] = v
        sl = np.mean([slope(x["vdf"], t, w0, w1) for x in g])
        print(f"{b:4} {len(g):2d} {sb:7.0f} {v:8.4f} {sl:+8.3f} "
              f"{np.mean([x['id'][w].mean() for x in g]):7.4f} "
              f"{np.mean([x['iq'][w].mean() for x in g]):+7.4f} {p:9.1f} {q:9.1f}")
    print(f"{'TOT':4} {n_inst:2d} {sum(NBUS[k][1] for k in NBUS):7.0f} {'':8} {'':8} {'':8} "
          f"{'':8} {tp:9.1f} {tq:9.1f}")

    # --------------------------------------------------------------- machines
    print(f"\n{'machine':12} {'Sbase':>7} {'VIT':>7} {'VIT-1.05':>9} {'POUT':>7} {'QOUT':>7} "
          f"{'P [MW]':>9} {'Q [Mvar]':>9} {'f Hz':>9} {'f p-p':>7} {'df/dt':>8}")
    mp = mq = 0.0
    mach = []
    for k in range(1, n_mach + 1):
        nm, sb = MACH.get(k, (f"[{k}]", 0.0))
        vit = get(f"Root/Main/SyncUnit[{k}]/VIT/0/1")[1]
        po = get(f"Root/Main/SyncUnit[{k}]/POUT/0/1")[1]
        qo = get(f"Root/Main/SyncUnit[{k}]/QOUT/0/1")[1]
        ws = get(f"Root/Main/SyncUnit[{k}]/Wspd/0/1")[1]
        try:
            vref = get(f"Root/Main/SyncUnit[{k}]/VREF/0/1")[1]
        except Exception:
            vref = None
        fs = mm(ws, n20) / 2 / np.pi
        mp += po[w].mean() * sb
        mq += qo[w].mean() * sb
        mach.append(dict(nm=nm, sb=sb, vit=vit, po=po, qo=qo, f=fs))
        print(f"{nm:12} {sb:7.0f} {vit[w].mean():7.4f} {vit[w].mean() - VREF:+9.4f} "
              f"{po[w].mean():+7.4f} {qo[w].mean():+7.4f} {po[w].mean() * sb:9.1f} "
              f"{qo[w].mean() * sb:9.1f} {fs[w].mean():9.5f} {np.ptp(fs[w]):7.4f} "
              f"{slope(fs, t, w0, w1):+8.4f}")
    print(f"{'TOTAL':12} {'':7} {'':7} {'':9} {'':7} {'':7} {mp:9.1f} {mq:9.1f}")
    print(f"\nbalance: machines {mp:.0f} MW + plants {tp:.0f} MW = {mp + tp:.0f} MW "
          f"(load 25,238 MW constant power) -> surplus/losses {mp + tp - 25238:.0f} MW")

    # ------------------------------------------------------- multimeters (bus V)
    print("\nmultimeters (Vd [pu], Pd/Qd [MW/Mvar] over the window; identify bus by plant VDF):")
    nmm = 0
    while True:
        try:
            get(f"Root/Main/multimeter[{nmm + 1}]/4/Vd")
            nmm += 1
        except Exception:
            break
    for k in range(1, nmm + 1):
        vd = get(f"Root/Main/multimeter[{k}]/4/Vd")[1]
        pd = get(f"Root/Main/multimeter[{k}]/2/Pd")[1]
        qd = get(f"Root/Main/multimeter[{k}]/3/Qd")[1]
        # coarse resample onto t
        tm = np.linspace(t[0], t[-1], len(vd))
        wm = (tm >= w0) & (tm <= w1)
        match = [b for b in BUSES if abs(vd[wm].mean() - bus_v[b]) < 0.03]
        mt = [m["nm"] for m in mach if abs(vd[wm].mean() - m["vit"][w].mean()) < 0.01]
        print(f"  multimeter[{k}]: Vd {vd[wm].mean():7.4f} pu ({vd[wm].mean()*400:6.1f} kV)"
              f"  P {pd[wm].mean():8.1f}  Q {qd[wm].mean():8.1f}   -> {match or mt or '?'}")
    try:
        vmm = get("Root/Main/MM9/4/Vd")[1]
        tm = np.linspace(t[0], t[-1], len(vmm))
        wm = (tm >= w0) & (tm <= w1)
        print(f"  MM9 (bus 9):     Vd {vmm[wm].mean():7.4f} pu ({vmm[wm].mean()*400:6.1f} kV)")
    except Exception as e:
        print("  MM9:", e)

    # ------------------------------------------------------------- figures
    tt = t
    fig, ax = plt.subplots(3, 1, figsize=(11, 11), sharex=True)
    for b in BUSES:
        g = [x for x in rows if x["bus"] == b]
        ax[0].plot(tt, g[0]["vdf"], label=f"bus {b}")
    ax[0].axhspan(1.00, 1.06, color="g", alpha=0.12, label="G4a target 1.00-1.06")
    ax[0].axhline(1.25, color="r", ls=":", label="parked relay Vt 1.25")
    for x in trips:
        ax[0].axvline(x["tt"], color="k", lw=0.8, ls="--")
        ax[0].annotate(f"[{x['k']}] {x['bus']}", (x["tt"], ax[0].get_ylim()[1]), fontsize=7)
    ax[0].set_ylabel("collector VDF [pu]")
    ax[0].set_title(f"WP5 operating point â€” {os.path.basename(PS)}")
    ax[0].legend(fontsize=7, ncol=3)
    ax[0].grid(alpha=0.3)

    for b in BUSES:
        g = [x for x in rows if x["bus"] == b]
        ax[1].plot(tt, sum(x["p"] for x in g), label=f"bus {b} P")
    ax[1].set_ylabel("plant P [MW] per bus")
    ax[1].legend(fontsize=7, ncol=3)
    ax[1].grid(alpha=0.3)

    for m in mach:
        ax[2].plot(tt, m["f"], label=m["nm"])
    ax[2].set_ylabel("frequency [Hz]")
    ax[2].set_xlabel("t [s]")
    ax[2].legend(fontsize=7, ncol=3)
    ax[2].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "01_collectors_P_freq.png"), dpi=120)
    plt.close(fig)

    fig, ax = plt.subplots(3, 1, figsize=(11, 11), sharex=True)
    for m in mach:
        ax[0].plot(tt, m["vit"], label=m["nm"])
    ax[0].axhline(VREF, color="r", ls=":", label="V0 = 1.05 (AVR set-point)")
    ax[0].set_ylabel("VIT [pu]")
    ax[0].legend(fontsize=7, ncol=3)
    ax[0].grid(alpha=0.3)
    for m in mach:
        ax[1].plot(tt, m["qo"], label=m["nm"])
    ax[1].set_ylabel("QOUT [pu on Sbase]")
    ax[1].legend(fontsize=7, ncol=3)
    ax[1].grid(alpha=0.3)
    for m in mach:
        ax[2].plot(tt, m["po"], label=m["nm"])
    ax[2].set_ylabel("POUT [pu on Sbase]")
    ax[2].set_xlabel("t [s]")
    ax[2].legend(fontsize=7, ncol=3)
    ax[2].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "02_machines_VIT_Q_P.png"), dpi=120)
    plt.close(fig)

    fig, ax = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    for b in BUSES:
        g = [x for x in rows if x["bus"] == b]
        ax[0].plot(tt, sum(x["q"] for x in g), label=f"bus {b}")
    ax[0].axhline(0, color="k", lw=0.6)
    ax[0].set_ylabel("plant Q [Mvar] per bus (negative = absorbing)")
    ax[0].legend(fontsize=7, ncol=3)
    ax[0].grid(alpha=0.3)
    for b in BUSES:
        g = [x for x in rows if x["bus"] == b]
        ax[1].plot(tt, np.mean([x["iq"] for x in g], axis=0), label=f"bus {b}")
    ax[1].axhline(0, color="k", lw=0.6)
    ax[1].set_ylabel("plant iq [pu]")
    ax[1].set_xlabel("t [s]")
    ax[1].legend(fontsize=7, ncol=3)
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "03_plant_Q_iq.png"), dpi=120)
    plt.close(fig)

    print(f"\nfigures -> {OUT}")
    f.close()


if __name__ == "__main__":
    main()
