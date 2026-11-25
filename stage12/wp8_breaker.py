r"""S26/WP8: breaker-test reader — breaker states, unit breaker powers, all five speeds, tie, RoCoF.

usage: python stage12\wp8_breaker.py <psout> <outdir> <t1,t2,...> [rocof_from rocof_to]
Prints, at each t: BRK30/31/32/37/BRKFR/OOS1 (0/1), PBK30/31/32/37 [MW] (power through each unit
breaker), the five machine speeds in Hz, PTIE (S->F), HVDC export, and the Iberian unit total.
Also the measured RoCoF over [rocof_from, rocof_to] for each machine and the C2 prediction for the
loss of one unit (RoCoF = dP*50/(2*KE), KE = Iberia 119.5 GW s + France 5000 GW s while connected).
Writes <outdir>\wp8.txt and <outdir>\wp8.png.
"""
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mhi.psout
import numpy as np

SB = {1: 15292.0, 2: 12838.0, 3: 6113.0, 4: 13548.0, 5: 200000.0}
NM = {1: "32", 2: "37", 3: "30", 4: "31", 5: "FR"}
ps, out = sys.argv[1], sys.argv[2]
ts = [float(x) for x in sys.argv[3].split(",")]
rf = (float(sys.argv[4]), float(sys.argv[5])) if len(sys.argv) > 5 else None
os.makedirs(out, exist_ok=True)
r = mhi.psout.File(ps).run(0)


def get(ch):
    tr = r.call(ch, sep="/")
    return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)


t, _ = get("Root/Main/SyncUnit[1]/Wspd/0/1")
dt = t[1] - t[0]
n20 = max(1, int(round(0.02 / dt)))


def mm(y, n=n20):
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


F = {i: get(f"Root/Main/SyncUnit[{i}]/Wspd/0/1")[1] / 2 / np.pi for i in SB}
P = {i: get(f"Root/Main/SyncUnit[{i}]/POUT/0/1")[1] * SB[i] for i in SB}
BRK = {b: get(f"Root/Main/BRK{b}/0/1")[1] for b in ("30", "31", "32", "37", "FR")}
PBK = {b: get(f"Root/Main/PBK{b}/0/1")[1] for b in ("30", "31", "32", "37")}
OOS = get("Root/Main/OOS1/0/1")[1]
PTIE = -get("Root/Main/PTIE/0/1")[1]
hv = {c: get(f"Root/Main/HVDC_T/{c}/0/1")[1] for c in ("ID", "IQ", "VD", "VQ")}
HP = -(hv["VD"] * hv["ID"] + hv["VQ"] * hv["IQ"]) * 1000.0

L = []
pr = L.append
pr(f"# {ps}\n# t {t[0]:.3f}..{t[-1]:.3f} s, 20 ms means\n")
hdr = (" t      BRK30 31 32 37 FR OOS | " + "  ".join(f"PBK{b}" for b in ("30", "31", "32", "37")) +
       " | " + "  ".join(f"f{NM[i]}" for i in SB) + " | PTIE  HVDC  unittot")
pr(hdr)
for tt in ts:
    k = min(len(t) - 1, int(np.searchsorted(t, tt)))
    row = [f"{tt:7.2f}", "  ".join(f"{BRK[b][k]:.0f}" for b in ("30", "31", "32", "37", "FR")),
           f"{OOS[k]:.0f}", "|"]
    row += [f"{PBK[b][k]:+7.0f}" for b in ("30", "31", "32", "37")]
    row += ["|"] + [f"{mm(F[i])[k]:8.4f}" for i in SB]
    row += ["|", f"{mm(PTIE)[k]:+6.0f}", f"{mm(HP)[k]:+6.0f}", f"{sum(mm(P[i])[k] for i in SB if i != 5):+7.0f}"]
    pr(" ".join(row))

if rf:
    w = (t >= rf[0]) & (t <= rf[1])
    pr(f"\nRoCoF, window {rf[0]}-{rf[1]} s (least squares on the 20 ms mean), and C2 prediction:")
    for i in SB:
        y = mm(F[i])[w]
        x = t[w]
        sl = np.polyfit(x, y, 1)[0]
        pr(f"  f{NM[i]}: {sl*1000:+7.1f} mHz/s   (df = {(y[-1]-y[0])*1000:+.1f} mHz)")
    dP = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
    for ke, lab in ((119.5e3, "Iberia alone 119.5 GW s"), (119.5e3 + 5.0e6, "Iberia + France 5,119.5 GW s")):
        pr(f"  C2 with dP = {dP:.0f} MW, KE = {lab}: RoCoF = {dP*50/(2*ke):+7.1f} mHz/s")

open(os.path.join(out, "wp8.txt"), "w").write("\n".join(L))
print("\n".join(L))

fig, ax = plt.subplots(4, 1, figsize=(12, 12), sharex=True)
for i in SB:
    ax[0].plot(t, mm(F[i]), lw=0.9, label=f"f{NM[i]}")
for b in ("30", "31", "32", "37"):
    ax[1].plot(t, mm(PBK[b]), lw=0.9, label=f"PBK{b}")
ax[2].plot(t, mm(PTIE), lw=0.9, label="PTIE S->F")
ax[2].plot(t, mm(HP), lw=0.9, label="HVDC export")
for b in ("30", "31", "32", "37", "FR"):
    ax[3].plot(t, BRK[b], lw=0.9, label=f"BRK{b}")
ax[3].plot(t, OOS, lw=0.6, ls="--", label="OOS1")
ax[3].set(ylabel="breaker signal (1 = open)")
ax[0].set(ylabel="f [Hz]"); ax[1].set(ylabel="PBK [MW]"); ax[2].set(ylabel="MW")
for a in ax:
    a.grid(alpha=0.3); a.legend(fontsize=7, ncol=5)
ax[-1].set(xlabel="time [s]")
fig.suptitle(os.path.basename(ps)); fig.tight_layout()
fig.savefig(os.path.join(out, "wp8.png"), dpi=110)
