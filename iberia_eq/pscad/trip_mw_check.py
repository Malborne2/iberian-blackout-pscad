r"""Check what a RES relay trip removes (S30 sec 25, test 5): per plant P = VD*ID and Q = -VD*IQ [pu of the plant
rating] in a window before and after its TRIP, and the residual current after the trip.

usage: python iberia_eq\pscad\trip_mw_check.py <tag> [--pre 0.40 0.50] [--post 0.70 1.10]
Pass: every tripped plant ends with |ID|, |IQ| < 0.02 pu (gate blocking removes the whole plant, Share1 = 1).
Writes iberia_eq\pscad\figs\trip_mw_<tag>.png (ID of every plant around the trip).
"""
import argparse, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from legacy_out import load
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

ap = argparse.ArgumentParser(); ap.add_argument("tag"); ap.add_argument("--pre", nargs=2, type=float, default=(0.40, 0.50))
ap.add_argument("--post", nargs=2, type=float, default=(0.70, 1.10)); a = ap.parse_args()
t, d = load(os.path.join(r"C:\PSCAD_work\v2_runs", a.tag), "v2")
inst = sorted({n.split(":")[0] for n in d if "RES_Plant" in n and n.endswith(":ID")})
pre = (t > a.pre[0]) & (t < a.pre[1]); post = (t > a.post[0]) & (t < a.post[1]); bad = 0
fig, ax = plt.subplots(figsize=(10, 4.5))
print(f"{'instance':16s} trip_t   P_pre  Q_pre   P_post  |ID|post |IQ|post")
for k in inst:
    ID, IQ, VD, TR = (d[f"{k}:{s}"] for s in ("ID", "IQ", "VD", "TRIP"))
    tt = t[np.argmax(TR > 0.5)] if (TR > 0.5).any() else None
    P0, Q0 = (VD * ID)[pre].mean(), (-VD * IQ)[pre].mean(); P1 = (VD * ID)[post].mean()
    ri, rq = np.abs(ID[post]).max(), np.abs(IQ[post]).max(); ok = tt is None or (ri < 0.02 and rq < 0.02); bad += not ok
    print(f"{k[-16:]:16s} {tt if tt is None else round(tt, 3)!s:7s} {P0:6.3f} {Q0:+6.3f}  {P1:6.3f}  {ri:7.4f}  {rq:7.4f} {'' if ok else '  <-- residual current'}")
    ax.plot(t, ID, lw=.7)
ax.axvspan(*a.pre, color="g", alpha=.08, label="pre window"); ax.axvspan(*a.post, color="r", alpha=.08, label="post window")
ax.set_xlabel("t [s]"); ax.set_ylabel("ID [pu of plant rating]"); ax.set_title(f"{a.tag}: d-axis current of all 21 RES plants around the relay trip")
ax.legend(); ax.grid(alpha=.3); fig.tight_layout()
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs", f"trip_mw_{a.tag}.png"); fig.savefig(out, dpi=110)
print(f"{'PASS' if not bad else 'FAIL'}: {len(inst) - bad} of {len(inst)} plants fully removed after trip; {out}")
