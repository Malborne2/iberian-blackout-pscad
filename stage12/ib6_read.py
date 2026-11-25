r"""ib6 run reader: snapshot table at chosen times + 5-panel figure (whole trace).

usage: python stage12\ib6_read.py <psout> <outdir> [t1,t2,...]
Writes <outdir>\read.txt and <outdir>\trace.png (F1: only into <outdir>).
Units are identified by POUT*Sbase vs P0 (the PSOUT index order is not the bus order).
PTIE is printed Spain -> France positive (raw channel is positive into Iberia, S24 M3 check).
"""
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mhi.psout
import numpy as np

SB = {"30": 6113.0, "31": 13548.0, "32": 15292.0, "37": 12838.0, "39F": 200000.0}
P0 = {"30": 1528.9, "31": 3387.6, "32": 3823.5, "37": 3210.0, "39F": 3195.8}
NB = {1: ("33", 3315.0), 2: ("36", 223.6), 3: ("36", 217.1), 4: ("36", 3122.6), 5: ("34", 841.1),
      6: ("34", 210.6), 7: ("34", 735.8), 8: ("34", 526.5), 9: ("34", 440.7), 10: ("34", 306.8),
      11: ("34", 1552.2), 12: ("35", 795.6), 13: ("35", 169.0), 14: ("35", 3247.4),
      15: ("38", 765.7), 16: ("38", 452.4), 17: ("38", 4071.6), 18: ("33", 520.0)}   # S27: 1 <-> 18 corrected (measured)
BUSES = ["33", "34", "35", "36", "38"]

ps, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
r = mhi.psout.File(ps).run(0)


def get(p):
    tr = r.call(p, sep="/")
    return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)


t, _ = get("Root/Main/SyncUnit[1]/Wspd/0/1")
dt = t[1] - t[0]
n20 = max(1, int(round(0.02 / dt)))


def mm(y, n=n20):
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


U = {}
for i in range(1, 6):
    d = {c: get(f"Root/Main/SyncUnit[{i}]/{c}/0/1")[1] for c in ("Wspd", "POUT", "QOUT", "VIT", "TMECH")}
    U[i] = d
# identify each SyncUnit index by its breaker power meter PBKxx (MW): best match of POUT*Sbase
PBK = {b: get(f"Root/Main/PBK{b}/0/1")[1] for b in ("30", "31", "32", "37")}
late = t >= t[-1] - 0.5
# L2: [2] (37) and [4] (31) are 12.8 and 13.5 GVA machines whose pu outputs are nearly equal
# (0.2585/0.2586 at 50-52 s), so a per-unit ratio test is ambiguous -- it was measured in S25 and is
# re-checked here by (a) the MW residual against the breaker meters and (b) VIT (37 sits higher).
UNIT_MAP = {1: "32", 2: "37", 3: "30", 4: "31", 5: "39F"}
name = UNIT_MAP
if os.environ.get("MAPCHECK", "1") == "1":
    print("unit map check (L2): POUT*Sbase vs PBK [MW]")
    for i, b in UNIT_MAP.items():
        if b == "39F":
            continue
        print("   [%d]=%s  POUT*SB %.1f  vs PBK%s %.1f  d %+.1f MW  VIT %.4f" % (
            i, b, U[i]["POUT"][late].mean() * SB[b], b, np.mean(PBK[b][late]),
            U[i]["POUT"][late].mean() * SB[b] - np.mean(PBK[b][late]), U[i]["VIT"][late].mean()))
PL = {}
for b in BUSES:
    ks = [k for k, (bb, s) in NB.items() if bb == b]
    v = np.mean([get(f"Root/Main/RES_Plant[{k}]/VDF/0/1")[1] for k in ks], axis=0)
    p = np.zeros_like(t)
    for k in ks:
        g = {c: get(f"Root/Main/RES_Plant[{k}]/{c}/0/1")[1] for c in ("VD", "VQ", "ID", "IQ")}
        p += (g["VD"] * g["ID"] + g["VQ"] * g["IQ"]) * NB[k][1]
    PL[b] = (v, p)
ptie = -get("Root/Main/PTIE/0/1")[1]
hv = {c: get(f"Root/Main/HVDC_T/{c}/0/1")[1] for c in ("ID", "IQ", "VD", "VQ")}
hp = (hv["VD"] * hv["ID"] + hv["VQ"] * hv["IQ"]) * 1000.0
v9 = get("Root/Main/V9/0/1")[1] / 400.0
oos = get("Root/Main/OOS1/0/1")[1]

