r"""S26/WP8.2: the slip — peak tie import, the angle across the tie, the opening time, and coherence.

usage: python stage12/wp8_slip.py <psout> <outdir>
Prints, for the window before/after the opening:
  * raw (un-averaged) PTIE minimum and the 20 ms-mean minimum, and when they occur;
  * BRKFR's opening time, OOS1's first fire;
  * |dPh| = Ph39 - Ph9 (cos/sin, so the +-180 wrap is removed) in degrees, max before opening;
  * the spread between the four Iberian speeds after the opening (coherence check, C4).
Writes <outdir>\wp8_slip.txt and <outdir>\wp8_slip.png.
"""
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mhi.psout
import numpy as np

ps, out = sys.argv[1], sys.argv[2]
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


ptie = -get("Root/Main/PTIE/0/1")[1]
brkfr = get("Root/Main/BRKFR/0/1")[1]
oos = get("Root/Main/OOS1/0/1")[1]
L = []
pr = L.append
pr(f"# {ps}")
pr(f"PTIE raw minimum           {ptie.min():+9.0f} MW at t = {t[np.argmin(ptie)]:8.3f} s")
pr(f"PTIE 20 ms-mean minimum    {mm(ptie).min():+9.0f} MW at t = {t[np.argmin(mm(ptie))]:8.3f} s")
i = np.argmax(brkfr > 0.5) if (brkfr > 0.5).any() else None
pr(f"BRKFR first 1              {None if i is None else f'{t[i]:.3f} s'}")
j = np.argmax(oos > 0.5) if (oos > 0.5).any() else None
pr(f"OOS1 first 1               {None if j is None else f'{t[j]:.3f} s'}")

# angle across the tie, if the meters are recorded
try:
    ph9 = get("Root/Main/Ph9/0/1")[1]
    ph39 = get("Root/Main/Ph39/0/1")[1]
    d = np.degrees(np.angle(np.exp(1j * np.radians(ph39 - ph9))))
    k = i if i is not None else len(t) - 1
    pr(f"|dPh| = Ph39-Ph9: max {np.abs(d[:k]).max():7.1f} deg before the opening; "
       f"at the opening {d[k]:7.1f} deg")
    have_angle = True
except Exception as e:  # noqa: BLE001
    pr(f"angle channels not available: {e}")
    have_angle = False

SB = {1: 15292.0, 2: 12838.0, 3: 6113.0, 4: 13548.0}
NM = {1: "32", 2: "37", 3: "30", 4: "31"}
F = {i: get(f"Root/Main/SyncUnit[{i}]/Wspd/0/1")[1] / 2 / np.pi for i in SB}
pr("\ncoherence after the opening (C4): f of the three machines still connected to Iberia")
for tt in (85.5, 86.0, 86.5, 87.0, 87.5, 88.0):
    kk = min(len(t) - 1, int(np.searchsorted(t, tt)))
    vals = "  ".join(f"f{NM[i]} {F[i][kk]:7.3f}" for i in (1, 2, 3))
    pr(f"  t={tt:5.2f}  {vals}   spread {(max(F[i][kk] for i in (1,2,3)) - min(F[i][kk] for i in (1,2,3)))*1000:7.0f} mHz")
open(os.path.join(out, "wp8_slip.txt"), "w").write("\n".join(L))
print("\n".join(L))

fig, ax = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
ax[0].plot(t, ptie, lw=0.5, label="PTIE raw")
ax[0].plot(t, mm(ptie), lw=1.0, label="PTIE 20 ms")
ax[0].set(ylabel="PTIE S->F [MW]"); ax[0].legend(fontsize=7); ax[0].grid(alpha=0.3)
if have_angle:
    ax[1].plot(t, d, lw=0.8)
ax[1].set(ylabel="Ph39 - Ph9 [deg, wrapped]"); ax[1].grid(alpha=0.3)
for i in SB:
    ax[2].plot(t, F[i], lw=0.8, label=f"f{NM[i]}")
ax[2].plot(t, get("Root/Main/SyncUnit[5]/Wspd/0/1")[1] / 2 / np.pi, lw=0.8, label="fFR")
ax[2].set(ylabel="f [Hz]"); ax[2].legend(fontsize=7, ncol=5); ax[2].grid(alpha=0.3)
ax[2].set(xlabel="time [s]")
fig.suptitle(os.path.basename(ps)); fig.tight_layout()
fig.savefig(os.path.join(out, "wp8_slip.png"), dpi=110)
