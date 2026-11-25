"""Stage 3c figure set: closed-loop dq current control on the converter bench (cv1)."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import mhi.psout

PSOUT = r"C:\PSCAD_work\cv1.gf81_x86\cv1.psout"
OUT = Path(r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model\results\stage3c_loop")
OUT.mkdir(parents=True, exist_ok=True)
V_BASE = 326.5986
CH = {"vd": "Root/Main/VD/0/1", "vq": "Root/Main/VQ/0/1",
      "id": "Root/Main/ID/0/1", "iq": "Root/Main/IQ/0/1",
      "vbr": "Root/Main/VbrA/0/1"}

data = {}
with mhi.psout.File(PSOUT) as f:
    run = f.run(0)
    for k, ch in CH.items():
        tr = run.call(ch, sep="/")
        data[k] = (np.asarray(tr.domain.data, dtype=float), np.asarray(tr.data, dtype=float))

t = data["vd"][0]
STRIDE = 20
sl = slice(None, None, STRIDE)


def save(fig, name):
    fig.tight_layout()
    p = OUT / name
    fig.savefig(p, dpi=130)
    plt.close(fig)
    print("wrote", p.name)


sel = (t >= 1.3) & (t <= 1.5)
print("stage 3c - closed loop on cv1, means 1.30-1.50 s")
for k in ("vd", "vq", "id", "iq"):
    y = data[k][1][sel]
    print(f"  {k}: mean {y.mean():+.4f}  min {y.min():+.4f}  max {y.max():+.4f}  std {y.std():.4f}")
P = (data["vd"][1] * data["id"][1] + data["vq"][1] * data["iq"][1])[sel]
Q = (data["vq"][1] * data["id"][1] - data["vd"][1] * data["iq"][1])[sel]
print(f"  P {P.mean():+.4f} pu = {P.mean()*300:+.0f} MW   (set 0.300 pu = 90 MW)")
print(f"  Q absorbed {Q.mean():+.4f} pu = {Q.mean()*300:+.0f} Mvar   (set 0.0526 pu = 16 Mvar)")

fig, axes = plt.subplots(2, 2, figsize=(13, 7.5))
ax = axes[0, 0]
for k, c in (("vd", "C0"), ("vq", "C1")):
    ax.plot(t[sl], data[k][1][sl], lw=0.8, color=c, label=k)
ax.set_title("dq grid voltage (PLL frame)")
ax.set_ylabel("pu"); ax.grid(alpha=0.3); ax.legend(fontsize=8)

ax = axes[0, 1]
for k, c in (("id", "C0"), ("iq", "C1")):
    ax.plot(t[sl], data[k][1][sl], lw=0.8, color=c, label=k)
ax.axhline(0.30, color="0.5", ls="--", lw=0.8)
ax.axhline(0.0526, color="0.5", ls=":", lw=0.8)
ax.set_title("dq currents with references (id 0.300 dashed, iq 0.053 dotted)")
ax.set_ylabel("pu"); ax.grid(alpha=0.3); ax.legend(fontsize=8)

ax = axes[1, 0]
Pp = (data["vd"][1] * data["id"][1] + data["vq"][1] * data["iq"][1]) * 300
Qp = (data["vq"][1] * data["id"][1] - data["vd"][1] * data["iq"][1]) * 300
ax.plot(t[sl], Pp[sl], lw=0.8, color="C2", label="P (MW)")
ax.plot(t[sl], Qp[sl], lw=0.8, color="C3", label="Q absorbed (Mvar)")
ax.set_xlabel("time (s)"); ax.set_ylabel("MW / Mvar"); ax.set_title("Power at the converter terminals")
ax.grid(alpha=0.3); ax.legend(fontsize=8)

ax = axes[1, 1]
ax.plot(t[sl], data["vbr"][1][sl] / V_BASE, lw=0.5, color="C4")
ax.set_xlabel("time (s)"); ax.set_ylabel("pu"); ax.set_title("Bridge terminal voltage, phase A")
ax.grid(alpha=0.3)

fig.suptitle("Stage 3c - closed-loop dq current control, Pset = 0.30 pu (id tracks; iq limit-cycles)", fontsize=11)
save(fig, "00_overview.png")
