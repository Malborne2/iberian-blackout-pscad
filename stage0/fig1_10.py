"""Figure 1-10 (p.16): Carmona 400 kV voltage, Iberian frequency, CE frequency.

Output: data/targets_fig1-10.csv   (t_sim = seconds after 12:32:00)
        stage0/fig1-10_overlay.png (sanity check of the extraction)
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from digitise import Axis, Trace, extract, find, render, resample, words  # noqa: E402

PAGE = 16
OUT = Path(__file__).resolve().parents[1] / "data" / "targets_fig1-10.csv"

im = render(PAGE)
ws = words(PAGE)

# ---- calibration from the PDF text layer ---------------------------------
v_axis = Axis((find(ws, "500")[1], 500.0), (find(ws, "330")[1], 330.0))
f_axis = Axis((find(ws, "50.1")[1], 50.1), (find(ws, "47.4")[1], 47.4))
t50 = find(ws, "12:32:50")[0]
t35 = find(ws, "12:33:35")[0]
t_axis = Axis((t50, 50.0), (t35, 95.0))       # seconds after 12:32:00

print(f"V axis : 500 kV at y={find(ws,'500')[1]:.1f}, 330 kV at y={find(ws,'330')[1]:.1f}"
      f"  ({abs(v_axis.k)*10:.1f} px per 10 kV)")
print(f"f axis : 50.1 Hz at y={find(ws,'50.1')[1]:.1f}, 47.4 Hz at y={find(ws,'47.4')[1]:.1f}"
      f"  ({1/abs(f_axis.k):.1f} px per 0.1 Hz)")
print(f"t axis : 12:32:50 at x={t50:.1f}, 12:33:35 at x={t35:.1f}  ({t_axis.k*45/45:.3f} px/s)")

BOX = (int(t50) - 4, int(find(ws, "500")[1]) - 6, int(t35) + 6, 2048)
traces = [Trace("EC6501", "V_carmona_kV"),      # orange
          Trace("009EE3", "f_iberia_Hz"),       # cyan
          Trace("124093", "f_CE_Hz")]           # navy
raw = extract(im, BOX, traces)
for name, pts in raw.items():
    print(f"  {name}: {len(pts)} columns found")

cal = {"V_carmona_kV": v_axis, "f_iberia_Hz": f_axis, "f_CE_Hz": f_axis}
rows = resample(cal, raw, t_axis, 0.25)

OUT.parent.mkdir(exist_ok=True)
with OUT.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["t_sim_s", "V_carmona_kV", "f_iberia_Hz", "f_CE_Hz", "source"])
    w.writeheader()
    for r in rows:
        r["source"] = "Fig 1-10, p.16 (digitised, 1 px = 0.02 s / 0.22 kV / 0.0035 Hz)"
        w.writerow(r)
print(f"wrote {OUT} ({len(rows)} rows)")

# ---- overlay --------------------------------------------------------------
fig, ax = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
pts = [(r["t_sim_s"], r["V_carmona_kV"]) for r in rows if r["V_carmona_kV"] != ""]
ax[0].plot(*zip(*pts), ".-", ms=2, lw=0.8, color="tab:orange")
ax[0].axhline(435, color="m", lw=0.6); ax[0].axhline(360, color="c", lw=0.6)
ax[0].set_ylabel("Carmona 400 kV (kV)"); ax[0].grid(alpha=.3)
ax[0].set_ylim(330, 500); ax[0].set_title("digitised Fig 1-10, p.16")
for key, c in (("f_iberia_Hz", "tab:cyan"), ("f_CE_Hz", "navy")):
    pts = [(r["t_sim_s"], r[key]) for r in rows if r[key] != ""]
    ax[1].plot(*zip(*pts), ".-", ms=2, lw=0.8, color=c, label=key)
ax[1].set_ylim(47.4, 50.1); ax[1].set_ylabel("frequency (Hz)")
ax[1].legend(); ax[1].grid(alpha=.3); ax[1].set_xlabel("t_sim (s after 12:32:00)")
fig.tight_layout()
fig.savefig(Path(__file__).with_name("fig1-10_overlay.png"), dpi=110)

# ---- residual against PLAN.md A3 anchors ---------------------------------
anchors = [(50, 410, 50.00), (56, 420, 49.98), (58, 425, 49.94),
           (75, 430, 49.93), (77, 440, 49.9), (78, 447, 49.8),
           (80.2, None, 49.5), (80.6, None, 49.0), (82.0, 460, 48.0)]
print("\nA3 anchor residuals (digitised minus PLAN.md starter value):")
for ts, v, f in anchors:
    near = [r for r in rows if abs(r["t_sim_s"] - ts) <= 0.13]
    if not near:
        print(f"  t={ts:5.1f}s  no sample"); continue
    r = near[0]
    msg = f"  t={ts:5.1f}s"
    if v is not None and r["V_carmona_kV"] != "":
        msg += f"  V={r['V_carmona_kV']:6.1f} (plan {v:5.0f}, d={r['V_carmona_kV']-v:+6.1f})"
    elif v is not None:
        msg += "  V=(obscured)"
    if r["f_iberia_Hz"] != "":
        msg += f"  f={r['f_iberia_Hz']:6.3f} (plan {f:5.2f}, d={r['f_iberia_Hz']-f:+.3f})"
    else:
        msg += "  f=(obscured)"
    print(msg)
