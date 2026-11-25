r"""Case A (forced replay, WP10.1) spec for stage12/make_variant.py, from stage6/event_table.csv (Table 3-1).

Clock: event 3 (Granada, report t = 57.220 s) at T0 + 1 s; the quiet 57.2 -> 76.4 s interval (no ES trips)
is shortened to 3 s; from event 4a (76.443 s) on the report's own timing is kept (k = 1):
    t_model = T0 + 1 + (t - 57.220)            for t <= 57.220
    t_model = T0 + 4 + (t - 76.443)            for t >= 76.443
Plant-type losses (PV / wind / thermo-solar): the 18 aggregate plants are tripped by `Tforce`, greedily, so
that the cumulative tripped MW tracks the report's cumulative loss (plant 1 = Granada takes event 3).
Machine losses: nuclear 1,045 MW (82.702) -> unit 31, nuclear 653 + 1,692 (83.515/83.590) -> unit 32 at
83.55, combined cycle 165 (80.10) -> unit 37, 166 + 87 (83.46/83.65) -> unit 30 at 83.55; via Ptrip steps.
Pump shedding, LFDD, the tie and the HVDC are NOT forced: they come from the model's relays.
usage: python stage12/caseA_spec.py <T0> <out.json> [psout window t0,t1 for plant MW]
"""
import csv, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
T0 = float(sys.argv[1]); out = sys.argv[2]
SB = {1: 3315.0, 2: 223.6, 3: 217.1, 4: 3122.6, 5: 841.1, 6: 210.6, 7: 735.8, 8: 526.5, 9: 440.7, 10: 306.8,
      11: 1552.2, 12: 795.6, 13: 169.0, 14: 3247.4, 15: 765.7, 16: 452.4, 17: 4071.6, 18: 520.0}
if len(sys.argv) > 3:   # measured plant MW from a settled PSOUT window
    import mhi.psout, numpy as np
    w0, w1 = (float(x) for x in sys.argv[3].split(","))
    ps = sys.argv[4]
    r = mhi.psout.File(ps).run(0)
    MW = {}
    for k in SB:
        g = {c: r.call(f"Root/Main/RES_Plant[{k}]/{c}/0/1", sep="/") for c in ("VD", "VQ", "ID", "IQ")}
        t = np.asarray(g["VD"].domain.data); m = (t >= w0) & (t <= w1)
        v = {c: np.asarray(x.data)[m] for c, x in g.items()}
        MW[k] = float(np.mean(v["VD"] * v["ID"] + v["VQ"] * v["IQ"]) * SB[k])
else:
    MW = {k: 0.88 * s for k, s in SB.items()}


def tm(t):
    return T0 + 1 + (t - 57.220) if t <= 57.3 else T0 + 4 + (t - 76.443)


ev = []
for r in csv.DictReader(open(ROOT / "stage6" / "event_table.csv", encoding="utf-8")):
    t = float(r["t_sim_s"])
    if r["country"] == "ES" and r["type"].startswith("Generation loss") and t >= 57.2 and \
            not any(k in r["description"] for k in ("Nuclear", "Combined cycle")):
        ev.append((t, float(r["mw_imbalance"])))
ev.sort()
plants = {"18": {"Tforce": round(tm(57.220), 4)}}   # Granada = RES_Plant[18] (520 MVA)
tripped = MW[18]; avail = {k for k in SB if k != 18}; cum = 0.0; log = [(57.22, 355.0, [18])]
for t, mw in ev:
    cum += mw
    if t < 57.3:
        continue
    now = []
    while avail:
        best = min(avail, key=lambda k: abs(tripped + MW[k] - (cum + 355.0)))
        if abs(tripped + MW[best] - (cum + 355.0)) < abs(tripped - (cum + 355.0)):
            tripped += MW[best]; avail.discard(best); now.append(best)
            plants[str(best)] = {"Tforce": round(tm(t), 4)}
        else:
            break
    if now:
        log.append((t, cum + 355.0, now))
units = {"31": {"Ttrip": round(tm(82.702), 4), "Ptrip": round(-1045.0 / 13548.0, 6)},
         "32": {"Ttrip": round(tm(83.55), 4), "Ptrip": round(-2345.0 / 15292.0, 6)},
         "37": {"Ttrip": round(tm(80.10), 4), "Ptrip": round(-165.0 / 12838.0, 6)},
         "30": {"Ttrip": round(tm(83.55), 4), "Ptrip": round(-253.0 / 6113.0, 6)}}
spec = {"plants": plants, "units": units, "ov_report": False,   # forced replay: OV relays stay parked
        "project": {"time_duration": str(round(tm(84.8) - T0 + 1.0, 1)), "sample_step": "500", "SnapType": "0"},
        "note": "Case A forced replay; clock: event 3 at T0+1, 76.443 at T0+4, real time after"}
json.dump(spec, open(out, "w"), indent=1)
for t, c, ks in log:
    print(f"report {t:7.3f} s -> model {tm(t):7.3f} s: cum report {c:6.0f} MW, trip plants {ks} "
          f"({sum(MW[k] for k in ks):.0f} MW)")
print(f"tripped {tripped:.0f} MW of plants; units {units}; duration {spec['project']['time_duration']} s")
