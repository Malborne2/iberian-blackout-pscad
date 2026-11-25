r"""S26: relative rotor angles from the recorded speeds (no new recorders, no new run).

    dtheta_ij(t) = 360 deg * integral (f_i - f_j) dt

usage: python stage12\rel_angle.py <psout> <outdir> [i j] [t0] [t1]
Defaults: pair (32,37), whole trace.  Prints the angle at chosen times, the total excursion and the
number of pole slips (excursion / 360 deg), and writes <outdir>\rel_angle.txt + .png.
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
os.makedirs(out, exist_ok=True)
r = mhi.psout.File(ps).run(0)


def get(ch):
    tr = r.call(ch, sep="/")
    return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)


t, _ = get("Root/Main/SyncUnit[1]/Wspd/0/1")
F = {i: get(f"Root/Main/SyncUnit[{i}]/Wspd/0/1")[1] / 2 / np.pi for i in SB}
dt = t[1] - t[0]
L = [f"# {ps}: relative rotor angles from the speeds (360 deg * integral(f_i - f_j) dt)"]
pr = L.append
pairs = [("32", "37"), ("30", "37"), ("32", "30"), ("31", "37"), ("32", "FR")]
name2i = {v: k for k, v in NM.items()}
th = {}
for a, b in pairs:
    ia, ib = name2i[a], name2i[b]
    d = F[ia] - F[ib]
    th[(a, b)] = 360.0 * np.concatenate([[0.0], np.cumsum(0.5 * (d[1:] + d[:-1]) * dt)])
pr(f"t range {t[0]:.2f}-{t[-1]:.2f} s\n")
pr("t      " + "  ".join(f"th{a}-{b} [deg]" for a, b in pairs))
for tt in [t[0], 15.9, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5, t[-1]]:
    k = min(len(t) - 1, int(np.searchsorted(t, tt)))
    pr(f"{t[k]:6.2f} " + "  ".join(f"{th[p][k]:+13.0f}" for p in pairs))
pr("")
for a, b in pairs:
    ex = th[(a, b)][-1] - th[(a, b)][0]
    pr(f"  theta {a}-{b}: total excursion {ex:+.0f} deg = {abs(ex)/360:.1f} pole slips over {t[-1]-t[0]:.1f} s")
open(os.path.join(out, "rel_angle.txt"), "w").write("\n".join(L))
print("\n".join(L))

fig, ax = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
for p in [("32", "37"), ("30", "37"), ("32", "30")]:
    ax[0].plot(t, th[p], lw=1.0, label=f"th{p[0]}-{p[1]}")
ax[0].set(ylabel="relative angle [deg]"); ax[0].grid(alpha=0.3); ax[0].legend(fontsize=7)
for i in SB:
    ax[1].plot(t, F[i], lw=0.9, label=f"f{NM[i]}")
ax[1].set(ylabel="f [Hz]", xlabel="t [s]"); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=7, ncol=5)
fig.suptitle(os.path.basename(ps)); fig.tight_layout()
fig.savefig(os.path.join(out, "rel_angle.png"), dpi=110)
