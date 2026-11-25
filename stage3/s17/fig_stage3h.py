"""Figure set for Stage 3h: the RES_Plant *module* on the two-plant shared-rail bench (Session 17).

Run: C:\\PSCAD_work\\rp1 (copy kept as stage3\\s17\\rp1_stage3h.pscx), 1.5 s at 5 us.
  plant 1: Pref pulse 0.5 -> 0.1 (0.5 s) -> 0.5 (1.0 s), CarrPh 0, relay test setting Vt 0.99 / Tt 0.2 s
  plant 2: same Pref, CarrPh 90, Force = 1 from 1.25 s (Case-A trip command)
  grid   : 400 kV, Z1 = Z0 = 53.33 ohm at 87 deg (SCR 5 on 600 MVA), source Type 4 (R-R//L)
P, Q from the dq quantities on each plant's own 300 MVA base:
  P = vd*id + vq*iq ;  Q = vd*iq - vq*id  (iq > 0 = injection, verified against the grid
  source's own P/Q outputs in this session). Frequency = d(PLL angle)/dt / 2pi, 20 ms mean.
usage: python fig_stage3h.py <psout>
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mhi.psout

PS = sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\rp1.gf81_x86\rp1.psout"
OUT = Path(__file__).resolve().parents[2] / "results" / "stage3h_module"
OUT.mkdir(parents=True, exist_ok=True)
SB = 300.0


def mm(y, n):
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


d = {}
with mhi.psout.File(PS) as f:
    run = f.run(0)
    for k in (1, 2):
        for c in ("VD", "VQ", "ID", "IQ", "VDF", "TRIP", "THETA_TR", "IsrcA", "VA_PU"):
            tr = run.call(f"Root/Main/RES_Plant[{k}]/{c}/0/1", sep="/")
            t = np.asarray(tr.domain.data, float)
            d[(k, c)] = np.asarray(tr.data, float)
    for c in ("PG", "QG"):
        d[c] = np.asarray(run.call(f"Root/Main/{c}/0/1", sep="/").data, float)
n20 = int(round(0.02 / (t[1] - t[0])))
lab = {1: "plant 1 (CarrPh 0, OV relay 0.99 pu / 0.2 s)", 2: "plant 2 (CarrPh 90, forced trip 1.25 s)"}
P = {k: mm(d[(k, "VD")] * d[(k, "ID")] + d[(k, "VQ")] * d[(k, "IQ")], n20) * SB for k in (1, 2)}
Q = {k: mm(d[(k, "VD")] * d[(k, "IQ")] - d[(k, "VQ")] * d[(k, "ID")], n20) * SB for k in (1, 2)}
F = {}
for k in (1, 2):
    th = np.unwrap(d[(k, "THETA_TR")])
    F[k] = mm(np.gradient(th, t) / (2 * np.pi), n20)
trip = {k: t[np.argmax(d[(k, "TRIP")] > 0.5)] if d[(k, "TRIP")].max() > 0.5 else None for k in (1, 2)}
m = t > 0.3


def deco(ax, yl, title):
    for k, tt in trip.items():
        if tt:
            ax.axvline(tt, color=f"C{k-1}", ls=":", lw=1)
    ax.axvline(0.5, color="0.6", lw=0.6); ax.axvline(1.0, color="0.6", lw=0.6)
    ax.set_ylabel(yl); ax.set_title(title, fontsize=9); ax.grid(alpha=0.3)


panels = []
def p_v(ax):
    for k in (1, 2):
        ax.plot(t[m], d[(k, "VDF")][m], lw=0.8, label=lab[k])
    ax.axhline(0.99, color="r", ls="--", lw=0.7, label="plant-1 relay threshold 0.99")
    deco(ax, "POI |V| (VDF) [pu]", "Voltage at the POI (d-axis, 8 ms filter)"); ax.legend(fontsize=7)
def p_p(ax):
    for k in (1, 2):
        ax.plot(t[m], P[k][m], lw=0.8, label=lab[k])
    ax.plot(t[m], -mm(d["PG"], n20)[m] * 600 / 2, "k--", lw=0.7, label="grid source -P/2")
    deco(ax, "P [MW]", "Active power (20 ms mean)"); ax.legend(fontsize=7)
def p_q(ax):
    for k in (1, 2):
        ax.plot(t[m], Q[k][m], lw=0.8, label=lab[k])
    ax.plot(t[m], -mm(d["QG"], n20)[m] * 600 / 2, "k--", lw=0.7, label="grid source -Q/2")
    deco(ax, "Q [Mvar] (+ = injection)", "Reactive power: fixed PF 0.985 absorbing"); ax.legend(fontsize=7)
def p_f(ax):
    for k in (1, 2):
        ax.plot(t[m], F[k][m], lw=0.8, label=lab[k])
    deco(ax, "f [Hz]", "PLL frequency (20 ms mean)"); ax.legend(fontsize=7)
def p_trip(ax):
    for k in (1, 2):
        ax.plot(t, d[(k, "TRIP")] + 0.02 * k, lw=1, label=lab[k])
    deco(ax, "TRIP", "Trip flags (latched)"); ax.legend(fontsize=7)
def p_cm(ax):
    s = (t > 0.40) & (t < 0.44)
    i1, i2 = d[(1, "IsrcA")][s], d[(2, "IsrcA")][s]
    ax.plot(t[s], i1, lw=0.6, label="plant 1 i_a"); ax.plot(t[s], i2, lw=0.6, label="plant 2 i_a")
    ax.plot(t[s], i1 + i2, "k", lw=0.8, label="sum = grid i_a")
    ax.set_ylabel("kA"); ax.grid(alpha=0.3); ax.legend(fontsize=7)
    ax.set_title("Shared rail: common-mode current circulates between plants, cancels in the grid", fontsize=9)

draws = [("01_voltage", p_v), ("02_active_power", p_p), ("03_reactive_power", p_q), ("04_frequency", p_f),
         ("05_trip_flags", p_trip), ("06_shared_rail_current", p_cm)]
fig, axs = plt.subplots(2, 2, figsize=(14, 8), sharex=True)
for ax, (_, fn) in zip(axs.flat, draws[:4]):
    fn(ax)
for ax in axs[-1]:
    ax.set_xlabel("t [s]")
fig.suptitle("Stage 3h - RES_Plant module, two plants on one shared 800 kV rail (SCR 5)")
fig.tight_layout(); fig.savefig(OUT / "00_overview.png", dpi=110); plt.close(fig)
for name, fn in draws:
    fig, ax = plt.subplots(figsize=(11, 4)); fn(ax); ax.set_xlabel("t [s]")
    fig.tight_layout(); fig.savefig(OUT / f"{name}.png", dpi=110); plt.close(fig)

w = lambda lo, hi: (t >= lo) & (t <= hi)
for k in (1, 2):
    for lo, hi in ((0.30, 0.48), (0.80, 0.98), (1.30, 1.48)):
        s = w(lo, hi)
        print(f"plant {k} {lo:.2f}-{hi:.2f}: P {P[k][s].mean():7.1f} MW  Q {Q[k][s].mean():6.1f} Mvar  "
              f"V {d[(k,'VDF')][s].mean():.4f}  f {F[k][s].mean():.3f} Hz")
    print(f"plant {k} trip at {trip[k]}")
print("written", OUT)
