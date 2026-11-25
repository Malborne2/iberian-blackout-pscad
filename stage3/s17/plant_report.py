"""Gate report for a RES_Plant bench run (Session 17).

usage: python plant_report.py <psout> [instance-group ...]
For each instance group (the channel path element, e.g. RES_Plant, RES_Plant_2) prints, over the
three PSET windows of the 0.5 -> 0.1 -> 0.5 pu pulse: id, iq (20 ms means), P and Q at the POI
from the fundamental phasors of VA_PU (POI voltage, pu) and IsrcA (current POI -> grid, kA),
and the POI current THD (2..60th harmonic, 0.18 s window).
Sign convention printed: P > 0 = plant exports, Q > 0 = plant injects (generator convention).
"""
import sys
import numpy as np
import mhi.psout

PSOUT = sys.argv[1]
GROUPS = sys.argv[2:] or ["RES_Plant"]
WINDOWS = [(0.30, 0.48, 0.50), (0.80, 0.98, 0.10), (1.30, 1.48, 0.50)]
VBASE_PK = 400 * np.sqrt(2 / 3)                 # kV


def read(run, path):
    try:
        tr = run.call(path, sep="/")
    except Exception:
        return None, None
    return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)


def phasor(t, y, lo, hi, h=1, f=50.0):
    s = (t >= lo) & (t < hi)
    tt, yy = t[s], y[s]
    w = 2 * np.pi * f * h
    return 2 * np.mean(yy * np.exp(-1j * w * tt))


with mhi.psout.File(PSOUT) as f:
    run = f.run(0)
    for g in GROUPS:
        ch = {k: read(run, f"Root/Main/{g}/{k}/0/1") for k in
              ("ID", "IQ", "VD", "VQ", "IsrcA", "VA_PU", "TRIP", "VbrA")}
        t = ch["ID"][0]
        print(f"=== {g}")
        for lo, hi, ps in WINDOWS:
            s = (t >= lo) & (t <= hi)
            idm, iqm = ch["ID"][1][s].mean(), ch["IQ"][1][s].mean()
            line = f" {lo:.2f}-{hi:.2f} PSET {ps:.2f}: id {idm:+.4f} iq {iqm:+.4f} vd {ch['VD'][1][s].mean():+.4f} vq {ch['VQ'][1][s].mean():+.4f}"
            ti, ia = ch["IsrcA"]
            I1 = phasor(ti, ia, lo, hi)
            harm = [abs(phasor(ti, ia, lo, hi, h)) for h in range(2, 61)]
            thd = np.sqrt(np.sum(np.square(harm))) / abs(I1) * 100
            line += f" | I1 {abs(I1):.4f} kA THD {thd:.2f} %"
            if ch["VA_PU"][0] is not None:
                V1 = phasor(ch["VA_PU"][0], ch["VA_PU"][1], lo, hi) * VBASE_PK   # kV peak
                S = 3 * 0.5 * V1 * np.conj(I1)   # MVA; IsrcA = ICA-ILA, +ve POI->grid (checked vs grid source P,Q)
                line += f" | P {S.real:+7.1f} MW Q {S.imag:+7.1f} Mvar |V| {abs(V1)/VBASE_PK:.4f} pu"
            print(line)
        if ch["TRIP"][0] is not None:
            tr = ch["TRIP"][1]
            print(f"  TRIP max {tr.max():.2f}" + (f" first at {ch['TRIP'][0][np.argmax(tr > 0.5)]:.4f} s" if tr.max() > 0.5 else ""))
        print(f"  id pp(0.3-1.5 s) {np.ptp(ch['ID'][1][t > 0.3]):.3f}  |id| max {np.abs(ch['ID'][1][t > 0.3]).max():.3f}")
