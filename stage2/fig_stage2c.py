"""Figure set for Stage 2c (WP1): SyncUnit with droop governor (Session 17).

bench  : C:\\PSCAD_work\\su2 (copy stage2\\su2_governor_island.pscx): island, two SyncUnits, base load
         132.6 MW, +13.3 MW switched in at 10 s.  Unit with Pmec 0.2 has Kgov 20 / Tgov 2 s, the
         Pmec 0.25 unit Kgov 0.  Units are identified by POUT (rule L2), not by [n].
network: C:\\PSCAD_work\\iberia4 with governors (40 s) vs the Session-17 run without (20 s).
usage: python fig_stage2c.py bench <psout> | network <psout_gov> <psout_nogov>
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mhi.psout

OUT = Path(__file__).resolve().parents[1] / "results"


def mm(y, n):
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


def load(ps, names, n_units):
    d = {}
    with mhi.psout.File(ps) as f:
        r = f.run(0)
        for k in range(1, n_units + 1):
            for c in names:
                try:
                    tr = r.call(f"Root/Main/SyncUnit[{k}]/{c}/0/1", sep="/")
                    d["t"] = np.asarray(tr.domain.data, float)
                    d[(k, c)] = np.asarray(tr.data, float)
                except Exception:
                    pass
        try:
            d["PBRK"] = np.asarray(r.call("Root/Main/PBRK/0/1", sep="/").data, float)
        except Exception:
            pass
    return d


def bench(ps):
    out = OUT / "stage2c_governor_bench"; out.mkdir(parents=True, exist_ok=True)
    d = load(ps, ("Wspd", "POUT", "QOUT", "VIT", "DPGOV", "TMECH"), 2)
    t = d["t"]; n = int(round(0.02 / (t[1] - t[0])))
    gov = 1 if abs(d[(1, "POUT")][t < 9].mean() - 0.2) < abs(d[(2, "POUT")][t < 9].mean() - 0.2) else 2
    lab = {gov: "unit A: Kgov 20, Tgov 2 s (Pmec 0.2)", 3 - gov: "unit B: Kgov 0 (Pmec 0.25)"}
    fig, ax = plt.subplots(2, 2, figsize=(14, 8), sharex=True)
    for k in (1, 2):
        ax[0, 0].plot(t, d[(k, "VIT")], lw=0.8, label=lab[k])
        ax[0, 1].plot(t, mm(d[(k, "POUT")], n) * 300, lw=0.8, label=lab[k])
        ax[1, 0].plot(t, mm(d[(k, "QOUT")], n) * 300, lw=0.8, label=lab[k])
    ax[0, 1].plot(t, -d["PBRK"], "k--", lw=0.8, label="switched load (breaker P)")
    f = d[(1, "Wspd")] / 2 / np.pi
    ax[1, 1].plot(t, f, lw=0.9, label="island frequency")
    pre, post = (t > 7) & (t < 10), (t > 22) & (t < 25)
    dP = (d[(gov, "DPGOV")][post].mean() - d[(gov, "DPGOV")][pre].mean())
    f0, f1 = f[pre].mean(), f[post].mean()
    ax[1, 1].axhline(f0 - dP / 20 * 50, color="r", ls="--", lw=0.8, label="expected f0 - dP_gov/Kgov x 50")
    for a, yl, ti in ((ax[0, 0], "V [pu]", "Terminal voltage"), (ax[0, 1], "P [MW]", "Active power (20 ms mean)"),
                      (ax[1, 0], "Q [Mvar]", "Reactive power"), (ax[1, 1], "f [Hz]", "Frequency")):
        a.set_ylabel(yl); a.set_title(ti); a.grid(alpha=.3); a.legend(fontsize=7); a.axvline(10, color="0.6", lw=0.6)
    ax[0, 0].set_ylim(0.95, 1.05)
    for a in ax[-1]:
        a.set_xlabel("t [s]")
    fig.suptitle("Stage 2c - SyncUnit droop governor, island bench, +13.3 MW load step at 10 s")
    fig.tight_layout(); fig.savefig(out / "00_overview.png", dpi=110)
    for i, nm in enumerate(("01_voltage", "02_active_power", "03_reactive_power", "04_frequency")):
        a = ax.flat[i]; f2, b = plt.subplots(figsize=(11, 4))
        for ln in a.get_lines():
            b.plot(*ln.get_data(), lw=0.8, ls=ln.get_linestyle(), color=ln.get_color(), label=ln.get_label())
        b.set_ylim(a.get_ylim()); b.set_title(a.get_title()); b.set_ylabel(a.get_ylabel()); b.set_xlabel("t [s]")
        b.grid(alpha=.3); b.legend(fontsize=7); f2.tight_layout(); f2.savefig(out / f"{nm}.png", dpi=110); plt.close(f2)
    print(f"governed unit = SyncUnit[{gov}]; dP_gov {dP*300:+.2f} MW; f {f0:.4f} -> {f1:.4f} Hz (df {f1-f0:+.4f}); "
          f"expected df from dP_gov {-dP/20*50:+.4f} Hz ({100*((f1-f0)/(-dP/20*50)-1):+.1f} %); "
          f"nadir {f[t>10].min():.4f} Hz; step {-d['PBRK'][post].mean():.2f} MW")
    print("written", out)


def network(ps_gov, ps_nogov):
    out = OUT / "stage2c_governor_network"; out.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    for ps, ls, tag in ((ps_nogov, ":", "no governor"), (ps_gov, "-", "with governor")):
        d = load(ps, ("Wspd", "POUT", "VIT", "DPGOV"), 5)
        t = d["t"]; n = int(round(0.02 / (t[1] - t[0])))
        for k in range(1, 6):
            if (k, "Wspd") in d:
                ax[0].plot(t, mm(d[(k, "Wspd")], n) / 2 / np.pi, ls=ls, lw=0.7, label=f"[{k}] {tag}")
                if (k, "DPGOV") in d:
                    ax[1].plot(t, d[(k, "DPGOV")], ls=ls, lw=0.8, label=f"[{k}] DPGOV {tag}")
        w = (t > t[-1] - 5)
        print(tag, " | ".join(f"[{k}] f {d[(k,'Wspd')][w].mean()/2/np.pi:.4f} pp {np.ptp(mm(d[(k,'Wspd')],n)[w])/2/np.pi*1000:.1f} mHz"
                              + (f" DPGOV {d[(k,'DPGOV')][w].mean():+.5f}" if (k, 'DPGOV') in d else "")
                              for k in range(1, 6) if (k, 'Wspd') in d))
    ax[0].set_ylim(49.9, 50.1); ax[0].set_ylabel("f [Hz]"); ax[0].set_title("Machine frequencies (20 ms mean)")
    ax[1].set_ylabel("governor output [pu on Sbase]"); ax[1].set_title("Governor outputs")
    for a in ax:
        a.grid(alpha=.3); a.legend(fontsize=6, ncol=2)
    ax[1].set_xlabel("t [s]"); fig.tight_layout(); fig.savefig(out / "00_overview.png", dpi=110)
    print("written", out)


if __name__ == "__main__":
    if sys.argv[1] == "bench":
        bench(sys.argv[2])
    else:
        network(sys.argv[2], sys.argv[3])
