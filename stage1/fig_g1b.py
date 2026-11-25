"""G1b - does flattening the PI line modules change anything?

Compares two runs of `iberia4` (before / after the flattening) channel by channel:

  * every multimeter Pd / Qd / Vd            (9 meters)
  * every SyncUnit VIT / POUT / QOUT / Wspd / THETA   (5 units)
  * every RES_Plant VD / ID / IQ / VDF / TRIP          (2 plants)
  * every PGB: Pg5..Pg9, Vg5..Vg9, Ph31..Ph39

Instances are identified by a *measured signature* (rule L2), not by the `[n]` index: for each
kind the two runs' instances are matched by nearest signature in the window, and the mapping is
printed. Identity by index is reported separately so a swap would be visible.

Figures are written only to the folder given on the command line (rule F1).

usage: python stage1\\fig_g1b.py <pre.psout> <post.psout> <outdir> [--window 2.0 3.0]
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mhi.psout

PRE, POST, OUT = sys.argv[1], sys.argv[2], Path(sys.argv[3])
window = (2.0, 3.0)
if "--window" in sys.argv:
    i = sys.argv.index("--window")
    window = (float(sys.argv[i + 1]), float(sys.argv[i + 2]))
OUT.mkdir(parents=True, exist_ok=True)

TOL = 1e-3          # 0.1 % relative, the G1b clause
MULTIMETERS = range(1, 10)
UNITS = range(1, 6)
PLANTS = range(1, 3)
PGB = [f"Pg{k}" for k in range(5, 10)] + [f"Vg{k}" for k in range(5, 10)] + [f"Ph{k}" for k in range(31, 40)]


def load(path):
    """Return {(kind, n, chan): (t, y)} for every channel that exists."""
    d = {}
    with mhi.psout.File(path) as f:
        r = f.run(0)

        def get(p):
            tr = r.call(p, sep="/")
            return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)

        for k in MULTIMETERS:
            for c, sub in (("Pd", 2), ("Qd", 3), ("Vd", 4)):
                try:
                    d[("mm", k, c)] = get(f"Root/Main/multimeter[{k}]/{sub}/{c}")
                except Exception:
                    pass
        for k in UNITS:
            for c in ("VIT", "POUT", "QOUT", "Wspd", "THETA"):
                try:
                    d[("su", k, c)] = get(f"Root/Main/SyncUnit[{k}]/{c}/0/1")
                except Exception:
                    pass
        for k in PLANTS:
            for c in ("VD", "ID", "IQ", "VDF", "TRIP"):
                try:
                    d[("pl", k, c)] = get(f"Root/Main/RES_Plant[{k}]/{c}/0/1")
                except Exception:
                    pass
        for nm in PGB:
            try:
                d[("pgb", nm, "1")] = get(f"Root/Main/{nm}/0/1")
            except Exception:
                pass
    return d


def mean_in(d, key, lo, hi):
    t, y = d[key]
    m = (t >= lo) & (t <= hi)
    if not m.any():
        return float("nan")
    return float(np.mean(y[m]))


pre = load(PRE)
post = load(POST)
lo, hi = window
print(f"window {lo}-{hi} s; pre {PRE}; post {POST}")
print(f"channels: pre {len(pre)}, post {len(post)}; "
      f"only pre {sorted(set(pre) - set(post))[:8]}; only post {sorted(set(post) - set(pre))[:8]}")


def signature(d, kind, n, chans):
    return np.array([mean_in(d, (kind, n, c), lo, hi) for c in chans])


def match(d_pre, d_post, kind, ns, chans):
    """Greedy nearest-signature matching; returns [(n_pre, n_post)]."""
    sig_p = {n: signature(d_pre, kind, n, chans) for n in ns if (kind, n, chans[0]) in d_pre}
    sig_q = {n: signature(d_post, kind, n, chans) for n in ns if (kind, n, chans[0]) in d_post}
    pairs, used = [], set()
    for n, s in sig_p.items():
        best, bd = None, None
        for m, s2 in sig_q.items():
            if m in used:
                continue
            scale = np.maximum(np.abs(s), 1e-9)
            dist = float(np.max(np.abs(s2 - s) / scale))
            if bd is None or dist < bd:
                best, bd = m, dist
        if best is not None:
            pairs.append((n, best))
            used.add(best)
    return pairs


rows = []          # (label, pre_mean, post_mean, rel_diff, abs_diff)
mapping = {}

for kind, ns, chans, label in (
    ("mm", list(MULTIMETERS), ["Pd", "Qd", "Vd"], "multimeter"),
    ("su", list(UNITS), ["POUT", "QOUT", "VIT"], "SyncUnit"),
    ("pl", list(PLANTS), ["ID", "IQ", "VD"], "RES_Plant"),
):
    pairs = match(pre, post, kind, ns, chans)
    mapping[kind] = pairs
    print(f"\n{label} identification by measured ({', '.join(chans)}) signature: "
          + ", ".join(f"{a}->{b}" for a, b in pairs))
    for a, b in pairs:
        for c in [k[2] for k in pre if k[0] == kind and k[1] == a]:
            if (kind, b, c) not in post:
                continue
            v1 = mean_in(pre, (kind, a, c), lo, hi)
            v2 = mean_in(post, (kind, b, c), lo, hi)
            ad = abs(v2 - v1)
            rd = ad / abs(v1) if abs(v1) > 1e-12 else ad
            rows.append((f"{label}[{a}->{b}] {c}", v1, v2, rd, ad))

for key in sorted({k for k in pre if k[0] == "pgb"}):
    if key in post:
        v1 = mean_in(pre, key, lo, hi)
        v2 = mean_in(post, key, lo, hi)
        ad = abs(v2 - v1)
        rd = ad / abs(v1) if abs(v1) > 1e-12 else ad
        rows.append((f"{key[1]}", v1, v2, rd, ad))

rows.sort(key=lambda r: -r[3])
print(f"\n{'channel':28} {'pre':>14} {'post':>14} {'rel diff':>11} {'abs diff':>11}  verdict")
for lab, v1, v2, rd, ad in rows:
    verdict = "ok" if (rd <= TOL or ad <= 1e-9 or abs(v1) < 1e-6) else "FAIL"
    print(f"{lab:28} {v1:14.8g} {v2:14.8g} {rd:11.3e} {ad:11.3e}  {verdict}")

worst = rows[0] if rows else None
n_fail = sum(1 for r in rows if not (r[3] <= TOL or r[4] <= 1e-9 or abs(r[1]) < 1e-6))
if worst:
    print(f"\nG1b: {len(rows)} channels compared, {n_fail} outside 0.1 %; "
          f"worst = {worst[0]} {worst[3]:.2e}")
else:
    print("no rows")

mm_rows = [r for r in rows if r[0].startswith("multimeter")]
oth_rows = [r for r in rows if not r[0].startswith("multimeter")]
for nm, sel in (("multimeter", mm_rows), ("all other", oth_rows)):
    if sel:
        w = max(sel, key=lambda r: r[3])
        print(f"  {nm:12}: {len(sel):2d} channels, max rel diff {w[3]:.3e} ({w[0]}), "
              f"outside 0.1 %: {sum(1 for r in sel if r[3] > TOL and r[4] > 1e-9)}")

fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for a, b in mapping["su"]:
    t, y = pre[("su", a, "VIT")]
    ax[0, 0].plot(t, y, lw=0.8, label=f"pre unit {a}")
    t, y = post[("su", b, "VIT")]
    ax[0, 0].plot(t, y, ls="--", lw=0.8, label=f"post unit {b}")
ax[0, 0].set_title("SyncUnit VIT: pre (solid) vs post (dashed)"); ax[0, 0].set_ylabel("V [pu]")
for a, b in mapping["pl"]:
    t, y = pre[("pl", a, "VD")]
    ax[0, 1].plot(t, y, lw=0.8, label=f"pre plant {a} VD")
    t, y = post[("pl", b, "VD")]
    ax[0, 1].plot(t, y, ls="--", lw=0.8, label=f"post plant {b} VD")
ax[0, 1].set_title("Plant VD: pre vs post"); ax[0, 1].set_ylabel("pu")
for a, b in mapping["mm"]:
    if ("mm", a, "Pd") not in pre or ("mm", b, "Pd") not in post:
        continue
    t, y = pre[("mm", a, "Pd")]
    ax[1, 0].plot(t, y, lw=0.8)
    t, y = post[("mm", b, "Pd")]
    ax[1, 0].plot(t, y, ls="--", lw=0.8)
ax[1, 0].set_title("Multimeter Pd: pre (solid) vs post (dashed)"); ax[1, 0].set_ylabel("Pd")
for a, b in mapping["su"]:
    t, y = pre[("su", a, "Wspd")]
    ax[1, 1].plot(t, y / 2 / np.pi, lw=0.8)
    t, y = post[("su", b, "Wspd")]
    ax[1, 1].plot(t, y / 2 / np.pi, ls="--", lw=0.8)
ax[1, 1].set_title("Machine frequency: pre (solid) vs post (dashed)"); ax[1, 1].set_ylabel("f [Hz]")
for a in ax.flat:
    a.grid(alpha=0.3); a.legend(fontsize=6); a.set_xlabel("t [s]")
fig.suptitle("G1b - iberia4 before vs after flattening the PI line modules")
fig.tight_layout()
fig.savefig(OUT / "00_pre_vs_post.png", dpi=110)

fig2, ax2 = plt.subplots(figsize=(9, 4))
ax2.barh([r[0] for r in rows], [max(r[3], 1e-12) for r in rows])
ax2.set_xscale("log")
ax2.axvline(TOL, color="r", ls="--", label="0.1 % gate")
ax2.set_xlabel("relative difference"); ax2.set_title("G1b channel-by-channel difference")
ax2.legend(); ax2.grid(alpha=0.3, axis="x")
fig2.tight_layout(); fig2.savefig(OUT / "01_relative_differences.png", dpi=110)
print("written", OUT)
