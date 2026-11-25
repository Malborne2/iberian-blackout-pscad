"""Build the full Case A plant-side cascade schedule (S22, G6).

Takes the report's plant-type generation loss (PV / wind / thermo-solar, ES) from
`stage6/event_table.csv`, compresses the 12:32:57.2-12:33:21.5 span into the 6 s budget, and assigns
trips to the 16 per-plant Force channels so that the achieved cumulative loss tracks the report.

Measured inputs (run 82, adopted lever-3 point): plant MW per channel.
Compression:  t_sim = 2.5 + (t_report - 77.22) * SCALE,  SCALE = 0.465  ->  2.5 .. 4.5 s,
leaving 1.5 s of post-cascade window inside the 6 s run.

Nuclear / CCGT / hydro losses (4,109 MW of the report's 11,921) are NOT plant-type and are not forced
here - they are machine-side trips the per-plant nets cannot reach. Recorded, not silently dropped.

usage: python stage6/build_caseA_schedule.py [--emit]
"""
import argparse
import csv
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLANT_DESC = ("PV", "Wind", "PV and thermo-solar", "Wind and PV", "PV, wind, and thermo-solar")
T0REP = 77.22          # cluster 3, 12:32:57.22 in t_sim seconds
SIM0 = 2.5
SCALE = 0.465

# channel -> measured MW at the adopted lever-3 point (run 82); 1 and 16 have no Force net
DISPATCH = {2: 125, 3: 123, 4: 1770, 5: 316, 6: 78, 7: 274, 8: 197, 9: 166, 10: 115, 11: 584,
            12: 458, 13: 97, 14: 1866, 15: 446, 17: 2339, 18: 1867}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true")
    a = ap.parse_args()

    curve = []
    with open(ROOT / "stage6" / "event_table.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["country"] != "ES" or not r["type"].startswith("Generation loss"):
                continue
            d = r["description"].strip()
            if not any(d.startswith(p) for p in PLANT_DESC):
                continue
            t_rep = float(r["t_sim_s"])
            if t_rep < T0REP:          # only the cascade itself, not clusters 1/2
                continue
            curve.append((t_rep, float(r["mw_imbalance"])))
    curve.sort()

    target_end = 6345.0                      # report plant-type cumulative at 12:33:21.5
    plants = sorted(DISPATCH.items(), key=lambda kv: kv[1])   # smallest first
    forced, cum_rep, cum_sim = [], 0.0, 0.0

    for t_rep, mw in curve:
        cum_rep += mw
        if cum_rep > target_end:
            break
        # trip the smallest remaining plant while the report curve is ahead of what we have forced
        # add while the report curve stays ahead by at least half the plant (accept <=50 % overshoot)
        while plants and cum_rep - cum_sim >= 0.5 * plants[0][1]:
            ch, m = plants.pop(0)
            t_sim = SIM0 + (t_rep - T0REP) * SCALE
            forced.append((ch, m, round(t_sim, 2)))
            cum_sim += m

    # close the residual gap with the smallest remaining plant if we are still well short
    if plants and cum_sim < 0.85 * cum_rep:
        ch, m = plants.pop(0)
        forced.append((ch, m, round(SIM0 + (curve[-1][0] - T0REP) * SCALE, 2)))
        cum_sim += m

    print(f"forced {len(forced)} plants, {cum_sim:.0f} MW  (report plant-type target {cum_rep:.0f} MW)")
    print(f"{'t_sim':>6s} {'ch':>4s} {'MW':>6s} {'cum_sim':>8s} {'cum_rep@t':>10s}")
    acc = 0.0
    for ch, m, ts in forced:
        acc += m
        # report cumulative at that sim time
        rep = sum(v for t, v in curve if SIM0 + (t - T0REP) * SCALE <= ts + 1e-9)
        print(f"{ts:6.2f} {ch:4d} {m:6d} {acc:8.0f} {rep:10.0f}")

    spec = ",".join(f"{ch}:{ts}" for ch, m, ts in forced)
    print("\n--force spec:\n" + spec)
    if a.emit:
        (ROOT / "stage6" / "caseA_force_spec.txt").write_text(spec + "\n", encoding="utf-8")
        print("\nwritten: stage6/caseA_force_spec.txt")


if __name__ == "__main__":
    main()
