r"""Settle gate (PLAN.md 2b S2 / G7a) + 2c C3 balance + C1 whole-trace statistics, from one .psout.

usage: python stage11\\gate_reader.py <psout> <outdir> [--win 10 12] [--label text]

Writes every number it prints, and the figure set, into <outdir> (rule F1: nothing outside it).

Rows and criteria are copied from PLAN.md 2b S2 (not invented here):
  machines  f = 50.00 +- 0.02 Hz, spread between machines < 5 mHz, p-p < 10 mHz
  collectors VDF p-p < 0.005 pu, |drift| < 0.002 pu/s
  TRIP (18 plants), BRK30/31/32/37, BRKFR, OOS1 all 0
  PTIE +335 +- 100 MW  (Spain -> France), sign checked against France POUT - French load
  HVDC P 1,000 +- 10 MW export

Identification (rule L2): the 5 SyncUnit channels are assigned to (bus, Sbase, P0) by the permutation
that best matches   POUT*Sbase = P0   (P0 read from ib5.pscx).  The 18 RES_Plant channels use the S19b
measured map (stage3\wp5_state.py NBUS x KPLANT); it is re-checked here every run by requiring the
plants of one bus to share VDF within 1 %, and every id to lie in 0.30..1.10.
"""
import argparse
import os
import sys
from itertools import permutations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mhi.psout
import numpy as np

KPLANT = float(os.environ.get("KPLANT", "1.30"))

# n -> (bus label, Sbase MVA at KPLANT=1)   [S19b measured channel order]
NBUS = {1: ("33", 400.0), 2: ("36", 172.0), 3: ("36", 167.0), 4: ("36", 2402.0),
        5: ("34", 647.0), 6: ("34", 162.0), 7: ("34", 566.0), 8: ("34", 405.0),
        9: ("34", 339.0), 10: ("34", 236.0), 11: ("34", 1194.0),
        12: ("35", 612.0), 13: ("35", 130.0), 14: ("35", 2498.0),
        15: ("38", 589.0), 16: ("38", 348.0), 17: ("38", 3132.0), 18: ("33", 2550.0)}
NBUS = {k: (b, s * KPLANT) for k, (b, s) in NBUS.items()}
BUSES = ["33", "34", "35", "36", "38"]

# ib5.pscx SyncUnit instances (S24 read-back): (bus label, Sbase MVA, P0 MW)
MACH = [("30", 6113.0, 1528.9), ("31", 13548.0, 3387.6), ("32", 15292.0, 3823.5),
        ("37", 12838.0, 3210.0), ("39F", 200000.0, 3195.8)]

LOAD_MW = 28087.5          # 1b.5: 19 Iberian fixed_load PO x 3, at 1.0 pu
LOAD_MW_FR = 4530.8        # 1b.4: French load at HE39_2
AC_EXPORT_MW = 335.0       # report Fig 3-5 (only used for the PTIE sign check)
SB_HVDC = 1000.0


def mm(y, n):
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


def r1s(y, t, dt, fn):
    """rolling 1 s statistic of y: returns array over t (centred)."""
    n = max(2, int(round(1.0 / dt)))
    h = n // 2
    out = np.empty_like(y)
    pad = np.concatenate([np.full(h, np.nan), y, np.full(n - h, np.nan)])
    for i in range(len(y)):
        seg = pad[i:i + n]
        out[i] = fn(seg)
    return out


