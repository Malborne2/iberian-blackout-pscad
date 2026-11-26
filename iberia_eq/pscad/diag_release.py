r"""Power balance around the SyncUnit release (S30 sec 10): machines, France source, RES plants, bus voltage.

usage: python iberia_eq\pscad\diag_release.py <tag> [--t0 4.6] [--t1 5.8] [--dt 0.04] [--build build_v2.out]

- machines: sum TMECH and POUT [pu on own S] weighted by each unit's S. Instances are matched to the build-log unit list
  by S-independent order-free assignment on (POUT, |Vt|) before the release, like read_v2.py;
- France: no meter in the case yet. P is computed from the FR bus voltage (3 phases, kV) and the source behind
  Z = 20 ohm / 85 deg: Es(t) = sqrt(2/3) Es sin(w t + phi). The phase convention (sin or cos) is chosen as the one
  that reproduces the load-flow source power (ext grid + 1,000 MW HVDC) in the first window;
- RES: sum over plants of (VD ID + VQ IQ) * Sbase. Sbase per instance from the build log, matched by the
  pre-release ID (all plants run at the same pu current, so the match only affects the weighting).
"""
import argparse, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from legacy_out import load
from scipy.optimize import linear_sum_assignment

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("tag"); ap.add_argument("--t0", type=float, default=4.6)
ap.add_argument("--t1", type=float, default=5.8); ap.add_argument("--dt", type=float, default=0.04)
ap.add_argument("--build", default="build_v2.out"); a = ap.parse_args()
t, c = load(os.path.join(r"C:\PSCAD_work\v2_runs", a.tag), "v2")
units, res, fr = [], [], {}
for ln in open(os.path.join(HERE, a.build), encoding="utf-8", errors="replace"):
    s = ln.strip()
    m = re.match(r"unit (.+?)\s+at (\S+(?: term)?)\s+P\s+(-?[\d.]+) Q\s+([-+\d.]+) S\s+([\d.]+) V ([\d.]+)", s)
    if m: units.append(dict(name=m.group(1), P=float(m.group(3)), S=float(m.group(5)), V=float(m.group(6))))
    m = re.match(r"RES (\S+)\s+at \S+\s+([\d.]+) MW\s+S\s+([\d.]+)", s)
    if m: res.append(float(m.group(3)))
    m = re.match(r"France source: S (-?[\d.]+) MW (-?[\d.]+) Mvar.*Es ([\d.]+) kV (-?[\d.]+) deg", s)
    if m: fr = dict(P=float(m.group(1)) + 1000.0, Es=float(m.group(3)), ph=np.radians(float(m.group(4))))
inst = sorted({k.split(":")[0] for k in c if k.startswith("SyncUnit(")})
jw = (t > a.t0 - 0.3) & (t < a.t0)
C = np.array([[abs(c[f"{i}:POUT"][jw].mean() - u["P"] / u["S"]) / 0.05 + abs(c[f"{i}:VIT[1]"][jw].mean() - u["V"]) / 0.01 for u in units] for i in inst])
r_, c_ = linear_sum_assignment(C); S = {inst[i]: units[j]["S"] for i, j in zip(r_, c_)}
rp = sorted({k.split(":")[0] for k in c if k.startswith("RES_Plant(")})
SR = dict(zip(rp, sorted(res))) if len(res) == len(rp) else {p: np.mean(res) for p in rp}   # weighting only
W = 2 * np.pi * 50; Z = 20.0 * np.exp(1j * np.radians(85.0)); N = int(round(0.02 / (t[1] - t[0])))
def phasor(x, j):                       # one-cycle DFT ending at sample j -> complex rms phasor (sin reference)
    tt = t[j - N + 1:j + 1]; xx = x[j - N + 1:j + 1]
    return (2.0 / N) * np.sum(xx * np.exp(-1j * W * tt)) * 1j / np.sqrt(2)
def p_france(j, conv):
    P = 0.0
    for k, sh in zip((1, 2, 3), (0.0, -2 * np.pi / 3, 2 * np.pi / 3)):
        v = phasor(c[f"V_FR[{k}]"], j)
        e = fr["Es"] / np.sqrt(3) * np.exp(1j * (fr["ph"] + sh + (0.0 if conv == "sin" else np.pi / 2)))
        i_ = (e - v) / Z; P += (v * np.conj(i_)).real
    return P
j0 = np.searchsorted(t, a.t0); conv = min(("sin", "cos"), key=lambda cv: abs(p_france(j0, cv) - fr["P"]))
print(f"France phase convention: {conv}; P at t0 {p_france(j0, conv):.0f} MW vs load flow {fr['P']:.0f} MW")
vb = sorted({k[2:-3] for k in c if k.startswith("V_") and k.endswith("[1]")})
print("   t     Tm sum   Pe sum  France   RES sum   (MW)   Pe+Fr+RES   Vmean kV   f mean Hz")
for tt in np.arange(a.t0, a.t1 + 1e-9, a.dt):
    j = np.searchsorted(t, tt)
    tm = sum(c[f"{i}:TMECH"][j] * S[i] for i in inst); pe = sum(c[f"{i}:POUT"][j] * S[i] for i in inst)
    pf = p_france(j, conv)
    pr = sum((c[f"{p}:VD"][j] * c[f"{p}:ID"][j] + c[f"{p}:VQ"][j] * c[f"{p}:IQ"][j]) * SR[p] for p in rp)
    v = np.mean([np.sqrt(sum(c[f"V_{b}[{k}]"][j] ** 2 for k in (1, 2, 3))) for b in vb])
    f = np.mean([c[f"{i}:Wspd"][j] for i in inst]) / (2 * np.pi)
    print(f"  {tt:5.2f}  {tm:7.0f}  {pe:7.0f}  {pf:6.0f}  {pr:7.0f}          {pe + pf + pr:7.0f}    {v:6.1f}    {f:7.3f}")
