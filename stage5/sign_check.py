"""G4a sensitivity sign check from one run that contains a Force step.

usage: python stage5\sign_check.py <psout> <outdir> --step 6.0 [--pre 5.7 6.0] [--post 6.15 6.6]

Prints, per bus, the VDF before and after the step, and per plant the TRIP time, so the check is
"the forced plant's bus goes UP" measured against its own pre-step value, with the plant that was
actually forced identified by its TRIP time (rule L2: identify by measurement, not by index).
Writes figures only into <outdir> (rule F1).
"""
import argparse
import os
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("psout")
    ap.add_argument("outdir")
    ap.add_argument("--step", type=float, default=6.0)
    ap.add_argument("--pre", nargs=2, type=float, default=None)
    ap.add_argument("--post", nargs=2, type=float, default=None)
    a = ap.parse_args()
    pre = a.pre or (a.step - 0.3, a.step - 0.02)
    post = a.post or (a.step + 0.15, a.step + 0.6)
    os.makedirs(a.outdir, exist_ok=True)

    f = mhi.psout.File(a.psout)
    r = f.run(0)

    def g(p):
        return np.asarray(r.call(p, sep="/").data, float)

    t = np.asarray(r.call("Root/Main/RES_Plant[1]/ID/0/1", sep="/").domain.data, float)
    wpre = (t >= pre[0]) & (t <= pre[1])
    wpost = (t >= post[0]) & (t <= post[1])
    print(f"{a.psout}\n  step at {a.step} s; pre {pre[0]}-{pre[1]}, post {post[0]}-{post[1]}")

    rows = []
    for k in sorted(NBUS):
        bus, sb = NBUS[k]
        v = g(f"Root/Main/RES_Plant[{k}]/VDF/0/1")
        p = g(f"Root/Main/RES_Plant[{k}]/ID/0/1")
        trip = g(f"Root/Main/RES_Plant[{k}]/TRIP/0/1")
        tt = t[np.argmax(trip > 0.5)] if np.any(trip > 0.5) else np.nan
        rows.append(dict(k=k, bus=bus, sb=sb, v0=v[wpre].mean(), v1=v[wpost].mean(),
                         p0=p[wpre].mean(), p1=p[wpost].mean(), tt=tt))

    forced = [x for x in rows if not np.isnan(x["tt"]) and abs(x["tt"] - a.step) < 0.5]
    print("\n  plants whose TRIP time is within 0.5 s of the step (these are the forced ones):")
    for x in forced:
        print(f"    [{x['k']}] bus {x['bus']} Sbase {x['sb']:.0f} at {x['tt']:.3f} s")
    if not forced:
        print("    NONE — the step did not force anything; the sign check cannot be read")

    print(f"\n{'bus':4} {'VDF pre':>8} {'VDF post':>9} {'dV [pu]':>8} {'dV [kV]':>8} {'id pre':>7} {'id post':>8}")
    for b in BUSES:
        g_ = [x for x in rows if x["bus"] == b]
        v0 = np.mean([x["v0"] for x in g_])
        v1 = np.mean([x["v1"] for x in g_])
        i0 = np.mean([x["p0"] for x in g_])
        i1 = np.mean([x["p1"] for x in g_])
        print(f"{b:4} {v0:8.4f} {v1:9.4f} {v1 - v0:+8.4f} {(v1 - v0) * 400:+8.1f} {i0:7.4f} {i1:8.4f}")

    print("\n  per forced plant:")
    for x in forced:
        print(f"    [{x['k']}] bus {x['bus']}: VDF {x['v0']:.4f} -> {x['v1']:.4f} "
              f"({(x['v1'] - x['v0']) * 400:+.1f} kV), id {x['p0']:.3f} -> {x['p1']:.3f}")

    fig, ax = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    for x in rows:
        ax[0].plot(t, g(f"Root/Main/RES_Plant[{x['k']}]/VDF/0/1"), lw=0.8,
                   label=f"[{x['k']}] bus {x['bus']}")
    ax[0].axvline(a.step, color="k", ls="--", lw=1)
    ax[0].set_ylabel("VDF [pu]")
    ax[0].set_title(f"G4a sign check — {os.path.basename(a.psout)}")
    ax[0].legend(fontsize=6, ncol=4)
    ax[0].grid(alpha=0.3)
    for x in rows:
        ax[1].plot(t, g(f"Root/Main/RES_Plant[{x['k']}]/TRIP/0/1"), lw=1.0,
                   label=f"[{x['k']}] {x['bus']}")
    ax[1].axvline(a.step, color="k", ls="--", lw=1)
    ax[1].set_ylabel("TRIP")
    ax[1].set_xlabel("t [s]")
    ax[1].legend(fontsize=6, ncol=4)
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(a.outdir, "04_sign_check.png"), dpi=120)
    plt.close(fig)
    print(f"\nfigure -> {os.path.join(a.outdir, '04_sign_check.png')}")
    f.close()


if __name__ == "__main__":
    main()