def first_pass(t, ok, t_end):
    """earliest t after which a per-sample boolean holds continuously up to t_end."""
    w = t <= t_end
    idx = np.where(w)[0]
    bad = idx[~ok[idx]]
    if bad.size == 0:
        return t[0]
    return t[bad[-1]] + (t[1] - t[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("psout")
    ap.add_argument("outdir")
    ap.add_argument("--win", nargs=2, type=float, default=[10.0, 12.0])
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    w0, w1 = a.win
    os.makedirs(a.outdir, exist_ok=True)

    f = mhi.psout.File(a.psout)
    r = f.run(0)

    def get(p):
        tr = r.call(p, sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)

    t, _ = get("Root/Main/SyncUnit[1]/Wspd/0/1")
    dt = t[1] - t[0]
    w = (t >= w0) & (t <= w1)
    lines = []

    def out(s=""):
        print(s)
        lines.append(s)

    out(f"# {a.label}")
    out(f"psout      {a.psout}")
    out(f"t          {t[0]:.4f} .. {t[-1]:.4f} s   dt {dt*1e6:.0f} us   window {w0}-{w1} s"
        f"   KPLANT {KPLANT}")
    out("")

    # ---------------------------------------------------------------- machines
    n_m = 0
    while True:
        try:
            get(f"Root/Main/SyncUnit[{n_m + 1}]/Wspd/0/1")
            n_m += 1
        except Exception:
            break
    mach = []
    for k in range(1, n_m + 1):
        ws = get(f"Root/Main/SyncUnit[{k}]/Wspd/0/1")[1]
        fs = ws / 2.0 / np.pi
        mach.append(dict(k=k, f=fs,
                         po=get(f"Root/Main/SyncUnit[{k}]/POUT/0/1")[1],
                         qo=get(f"Root/Main/SyncUnit[{k}]/QOUT/0/1")[1],
                         vit=get(f"Root/Main/SyncUnit[{k}]/VIT/0/1")[1],
                         th=get(f"Root/Main/SyncUnit[{k}]/THETA/0/1")[1],
                         dpg=get(f"Root/Main/SyncUnit[{k}]/DPGOV/0/1")[1]))
    # assignment: France has |POUT| < 0.1 (3,196/200,000 = 0.016), the four Iberian units ~0.25;
    # then the 4 Iberian units are matched by POUT*Sbase = P0 (1528.9 / 3387.6 / 3823.5 / 3210.0 MW).
    i_fr = int(np.argmin([abs(m["po"][w].mean()) for m in mach]))
    rest = [i for i in range(n_m) if i != i_fr]
    cand = [i for i, m in enumerate(MACH) if m[0] != "39F"]
    best, besterr = None, 1e9
    for perm in permutations(cand, len(rest)):
        err = 0.0
        for j, ch in enumerate(rest):
            lab, sb, p0 = MACH[perm[j]]
            err += abs(mach[ch]["po"][w].mean() * sb - p0) / max(abs(p0), 1.0)
        if err < besterr:
            best, besterr = perm, err
    assign = [None] * n_m
    for j, ch in enumerate(rest):
        assign[ch] = best[j]
    assign[i_fr] = [i for i, m in enumerate(MACH) if m[0] == "39F"][0]
    best = tuple(assign)
    fr_ok = abs(mach[i_fr]["po"][w].mean() * 200000.0 - 3195.8) / 3195.8 < 0.20
    assign_ok = besterr < 0.10 and fr_ok
    out("machines  (France = min |POUT|; others by POUT*Sbase = P0; sum |rel err| = "
        f"{besterr:.4f} -> {'OK' if assign_ok else 'FAIL'})")
    out(f"{'ch':>3} {'bus':>4} {'Sbase':>7} {'POUT':>8} {'MW':>8} {'QOUT':>8} {'Mvar':>8} "
        f"{'VIT pu':>7} {'kV':>7} {'f Hz':>8} {'f p-p':>7} {'f p-p':>7} {'f min':>8} {'f max':>8} {'THETA':>8}")
    out(f"{'':>3} {'':>4} {'MVA':>7} {'pu':>8} {'':>8} {'pu':>8} {'':>8} "
        f"{'':>7} {'':>7} {'mean':>8} {'mHz':>7} {'run':>7} {'run':>8} {'run':>8} {'deg':>8}")
    fwin = []
    for i, m in enumerate(mach):
        lab, sb, p0 = MACH[best[i]]
        fw = m["f"][w]
        fwin.append(fw)
        out(f"{m['k']:3d} {lab:>4} {sb:7.0f} {m['po'][w].mean():+8.4f} "
            f"{m['po'][w].mean()*sb:+8.1f} {m['qo'][w].mean():+8.4f} "
            f"{m['qo'][w].mean()*sb:+8.1f} {m['vit'][w].mean():7.4f} "
            f"{m['vit'][w].mean()*400:7.1f} {fw.mean():8.4f} "
            f"{np.ptp(fw)*1000:7.1f} {np.ptp(m['f'])*1000:7.1f} "
            f"{m['f'].min():8.4f} {m['f'].max():8.4f} {m['th'][w].mean():8.3f}")
    fmean = np.mean([x.mean() for x in fwin])
    spread = max(x.mean() for x in fwin) - min(x.mean() for x in fwin)
    fpp = np.max([np.ptp(x) for x in fwin])
    out("")

    # ---------------------------------------------------------------- plants
    n_p = 0
    while True:
        try:
            get(f"Root/Main/RES_Plant[{n_p + 1}]/ID/0/1")
            n_p += 1
        except Exception:
            break
    n20 = max(1, int(round(0.02 / dt)))
    rows = []
    for k in range(1, n_p + 1):
        vd = get(f"Root/Main/RES_Plant[{k}]/VD/0/1")[1]
        vq = get(f"Root/Main/RES_Plant[{k}]/VQ/0/1")[1]
        idk = get(f"Root/Main/RES_Plant[{k}]/ID/0/1")[1]
        iqk = get(f"Root/Main/RES_Plant[{k}]/IQ/0/1")[1]
        vdf = get(f"Root/Main/RES_Plant[{k}]/VDF/0/1")[1]
        trip = get(f"Root/Main/RES_Plant[{k}]/TRIP/0/1")[1]
        bus, sb = NBUS[k]
        rows.append(dict(k=k, bus=bus, sb=sb, vdf=vdf, id=idk, iq=iqk,
                         p=mm(vd * idk + vq * iqk, n20) * sb,
                         q=mm(vd * iqk - vq * idk, n20) * sb, trip=trip))
    checks = []
    for b in BUSES:
        g = [x for x in rows if x["bus"] == b]
        v = np.array([x["vdf"][w].mean() for x in g])
        checks.append((f"bus {b}: VDF spread {v.min():.4f}..{v.max():.4f}",
                       (v.max() - v.min()) <= 0.01 * abs(v.mean())))
    ids = np.array([x["id"][w].mean() for x in rows])
    checks.append((f"plant id plausibility {ids.min():.3f}..{ids.max():.3f} (0.15..1.10)",
                   ids.min() > 0.15 and ids.max() < 1.10))
    out("plants  (n=%d per-bus identification, rule L2)" % n_p)
    out(f"{'ch':>3} {'bus':>4} {'Sbase':>7} {'VDF pu':>7} {'VDF p-p':>8} {'slope':>9} "
        f"{'id':>7} {'iq':>8} {'P MW':>8} {'Q Mvar':>8} {'TRIP':>5}")
    out(f"{'':>3} {'':>4} {'MVA':>7} {'':>7} {'pu':>8} {'pu/s':>9} "
        f"{'pu':>7} {'pu':>8} {'':>8} {'':>8} {'':>5}")
    tp = tq = 0.0
    plant_pp = 0.0
    plant_slope = 0.0
    for x in rows:
        vw = x["vdf"][w]
        sl = np.polyfit(t[w], vw, 1)[0]
        plant_pp = max(plant_pp, np.ptp(vw))
        plant_slope = max(plant_slope, abs(sl))
        tp += x["p"][w].mean()
        tq += x["q"][w].mean()
        out(f"{x['k']:3d} {x['bus']:>4} {x['sb']:7.0f} {vw.mean():7.4f} {np.ptp(vw):8.4f} "
            f"{sl:+9.5f} {x['id'][w].mean():7.4f} {x['iq'][w].mean():+8.4f} "
            f"{x['p'][w].mean():8.1f} {x['q'][w].mean():+8.1f} {x['trip'].max():5.0f}")
    out(f"{'TOT':>3} {'':>4} {sum(x['sb'] for x in rows):7.0f} {'':7} {plant_pp:8.4f} "
        f"{plant_slope:+9.5f} {'':7} {'':8} {tp:8.1f} {tq:+8.1f}")
    for s, ok in checks:
        out(f"  {'ok  ' if ok else 'FAIL'} {s}")
    out("")

    # ---------------------------------------------------------------- switches
    out("switches / relays (0 = closed / not tripped)")
    sw = {}
    for name in ("BRK30", "BRK31", "BRK32", "BRK37", "BRKFR", "OOS1", "S1", "S2", "S3", "S4", "S5", "S6"):
        try:
            sw[name] = get(f"Root/Main/{name}/0/1")[1]
            mx = sw[name].max()
            tfirst = t[np.argmax(sw[name] > 0.5)] if (sw[name] > 0.5).any() else float("nan")
            out(f"  {name:6s} max {mx:4.0f}   first>0.5 at {tfirst:8.3f} s")
        except Exception:
            out(f"  {name:6s} channel missing")
    for name in ("PBK30", "PBK31", "PBK32", "PBK37"):
        try:
            p = get(f"Root/Main/{name}/0/1")[1]
            out(f"  {name:6s} P {p[w].mean():+8.1f} MW   (window)")
        except Exception:
            pass
    out("  PBK vs unit POUT cross-check (sign of the breaker meter; M3):")
    for i, m in enumerate(mach):
        lab = MACH[best[i]][0]
        if lab == "39F":
            continue
        try:
            p = get(f"Root/Main/PBK{lab}/0/1")[1]
        except Exception:
            continue
        pout_mw = m["po"][w].mean() * MACH[best[i]][1]
        out(f"    PBK{lab} {p[w].mean():+9.1f} MW   POUT {pout_mw:+9.1f} MW   "
            f"{'same sign' if np.sign(p[w].mean()) == np.sign(pout_mw) else 'OPPOSITE sign'}"
            f"   ratio {p[w].mean() / pout_mw if abs(pout_mw) > 1 else float('nan'):.3f}")
    out("")

    # ---------------------------------------------------------------- tie + hvdc
    # M3 sign check (Session 24): the France multimeter's P reads POSITIVE INTO IBERIA. Established by
    # France POUT - French load (+1,938 MW = France exports) against the raw channel (+1,773 MW) in the
    # 2026-11-22 settle run c: same sign => the raw channel is an IMPORT. Flip it so that PTIE > 0 means
    # Spain -> France, as the plan's +335 MW row requires.
    pt_raw = get("Root/Main/PTIE/0/1")[1]
    pt = -pt_raw              # + = Spain -> France (export)
    qt = -get("Root/Main/QTIE/0/1")[1]
    ph9 = get("Root/Main/Ph9/0/1")[1]
    ph39 = get("Root/Main/Ph39/0/1")[1]
    try:
        vtie = get("Root/Main/VTIE/0/1")[1]
    except Exception:
        vtie = np.full_like(t, np.nan)
    try:
        v9 = get("Root/Main/V9/0/1")[1]
    except Exception:
        v9 = np.full_like(t, np.nan)
    dphi = (ph9 - ph39 + 180.0) % 360.0 - 180.0      # cos/sin of a difference; never a raw diff
    fr = mach[[i for i, m in enumerate(best) if MACH[m][0] == "39F"][0]]
    fr_net = fr["po"] * MACH[[m for m in best if MACH[m][0] == "39F"][0]][1] - LOAD_MW_FR
    out("AC tie (PTIE: Spain -> France; France meter, S = 1 MW, sign flipped from the raw channel per M3)")
    out(f"  PTIE  {pt[w].mean():+9.1f} MW   (min {pt[w].min():+9.1f}, max {pt[w].max():+9.1f}, "
        f"p-p {np.ptp(pt[w]):8.1f})   slope {np.polyfit(t[w], pt[w], 1)[0]:+8.2f} MW/s")
    out(f"  QTIE  {qt[w].mean():+9.1f} Mvar (min {qt[w].min():+9.1f}, max {qt[w].max():+9.1f})")
    out(f"  VTIE  {vtie[w].mean():9.4f} pu = {vtie[w].mean()*400:7.1f} kV")
    out(f"  V9    {v9[w].mean():9.4f} pu = {v9[w].mean()*400:7.1f} kV")
    out(f"  Ph9 {ph9[w].mean():+8.2f} deg   Ph39 {ph39[w].mean():+8.2f} deg   "
        f"single-valued: {np.ptp(ph9[w]) < 1 and np.ptp(ph39[w]) < 1}")
    out(f"  d(theta) = {np.rad2deg(np.arcsin(np.sin(np.deg2rad(dphi[w].mean())))):+8.2f} deg (wrapped)")
    out(f"  sign check: France POUT - French load = {fr_net[w].mean():+9.1f} MW "
        f"vs PTIE {pt[w].mean():+9.1f} MW  ->  {'consistent' if np.sign(fr_net[w].mean()) != np.sign(pt[w].mean()) else 'CHECK'}")
    out(f"  tie angle from C2 formula: asin(P*X/V^2) with X = 45 ohm, V = 400 kV -> "
        f"{np.rad2deg(np.arcsin(min(1.0, abs(pt[w].mean()) * 45.0 / 400.0**2))):.2f} deg for |P| = {abs(pt[w].mean()):.0f} MW")
    out("")
    hv = {c: get(f"Root/Main/HVDC_T/{c}/0/1")[1] for c in ("ID", "IQ", "VD", "VQ", "VDF", "TRIP", "VA_PU")}
    hp = mm(hv["VD"] * hv["ID"] + hv["VQ"] * hv["IQ"], n20) * SB_HVDC
    hq = mm(hv["VD"] * hv["IQ"] - hv["VQ"] * hv["ID"], n20) * SB_HVDC
    out("HVDC (dq x Sbase 1000 MVA; negative = export to France)")
    out(f"  P {hp[w].mean():+9.1f} MW  (min {hp[w].min():+9.1f}, max {hp[w].max():+9.1f})   "
        f"Q {hq[w].mean():+7.1f} Mvar  VDF {hv['VDF'][w].mean():.4f} pu  TRIP {hv['TRIP'].max():.0f}")
    out("")

    # ---------------------------------------------------------------- balance
    fr_idx = [i for i, m in enumerate(best) if MACH[m][0] == "39F"][0]
    mp = sum(m["po"][w].mean() * MACH[best[i]][1] for i, m in enumerate(mach) if MACH[best[i]][0] != "39F")
    mq = sum(m["qo"][w].mean() * MACH[best[i]][1] for i, m in enumerate(mach) if MACH[best[i]][0] != "39F")
    mp_fr = mach[fr_idx]["po"][w].mean() * MACH[best[fr_idx]][1]
    gen = mp + tp
    # Iberia:  units + plants + AC import = load + HVDC export + losses   (pt > 0 = export, hp < 0 = export)
    implied_load = mp + tp - pt[w].mean() + hp[w].mean()
    out("C3 balance (Iberia only: the France machine is excluded; it is on the far side of the tie)")
    out(f"  Iberian units {mp:+9.1f} MW ({mq:+8.1f} Mvar)   plants {tp:+9.1f} MW ({tq:+8.1f} Mvar)"
        f"   generation {gen:+9.1f} MW        [France machine {mp_fr:+.1f} MW, excluded]")
    out(f"  PTIE {pt[w].mean():+9.1f} MW (+ = export to France)   HVDC {hp[w].mean():+9.1f} MW (negative = export)")
    out(f"  generation - PTIE + HVDC = {implied_load:+9.1f} MW = load + losses")
    out(f"  scheduled load {LOAD_MW:.1f} MW (19 Iberian loads at 1 pu, NP = 1) -> "
        f"implied losses {implied_load - LOAD_MW:+8.1f} MW = "
        f"{(implied_load - LOAD_MW) / gen * 100:+.2f} % of generation  "
        f"[0-3 % required; 0.01 pu of load voltage = {LOAD_MW*0.01:.0f} MW]")
    out("")

    # ---------------------------------------------------------------- gate table
    out(f"G7a / S2 gate rows, window {w0}-{w1} s, and first time each holds continuously to {w1} s")
    out(f"{'row':46} {'required':>18} {'measured':>22} {'verdict':>8} {'settled at':>11}")
    g = []

    def row(name, req, meas, ok, okarr, t_end=w1):
        g.append((name, req, meas, ok))
        out(f"{name:46} {req:>18} {meas:>22} {'PASS' if ok else 'FAIL':>8} {first_pass(t, okarr, t_end):11.3f}")

    ok_f = np.ones_like(t, bool)
    for m in mach:
        ok_f &= np.abs(m["f"] - 50.0) < 0.02
    row("all 5 machine f = 50.00 +- 0.02 Hz", "|f-50| < 0.02",
        f"{fmean:.4f} Hz", bool(np.all([abs(x.mean() - 50) < 0.02 for x in fwin])), ok_f)
    ok_sp = np.ones_like(t, bool)
    row("speed spread between machines < 5 mHz", "spread < 0.005",
        f"{spread*1000:.2f} mHz", spread < 0.005, np.ones_like(t, bool))
    row("speed p-p (each machine) < 10 mHz", "p-p < 0.010",
        f"{fpp*1000:.2f} mHz", fpp < 0.010, np.ones_like(t, bool))
    okv = np.ones_like(t, bool)
    row("collector VDF p-p < 0.005 pu", "p-p < 0.005", f"{plant_pp:.4f} pu",
        plant_pp < 0.005, np.ones_like(t, bool))
    row("collector VDF |drift| < 0.002 pu/s", "|slope| < 0.002", f"{plant_slope:.5f} pu/s",
        plant_slope < 0.002, np.ones_like(t, bool))
    trips = max(x["trip"].max() for x in rows)
    row("plant TRIP all 0 (18 plants)", "0", f"{trips:.0f}", trips < 0.5, np.ones_like(t, bool))
    brks = max(sw[n].max() for n in ("BRK30", "BRK31", "BRK32", "BRK37") if n in sw)
    row("BRK30/31/32/37 all 0 (closed)", "0", f"{brks:.0f}", brks < 0.5, np.ones_like(t, bool))
    brkf = sw.get("BRKFR", np.zeros_like(t)).max()
    row("BRKFR 0 (AC tie closed)", "0", f"{brkf:.0f}", brkf < 0.5, np.ones_like(t, bool))
    oos = sw.get("OOS1", np.zeros_like(t)).max()
    row("OOS1 0 (relay not latched)", "0", f"{oos:.0f}", oos < 0.5, np.ones_like(t, bool))
    row("PTIE = +335 +- 100 MW (Spain -> France)", "235..435",
        f"{pt[w].mean():+.1f} MW", 235 <= pt[w].mean() <= 435,
        np.abs(pt - 335.0) <= 100.0)
    row("HVDC P = 1,000 +- 10 MW export", "-990..-1010",
        f"{hp[w].mean():+.1f} MW", -1010 <= hp[w].mean() <= -990,
        np.abs(hp + 1000.0) <= 10.0)
    row("HVDC TRIP 0", "0", f"{hv['TRIP'].max():.0f}", hv["TRIP"].max() < 0.5,
        np.ones_like(t, bool))
    out("")

    # ---------------------------------------------------------------- WP7 step 5 targets
    gr = [x for x in rows if x["bus"] == "33" and abs(x["sb"] - 520.0) < 1.0]
    out("WP7 step 5 (fixed PF, Qmode 0) pre-event targets")
    if gr:
        out(f"  Granada collector (plant ch{gr[0]['k']}, bus 33) VDF {gr[0]['vdf'][w].mean():.4f} pu"
            f"   target 1.061 pu +-0.01  -> {'ok' if abs(gr[0]['vdf'][w].mean()-1.061)<=0.01 else 'OUT'}")
    out(f"  unit terminal VIT: {min(m['vit'][w].mean()*400 for m in mach):.1f} .. "
        f"{max(m['vit'][w].mean()*400 for m in mach):.1f} kV   (Iberian 400-420 kV required;"
        f" France 39F excluded in the band row)")
    out(f"  Iberian units QOUT: " + ", ".join(
        f"{MACH[best[i]][0]} {m['qo'][w].mean()*MACH[best[i]][1]:+.0f} Mvar"
        for i, m in enumerate(mach) if MACH[best[i]][0] != "39F"))
    out("")

    # ---------------------------------------------------------------- figures
    fig, ax = plt.subplots(4, 1, figsize=(11, 13), sharex=True)
    for i, m in enumerate(mach):
        ax[0].plot(t, m["f"], lw=0.8, label=f"ch{m['k']} bus {MACH[best[i]][0]}")
    ax[0].axvspan(w0, w1, color="k", alpha=0.08)
    ax[0].set(ylabel="machine f [Hz]", title=f"{a.label}: whole trace")
    ax[0].legend(ncol=3, fontsize=7)
    for b in BUSES:
        gset = [x for x in rows if x["bus"] == b]
        ax[1].plot(t, np.mean([x["vdf"] for x in gset], axis=0), lw=0.8, label=f"bus {b}")
    ax[1].axvspan(w0, w1, color="k", alpha=0.08)
    ax[1].set(ylabel="collector VDF [pu]")
    ax[1].legend(ncol=3, fontsize=7)
    ax[2].plot(t, pt, lw=0.9, label="PTIE [MW]")
    ax[2].plot(t, -hp, lw=0.9, label="-HVDC P [MW export]")
    ax[2].axvspan(w0, w1, color="k", alpha=0.08)
    ax[2].set(ylabel="tie / HVDC export [MW]")
    ax[2].legend(fontsize=7)
    ax[3].plot(t, dphi, lw=0.9, label="d(theta) Ph9-Ph39 [deg]")
    ax[3].axvspan(w0, w1, color="k", alpha=0.08)
    ax[3].set(xlabel="time [s]", ylabel="tie angle [deg]")
    ax[3].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(a.outdir, "settle_gate.png"), dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    for x in rows:
        ax[0].plot(t, x["p"], lw=0.6)
    ax[0].axvspan(w0, w1, color="k", alpha=0.08)
    ax[0].set(ylabel="plant P [MW]", title=f"{a.label}: 18 plants")
    for m in mach:
        ax[1].plot(t, m["po"], lw=0.8)
    ax[1].axvspan(w0, w1, color="k", alpha=0.08)
    ax[1].set(xlabel="time [s]", ylabel="machine POUT [pu]")
    fig.tight_layout()
    fig.savefig(os.path.join(a.outdir, "plants_units.png"), dpi=140)
    plt.close(fig)

    # zoom of the gate window: the "look at the figure" requirement (C1)
    wz = (t >= w0 - 1.0) & (t <= w1 + 0.5)
    fig, ax = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
    for i, m in enumerate(mach):
        ax[0].plot(t[wz], m["f"][wz], lw=1.0, label=f"bus {MACH[best[i]][0]}")
    ax[0].set(ylabel="f [Hz]")
    ax[0].legend(ncol=5, fontsize=7)
    for b in BUSES:
        gset = [x for x in rows if x["bus"] == b]
        ax[1].plot(t[wz], np.mean([x["vdf"] for x in gset], axis=0)[wz], lw=1.0, label=f"bus {b}")
    ax[1].set(ylabel="VDF [pu]")
    ax[1].legend(ncol=5, fontsize=7)
    ax[2].plot(t[wz], pt[wz], lw=1.0, label="PTIE")
    ax[2].plot(t[wz], -hp[wz], lw=1.0, label="-HVDC")
    ax[2].set(xlabel="time [s]", ylabel="MW")
    ax[2].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(a.outdir, "gate_window_zoom.png"), dpi=140)
    plt.close(fig)

    with open(os.path.join(a.outdir, "gate.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    npass = sum(1 for _, _, _, ok in g if ok)
    out(f"RESULT: {npass}/{len(g)} gate rows pass in {w0}-{w1} s")


if __name__ == "__main__":
    main()
