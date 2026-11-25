"""Digitise the report's secondary target figures (PLAN.md A3).

Figures and the values they constrain
-------------------------------------
Fig 3-5  p.127  Carmona 400 kV voltage + Spain net active-power exchange, 12:32:00-12:33:00
Fig 3-7  p.129  cumulative (net load increase + generation loss) and 400 kV Vmax
                panel a: 12:32:00-12:33:30, panel b: 12:33:10-12:33:24
Fig 4-89 p.299  frequency at La Cereal 400 kV, simulation vs PMU
Fig 4-90 p.299  voltage at La Cereal 400 kV, simulation vs PMU
Fig 4-91 p.300  Spain-France active-power exchange, simulation vs PMU

Axis calibration comes from the PDF text layer (tick-label centres); the plot frame
is found from the page's own border lines; curves are separated by exact RGB colour.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from digitise import Axis, Trace, extract, render, resample, words  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
HERE = Path(__file__).parent


def lab(ws, text, ywin):
    hits = [(x, y) for w, x, y in ws
            if w == text and ywin[0] <= y <= ywin[1]]
    if not hits:
        raise SystemExit(f"label {text!r} not found in y-window {ywin}")
    return hits[0]


def frame(im, ywin, grid_y, frac=0.5):
    a = np.asarray(im).astype(int)
    r, g, b = (a[..., i] for i in range(3))
    grey = (abs(r - g) < 14) & (abs(g - b) < 14) & (r < 235)
    y0, y1 = int(ywin[0]), int(ywin[1])
    sub = grey[y0:y1]
    rows = sub.sum(axis=1)
    ycs = np.where(rows > frac * im.width)[0]
    if not len(ycs):
        raise SystemExit("could not find the plot frame (rows)")
    # horizontal extent: the longest run of grey pixels along the gridline nearest
    # to the tick label (text-box centres sit ~1 line-width away from the line)
    best = max(range(int(grid_y) - 25, int(grid_y) + 26),
               key=lambda y: grey[y].sum())
    row = np.where(grey[best])[0]
    if not len(row):
        raise SystemExit("gridline row is empty")
    runs, run = [], [row[0]]
    for x in row[1:]:
        if x - run[-1] <= 8:
            run.append(x)
        else:
            runs.append(run); run = [x]
    runs.append(run)
    run = max(runs, key=len)
    return int(run[0]), int(ycs.min()) + y0, int(run[-1]), int(ycs.max()) + y0


def run(name, page, ywin, axis_defs, traces, t_def, step=0.25, box=None):
    """axis_defs: {trace: ((labelA, valA), (labelB, valB))}; t_def: ((labelA, tA), (labelB, tB))."""
    im = render(page)
    ws = words(page)
    if box is None:
        grid_y = lab(ws, next(iter(axis_defs.values()))[0][0], ywin)[1]
        x0, y0, x1, y1 = frame(im, ywin, grid_y)
        box = (x0 + 1, y0 + 1, x1, y1)
    print(f"  box x={box[0]}..{box[2]}  y={box[1]}..{box[3]}")

    (la, va), (lb, vb) = t_def
    t_axis = Axis((lab(ws, la, ywin)[0], va), (lab(ws, lb, ywin)[0], vb))
    print(f"  t: {la}@{lab(ws, la, ywin)[0]:.0f}px -> {va}s ; {lb}@{lab(ws, lb, ywin)[0]:.0f}px -> {vb}s"
          f"  ({t_axis.k:.4f} s/px)")

    cal = {}
    for nm, ((sa, qa), (sb, qb)) in axis_defs.items():
        ya, yb = lab(ws, sa, ywin)[1], lab(ws, sb, ywin)[1]
        cal[nm] = Axis((ya, qa), (yb, qb))
        print(f"  {nm:<18} {sa}@{ya:.0f}px -> {qa} ; {sb}@{yb:.0f}px -> {qb}"
              f"  ({abs(cal[nm].k):.4f} per px)")

    raw = extract(im, box, [Trace(c, nm) for c, nm in traces])
    for nm, pts in raw.items():
        print(f"    -> {nm:<18} {len(pts):4d} columns")

    rows = resample(cal, raw, t_axis, step)
    out = DATA / f"targets_{name}.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["t_sim_s", *raw.keys(), "source"])
        w.writeheader()
        for r in rows:
            r["source"] = f"Fig {name[3:]}, p.{page} (digitised)"
            w.writerow(r)

    fig, ax = plt.subplots(figsize=(10, 4))
    for nm, pts in raw.items():
        ax.plot([t_axis.at(x) for x in pts], [cal[nm].at(y) for y in pts.values()],
                ".", ms=1, label=nm)
    ax.legend(); ax.grid(alpha=.3); ax.set_xlabel("t_sim (s after 12:32:00)")
    ax.set_title(f"{name}  p.{page}")
    fig.tight_layout()
    fig.savefig(HERE / f"{name}_overlay.png", dpi=100)
    plt.close(fig)
    print(f"  -> {out.name}: {len(rows)} rows\n")
    return rows


if __name__ == "__main__":

    print("Fig 3-5 (p.127)")
    run("fig3-5", 127, (410, 1470),
        {"P_exchange_MW": (("5,000", 5000.0), ("3,200", 3200.0)),
         "V_carmona_kV": (("435", 435.0), ("395", 395.0))},
        [("1171B8", "P_exchange_MW"), ("D95318", "V_carmona_kV")],
        (("12:32:00", 0.0), ("12:33:00", 60.0)))

    print("Fig 3-7 panel a (p.129)")
    run("fig3-7a", 129, (540, 1500),
        {"cum_imbalance_MW": (("5,000", 5000.0), ("0", 0.0)),
         "Vmax_400kV": (("405", 405.0), ("435", 435.0))},
        [("0071BC", "cum_imbalance_MW"), ("D95218", "Vmax_400kV")],
        (("12:32:00", 0.0), ("12:33:30", 90.0)))

    print("Fig 3-7 panel b (p.129)")
    run("fig3-7b", 129, (1700, 2520),
        {"cum_imbalance_MW": (("16,000", 16000.0), ("2,000", 2000.0)),
         "Vmax_400kV": (("410", 410.0), ("460", 460.0))},
        [("0071BC", "cum_imbalance_MW"), ("D95218", "Vmax_400kV")],
        (("12:33:10", 70.0), ("12:33:24", 84.0)),
        box=(443, 1676, 1965, 2483))

    print("Fig 4-89 (p.299)")
    run("fig4-89", 299, (1230, 1940),
        {"f_sim_Hz": (("50.0", 50.0), ("47.0", 47.0)),
         "f_pmu_Hz": (("50.0", 50.0), ("47.0", 47.0))},
        [("124093", "f_sim_Hz"), ("BF017E", "f_pmu_Hz")],
        (("33:17.568", 77.568), ("33:22.752", 82.752)))

    print("Fig 4-90 (p.299)")
    run("fig4-90", 299, (2250, 2970),
        {"V_sim_pu": (("1.25", 1.25), ("0.95", 0.95)),
         "V_pmu_pu": (("1.25", 1.25), ("0.95", 0.95))},
        [("124093", "V_sim_pu"), ("BF017E", "V_pmu_pu")],
        (("33:17.568", 77.568), ("33:22.752", 82.752)))

    print("Fig 4-91 (p.300)")
    run("fig4-91", 300, (490, 1190),
        {"P_sim_MW": (("6,000", 6000.0), ("–6,000", -6000.0)),
         "P_pmu_MW": (("6,000", 6000.0), ("–6,000", -6000.0))},
        [("124093", "P_sim_MW"), ("BF017E", "P_pmu_MW")],
        (("33:17.568", 77.568), ("33:22.752", 82.752)))