ts = [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else \
    [x for x in (0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 2.9, 3.2, 3.5, 4.0, 6, 8, 10, 12, 14) if x <= t[-1] + 1e-9]
L = []
pr = L.append
pr(f"# {ps}\n# t 0..{t[-1]:.3f} s, values = 20 ms means centred at t (p-p over the 0.2 s before t)\n")
pr("units: " + ", ".join(f"[{i}]={name[i]}" for i in U))
for tt in ts:
    k = min(len(t) - 1, int(np.searchsorted(t, tt)))   # psout may start at the snapshot time
    w = slice(max(0, k - int(0.2 / dt)), k + 1)
    pr(f"\n--- t = {tt:.2f} s")
    gen = 0.0
    for i, d in U.items():
        b = name[i]
        f = mm(d["Wspd"])[k] / 2 / np.pi
        fpp = (d["Wspd"][w].max() - d["Wspd"][w].min()) / 2 / np.pi * 1000
        P = mm(d["POUT"])[k] * SB[b]; Q = mm(d["QOUT"])[k] * SB[b]; TM = mm(d["TMECH"])[k] * SB[b]
        if b != "39F":
            gen += P
        pr(f"  unit {b:>3}: f {f:8.4f} Hz (p-p {fpp:6.1f} mHz)  P {P:8.0f} MW  Q {Q:+7.0f} Mvar  V {mm(d['VIT'])[k]:.4f} pu  Tm*S {TM:8.0f}")
    pt = 0.0
    for b in BUSES:
        v, p = PL[b]
        pt += mm(p)[k]
        pr(f"  bus {b}: VDF {mm(v)[k]:.4f} (p-p {v[w].max()-v[w].min():.4f})  plant P {mm(p)[k]:7.0f} MW")
    pr(f"  plants {pt:.0f} MW, Iberian units {gen:.0f} MW, PTIE {mm(ptie)[k]:+.0f} MW (S->F), HVDC P {mm(hp)[k]:+.0f} (neg=export), V9 {mm(v9)[k]:.3f} pu, OOS1 {oos[k]:.0f}")
open(os.path.join(out, "read.txt"), "w").write("\n".join(L))
print("\n".join(L))

fig, ax = plt.subplots(5, 1, figsize=(12, 14), sharex=True)
for b in BUSES:
    ax[0].plot(t, mm(PL[b][0]), lw=0.8, label=f"bus {b}")
    ax[1].plot(t, mm(PL[b][1]), lw=0.8, label=f"bus {b}")
for i, d in U.items():
    ax[2].plot(t, mm(d["Wspd"]) / 2 / np.pi, lw=0.8, label=name[i])
    ax[3].plot(t, mm(d["QOUT"]) * SB[name[i]], lw=0.8, label=name[i])
ax[4].plot(t, mm(ptie), lw=0.8, label="PTIE S->F [MW]")
ax[4].plot(t, -mm(hp), lw=0.8, label="HVDC export [MW]")
for a, yl in zip(ax, ["collector VDF [pu]", "plant P per bus [MW]", "f [Hz]", "unit Q [Mvar]", "MW"]):
    a.set(ylabel=yl); a.grid(alpha=0.3); a.legend(ncol=5, fontsize=7)
ax[-1].set(xlabel="time [s]")
fig.suptitle(os.path.basename(ps)); fig.tight_layout()
fig.savefig(os.path.join(out, "trace.png"), dpi=110)

# ---- settle gate (PLAN v1.0 S2), window w0..w1 (default last 2 s before the snapshot time)
w0, w1 = (float(x) for x in (os.environ.get("GATE", "10,12").split(",")))
W = (t >= w0) & (t <= w1)
G = []
fs = {name[i]: d["Wspd"][W] / 2 / np.pi for i, d in U.items()}
fm = {b: v.mean() for b, v in fs.items()}
G.append(("all 5 machines f = 50.00 +- 0.02 Hz", max(abs(v - 50) for v in fm.values()) < 0.02, " ".join(f"{b}:{v:.4f}" for b, v in fm.items())))
G.append(("speed spread < 5 mHz", (max(fm.values()) - min(fm.values())) * 1000 < 5, f"{(max(fm.values())-min(fm.values()))*1000:.1f} mHz"))
pp = {b: (mm(v).max() - mm(v).min()) * 1000 for b, v in fs.items()}
G.append(("speed p-p each < 10 mHz", max(pp.values()) < 10, " ".join(f"{b}:{v:.1f}" for b, v in pp.items())))
vpp = {b: mm(PL[b][0])[W].max() - mm(PL[b][0])[W].min() for b in BUSES}
G.append(("collector VDF p-p < 0.005 pu", max(vpp.values()) < 0.005, " ".join(f"{b}:{v:.4f}" for b, v in vpp.items())))
sl = {b: np.polyfit(t[W], PL[b][0][W], 1)[0] for b in BUSES}
G.append(("collector VDF |drift| < 0.002 pu/s", max(abs(v) for v in sl.values()) < 0.002, " ".join(f"{b}:{v:+.4f}" for b, v in sl.items())))
trips = max(get(f"Root/Main/RES_Plant[{k}]/TRIP/0/1")[1][t <= w1].max() for k in NB)
G.append(("plant TRIP all 0", trips == 0, f"{trips:.0f}"))
for nm in ("BRK30", "BRK31", "BRK32", "BRK37", "BRKFR", "OOS1"):
    v = get(f"Root/Main/{nm}/0/1")[1][(t >= 0.1) & (t <= w1)].max()   # meters undefined in the first ms
    G.append((f"{nm} = 0", v == 0, f"{v:.0f}"))
G.append(("PTIE = +335 +- 100 MW (S->F)", abs(ptie[W].mean() - 335) <= 100, f"{ptie[W].mean():+.0f} (p-p {mm(ptie)[W].max()-mm(ptie)[W].min():.0f})"))
G.append(("HVDC P = 1000 +- 10 MW export", abs(-hp[W].mean() - 1000) <= 10, f"{-hp[W].mean():.0f}"))
gl = [f"=== settle gate, window {w0}-{w1} s ==="] + [f"{'PASS' if ok else 'FAIL'}  {n:40s} {v}" for n, ok, v in G]
gl.append(f"RESULT {sum(ok for _, ok, _ in G)}/{len(G)}")
gl.append("collector VDF means: " + " ".join(f"{b}:{PL[b][0][W].mean():.4f}" for b in BUSES))
gl.append("unit P/Q/V means: " + "; ".join(f"{name[i]} {U[i]['POUT'][W].mean()*SB[name[i]]:.0f} MW {U[i]['QOUT'][W].mean()*SB[name[i]]:+.0f} Mvar {U[i]['VIT'][W].mean():.4f}" for i in U))
gl.append(f"plants {sum(PL[b][1][W].mean() for b in BUSES):.0f} MW")
open(os.path.join(out, "gate.txt"), "w").write(chr(10).join(gl)); print(chr(10).join(gl))
