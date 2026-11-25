"""Stage 0 / G0 check: does data/events.csv reproduce the report's own totals?

Source of every expected number: FINAL REPORT (ENTSO-E Expert Panel, 20 March 2026),
files in notes/. Page numbers are PDF page numbers.

Run:  python stage0/check_events.py
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "events.csv"

# p.131, Table 3-2 "Focus of power disconnection from 12:33:20 to 12:33:25"
# Spain only: p.200 (LFDD total 8,504.9 MW) and p.203 (2,756 MW pumps in Spain).
TABLE_3_2 = {
    "Combined Cycle": 719.0,
    "Load": -8504.3,
    "Nuclear Power Plant": 3390.0,
    "Pumped Hydro": -2756.0,
    "PV": 3198.1,
    "PV and Thermo-Solar": 85.3,
    "Wind": 48.9,
    "Wind and PV": 168.0,
    "Total generation": 7609.3,
    "Total demand + Pump": -11260.3,
}
# p.200 Table 3-10 / p.202 Table 3-13 (independent cross-check of the Load row)
LFDD_ES_STEPS = [1176, 1669, 1575, 1524, 1294, 1267]      # total 8,505
LFDD_PT_STEPS = [315, 293, 315, 323, 282, 427]           # total 1,955

EVENT5 = {"5a1", "5a2", "5a3", "5b1", "5b2", "5b3", "5b4"}


def secs(t: str) -> float:
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


T0 = secs("12:32:00")
LO, HI = secs("12:33:20.000") - T0, secs("12:33:25.000") - T0


def load() -> list[dict]:
    with CSV.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def mw(r: dict) -> float:
    v = (r["mw_imbalance"] or "").strip()
    return float(v) if v else 0.0


def main() -> int:
    R = load()
    lines: list[str] = []
    fails = 0
    unresolved: list[str] = []

    def emit(s: str = "") -> None:
        print(s.encode("utf-8", "replace").decode("utf-8", "replace")
              .encode(sys.stdout.encoding or "utf-8", "replace").decode(sys.stdout.encoding or "utf-8", "replace"))
        lines.append(s)

    def chk(label: str, got: float, want: float, tol: float) -> None:
        nonlocal fails
        ok = abs(got - want) <= tol
        fails += not ok
        emit(f"{'PASS' if ok else 'FAIL'}  {label:<40} csv={got:10.2f}  report={want:10.2f}  d={got-want:+8.2f}  tol={tol}")

    emit(f"events.csv rows: {len(R)}   clusters: {len({r['cluster'] for r in R})}")

    # ---------- A2 anchors (PLAN.md A2, from p.117-120 and p.130) ----------
    emit("\n== A2 anchor sums ==")
    c3 = sum(mw(r) for r in R if r["cluster"] == "3")
    c4 = sum(mw(r) for r in R if r["cluster"] in ("4a", "4b"))
    c5 = sum(mw(r) for r in R if r["cluster"] in EVENT5)
    n5 = sum(1 for r in R if r["cluster"] in EVENT5)
    chk("event 3 (Granada transformer)", c3, 355.0, 0.5)
    chk("event 4a+4b (Badajoz)", c4, 727.0, 0.5)
    chk("event 5 (seven trips)", c5, 928.0, 0.5)
    ok = n5 == 7
    fails += not ok
    emit(f"{'PASS' if ok else 'FAIL'}  event 5 row count = {n5} (report: seven trips)")
    # p.118 lists the individual values; check the largest one (550 MW, 5a2)
    big = [mw(r) for r in R if r["cluster"] == "5a2"]
    chk("event 5a2 (largest of the seven)", big[0] if big else 0.0, 550.0, 0.05)

    # ---------- Table 3-2 (p.131), 12:33:20.000-12:33:25.000 ----------
    emit("\n== Table 3-2, window 12:33:20.000-12:33:25.000, Spain rows only ==")
    win = [r for r in R if LO <= secs(r["time"]) - T0 <= HI]
    gen: dict[str, float] = defaultdict(float)
    for r in win:
        if r["country"].strip() != "ES" or mw(r) <= 0:
            continue
        if r["type"].startswith(("Generation loss", "Net load disconnection")):
            gen[r["description"].split(",")[0].strip()] += mw(r)
    mapping = {
        "Combined Cycle": ["Combined cycle"],
        "Nuclear Power Plant": ["Nuclear"],
        "PV": ["PV"],
        "PV and Thermo-Solar": ["PV and thermo-solar"],
        "Wind": ["Wind"],
        "Wind and PV": ["Wind and PV"],
    }
    for cat, keys in mapping.items():
        chk(cat, sum(gen[k] for k in keys), TABLE_3_2[cat], 0.05)
    chk("Total generation", sum(gen.values()), TABLE_3_2["Total generation"], 0.05)

    # pumps in Spain: report 2,756 MW (p.203)
    es_pump = -sum(mw(r) for r in win
                   if r["country"].strip() == "ES" and mw(r) < 0 and "Pump" in r["description"])
    c50 = -sum(mw(r) for r in win if r["cluster"] == "50")
    emit(f"INFO  Pumped Hydro, all ES pump rows: csv={-es_pump:.2f}  report={TABLE_3_2['Pumped Hydro']:.2f}")
    emit(f"NOTE  ES pump rows = {es_pump:.2f} MW; rows of cluster 50 = {c50:.2f} MW are "
         f"UV / loss-of-synchronism trips (footnotes 23-24), not frequency shedding.")
    chk("Pumped Hydro (cluster 50 excluded)", -(es_pump - c50), TABLE_3_2["Pumped Hydro"], 0.05)

    # demand: the report's Load row is the Spanish LFDD total (p.200)
    es_load = -sum(mw(r) for r in win
                   if r["country"].strip() == "ES" and mw(r) < 0 and "Pump" not in r["description"])
    ip_load = -sum(mw(r) for r in win if r["country"].strip() == "IP" and mw(r) < 0)
    emit(f"\n  Spanish demand rows in window      : {es_load:9.2f} MW")
    emit(f"  Rows with country 'IP' in window   : {ip_load:9.2f} MW  (6 rows, one per LFDD step)")
    emit(f"  Report Load (Table 3-2 / p.200)    : {TABLE_3_2['Load']:9.2f} MW")
    emit(f"  Report LFDD steps ES (p.200) total : {sum(LFDD_ES_STEPS):9.2f} MW")
    emit(f"  Report LFDD steps PT (p.202) total : {sum(LFDD_PT_STEPS):9.2f} MW")
    emit(f"  ES + IP rows                       : {es_load + ip_load:9.2f} MW")
    emit("  => the Load row of Table 3-2 is NOT reproducible from events.csv as written.")
    unresolved.append("Table 3-2 Load row (-8,504.3 MW) vs events.csv demand rows (see above)")

    # ---------- internal consistency ----------
    emit("\n== internal consistency ==")
    detail = sum(mw(r) for r in R if r["cluster"] in ("2a", "2b"))
    summary = sum(mw(r) for r in R if r["cluster"] == "2a/b")
    ok = abs(detail - summary) <= 0.5
    fails += not ok
    emit(f"{'PASS' if ok else 'FAIL'}  cluster 2a/b: detail rows {detail:.2f} vs summary {summary:.2f} "
         f"(report prints 'Total 208' over 208.46 of detail rows)")

    bad = [r for r in R if r["type"].startswith("Generation loss") and mw(r) < 0]
    ok = not bad
    fails += not ok
    emit(f"{'PASS' if ok else 'FAIL'}  all generation-loss rows positive ({len(bad)} violations)")

    empty_mw = [r for r in R if not (r["mw_imbalance"] or "").strip()
                and r["type"] not in ("Line trip", "Tie-line trip", "Generation evacuation line trip", "HVDC block")]
    ok = not empty_mw
    fails += not ok
    emit(f"{'PASS' if ok else 'FAIL'}  every non-line-event row has an MW value ({len(empty_mw)} exceptions)")

    # rows whose description field carries page text rather than a technology
    dirty = [r for r in R if "Grid Incident" in r["description"] or "Final Report" in r["description"]]
    emit(f"INFO  {len(dirty)} row(s) with page-header text inside the description field: "
         f"{[(r['cluster'], r['description'][:40]) for r in dirty]}")

    if fails:
        emit(f"\nRESULT: {fails} CHECK(S) FAILED")
    elif unresolved:
        emit(f"\nRESULT: numeric checks pass; {len(unresolved)} item(s) UNRESOLVED:")
        for u in unresolved:
            emit(f"        - {u}")
    else:
        emit("\nRESULT: ALL CHECKS PASS")
    (Path(__file__).with_name("check_events.out.txt")).write_text("\n".join(lines), encoding="utf-8")
    return 0 if fails == 0 and not unresolved else 1


if __name__ == "__main__":
    sys.exit(main())
