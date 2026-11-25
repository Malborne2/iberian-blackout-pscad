"""Windowed report for the G2a bench run (sb17): step at t=TSTEP, fault at t=TFLT.

Reads the .psout directly (no PSCAD connection).

Run: python analyze_run.py <psout> [TSTEP] [TFLT] [DFLT]
"""
import sys
from statistics import fmean

import mhi.psout

PATH = sys.argv[1]
TSTEP = float(sys.argv[2]) if len(sys.argv) > 2 else 8.0
TFLT = float(sys.argv[3]) if len(sys.argv) > 3 else 14.0
DFLT = float(sys.argv[4]) if len(sys.argv) > 4 else 0.1

WANT = ("Vinf", "Vt", "V400", "VIT", "POUT", "QOUT", "Pgrid", "Qgrid",
        "Wspd", "ExInit", "VREFO", "EFD0ch", "Flt", "FltOp")


def load():
    out = {}
    with mhi.psout.File(PATH) as f:
        run = f.run(0)
        paths = {str(p): str(p) for _, p in run.trace_paths()}
        t = run.call("PGB:Domain", sep="/").data
        for name in WANT:
            hits = [p for p in paths if p.endswith(f"/{name}/0/1")]
            if not hits:
                continue
            out[name] = list(run.call(hits[0], sep="/").data)
        out["__t"] = list(t)
    return out


def win(vals, t, t0, t1):
    return [v for tt, v in zip(t, vals) if t0 <= tt <= t1]


d = load()
t = d["__t"]
print(f"samples={len(t)}  t={t[0]:.4f}..{t[-1]:.4f}")

TIMES = [0.05, 0.2, 0.5, 1.0, 2.0, 4.0, 6.0, TSTEP - 0.1, TSTEP + 0.2, TSTEP + 1.0,
         TSTEP + 2.0, TFLT - 1.0, TFLT + 0.05, TFLT + 0.2, TFLT + 0.5, TFLT + 1.0,
         TFLT + 2.0, TFLT + 4.0, t[-1]]
hdr = "chan".ljust(8) + "".join(f"{x:>10.2f}" for x in TIMES)
print(hdr)
for name, vals in d.items():
    if name.startswith("__"):
        continue
    row = name.ljust(8)
    for x in TIMES:
        seg = win(vals, t, x, x + 0.02)
        row += f"{fmean(seg):>10.4f}" if seg else f"{'--':>10}"
    print(row)

print("\nextremes")
for name, vals in d.items():
    if name.startswith("__"):
        continue
    tail = win(vals, t, TFLT + DFLT + 0.5, t[-1])
    pre = win(vals, t, 6.0, TSTEP - 0.2)
    print(f"  {name:<8} all min={min(vals):>10.4f} max={max(vals):>10.4f}   "
          f"pre-step mean={fmean(pre):>10.4f}   after-fault min={min(tail):>10.4f} "
          f"max={max(tail):>10.4f}")

# settling: last time VIT (or V400) leaves +-0.01 of its final value
for name in ("VIT", "V400", "Vinf"):
    vals = d.get(name)
    if not vals:
        continue
    endv = fmean(win(vals, t, t[-1] - 0.5, t[-1]))
    dev = [(tt, v) for tt, v in zip(t, vals) if abs(v - endv) > 0.01 and tt > TFLT + DFLT]
    print(f"  {name}: last deviating sample t={dev[-1][0]:.3f}" if dev else f"  {name}: within +-0.01 of {endv:.4f} for the whole post-fault window")
