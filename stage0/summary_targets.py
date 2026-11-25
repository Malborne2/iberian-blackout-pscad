"""Print the digitised targets at the times PLAN.md quotes, so the numbers can be audited."""
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


def show(name, times, cols=None):
    p = DATA / f"targets_{name}.csv"
    rows = [{k: (float(v) if v not in ("",) and k != "source" else v) for k, v in r.items()}
            for r in csv.DictReader(p.open(encoding="utf-8"))]
    cols = cols or [k for k in rows[0] if k not in ("t_sim_s", "source")]
    print(f"\n{name}  ({len(rows)} rows, {rows[0]['t_sim_s']:.2f}..{rows[-1]['t_sim_s']:.2f} s)")
    for t in times:
        near = min(rows, key=lambda r: abs(r["t_sim_s"] - t))
        vals = "  ".join(f"{c}={near[c]:8.2f}" if isinstance(near[c], float) else f"{c}={near[c]}"
                         for c in cols)
        print(f"  t={near['t_sim_s']:6.2f}  {vals}")
    for c in cols:
        v = [r[c] for r in rows if isinstance(r[c], float)]
        if v:
            print(f"    {c}: min={min(v):.2f} max={max(v):.2f}")


show("fig1-10", [50, 56, 57.2, 58, 75, 77, 78, 79, 80, 80.2, 80.6, 81.5, 82, 83])
show("fig3-5", [0, 15, 30, 45, 57])
show("fig3-7a", [0, 57.2, 70, 76.4, 80])
show("fig3-7b", [70, 76.4, 77, 78, 79, 80, 81])
show("fig4-89", [77.568, 78.5, 79.5, 80.5, 81.5, 82.752])
show("fig4-90", [77.568, 78.5, 79.5, 80.5, 81.5, 82.752])
show("fig4-91", [77.568, 78.5, 79.5, 80.5, 81.5, 82.752])
