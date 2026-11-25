r"""Compare a v2 PSCAD run with the accepted load flow (S30). Writes iberia_eq\pscad\figs\v2_<tag>.png.

usage: python iberia_eq\pscad\read_v2.py <tag> [--win 8 10]
Reads C:\PSCAD_work\v2_runs\<tag>\ (legacy .out + .infx) and the unit list printed by build_v2.py (build_v2.out).
- bus voltages: V_<bus> channels are the 3 instantaneous phase voltages (kV); sqrt(va^2+vb^2+vc^2) = line-to-line rms;
- machines: SyncUnit(k)/PumpUnit(k) are matched to the load-flow units by (POUT pu, |Vt|) with an optimal assignment
  (PSCAD's instance order is arbitrary, skill P5.4);
- frequency: all machine speeds (Wspd, rad/s) -> Hz; spread printed (loss of synchronism check, skill 3b).
"""
import argparse, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from legacy_out import load
from scipy.optimize import linear_sum_assignment
import pandapower as pp
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

ap = argparse.ArgumentParser(); ap.add_argument("tag"); ap.add_argument("--win", nargs=2, type=float); ap.add_argument("--timeline", type=float)
a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__))
t, c = load(os.path.join(r"C:\PSCAD_work\v2_runs", a.tag), "v2")
w0, w1 = a.win or (max(0.0, t[-1] - 2.0), t[-1]); m = (t >= w0) & (t <= w1)
print(f"{a.tag}: {len(t)} samples to {t[-1]:.2f} s; window {w0:.2f}-{w1:.2f} s")
net = pp.from_pickle(os.path.join(os.path.dirname(HERE), "cal_s29", "base_vk3_net.p"))
VREF = dict(zip(net.bus.name, 400 * net.res_bus.vm_pu))
# ---- bus voltages ----
vb = {}
for k in c:
    mm = re.match(r"V_(.+)\[1\]$", k)
    if mm:
        b = mm.group(1); ph = [c[f"V_{b}[{j}]"] for j in (1, 2, 3)]
        vll = np.sqrt(ph[0] ** 2 + ph[1] ** 2 + ph[2] ** 2) * (1.0 if np.nanmax(np.abs(ph[0])) > 50 else 400.0 / np.sqrt(2.0 / 3.0))
        vb[b] = vll
nm2 = {b.replace("-", "_").replace(" ", "_"): b for b in VREF}
print("bus  PSCAD kV (min..max in window)  load flow  diff")
for b in sorted(vb):
    ref = VREF.get(nm2.get(b, b), np.nan); v = vb[b][m]
    print(f"  {b:14s} {v.mean():7.1f} ({v.min():6.1f}..{v.max():6.1f})  {ref:7.1f}  {v.mean() - ref:+6.1f}")
# ---- machines ----
units = []
for ln in open(os.path.join(HERE, "build_v2.out"), encoding="utf-8", errors="replace"):
    mm = re.match(r"unit (.+?)\s+at (\S+(?: term)?)\s+P\s+(-?[\d.]+) Q\s+([-+\d.]+) S\s+([\d.]+) V ([\d.]+) ang\s+([-+\d.]+)", ln.strip())
    if mm: units.append(dict(name=mm.group(1).strip(), bus=mm.group(2), P=float(mm.group(3)), Q=float(mm.group(4)), S=float(mm.group(5)), V=float(mm.group(6))))
inst = sorted({re.match(r"(SyncUnit\(\d+\))", k).group(1) for k in c if k.startswith("SyncUnit(")})
po = {i: c[f"{i}:POUT"][m].mean() for i in inst}; vi = {i: c[f"{i}:VIT[1]"][m].mean() for i in inst}
if units and len(units) == len(inst):
    C = np.array([[abs(po[i] - u["P"] / u["S"]) / 0.05 + abs(vi[i] - u["V"]) / 0.01 for u in units] for i in inst])
    r_, c_ = linear_sum_assignment(C)
    print("unit                      bus         P lf / PSCAD MW      Q lf / PSCAD Mvar   |Vt| lf / PSCAD   f Hz")
    for ri, ci in zip(r_, c_):
        i, u = inst[ri], units[ci]
        f = c[f"{i}:Wspd"][m].mean() / (2 * np.pi)
        print(f"  {u['name']:22s} {u['bus']:9s} {u['P']:7.0f} / {po[i] * u['S']:7.0f}   {u['Q']:+7.0f} / {c[f'{i}:QOUT'][m].mean() * u['S']:+7.0f}   "
              f"{u['V']:.4f} / {vi[i]:.4f}   {f:.4f}")
else:
    print(f"unit list ({len(units)}) and SyncUnit instances ({len(inst)}) differ: no matching")
ws = np.array([c[f"{i}:Wspd"] for i in inst]) / (2 * np.pi)
if a.timeline:                                   # S30 sec 9: where a collapse starts (0.25 s steps)
    nm_of = {inst[ri]: units[ci]["name"] for ri, ci in zip(r_, c_)} if units and len(units) == len(inst) else {i: i for i in inst}
    print("  t s   Vbus min/mean/max kV     f min..max Hz   fastest / slowest unit")
    for t_ in np.arange(0.0, t[-1] + 1e-9, a.timeline):
        j = min(len(t) - 1, np.searchsorted(t, t_)); vv = np.array([vb[b][j] for b in vb]); ff = ws[:, j]
        print(f"  {t_:5.2f}  {vv.min():6.1f} {vv.mean():6.1f} {vv.max():6.1f}   {ff.min():7.3f}..{ff.max():7.3f}   "
              f"{nm_of[inst[ff.argmax()]]} / {nm_of[inst[ff.argmin()]]}")
print(f"machine frequency in window: {ws[:, m].mean():.4f} Hz, spread {(ws[:, m].max(axis=0) - ws[:, m].min(axis=0)).max() * 1000:.1f} mHz")
fig, ax = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
k = max(1, len(t) // 5000)
for b in vb: ax[0].plot(t[::k], vb[b][::k], lw=0.8)
for j in range(len(ws)): ax[1].plot(t[::k], ws[j, ::k], lw=0.8)
for i in inst: ax[2].plot(t[::k], c[f"{i}:QOUT"][::k], lw=0.8)
ax[0].set_ylabel("bus V LL [kV]"); ax[1].set_ylabel("machine f [Hz]"); ax[2].set_ylabel("unit Q [pu]"); ax[2].set_xlabel("t [s]")
for a_ in ax: a_.grid(alpha=0.3)
ax[0].set_title(f"v2 {a.tag}")
os.makedirs(os.path.join(HERE, "figs"), exist_ok=True); fig.tight_layout(); fig.savefig(os.path.join(HERE, "figs", f"v2_{a.tag}.png"), dpi=100)
