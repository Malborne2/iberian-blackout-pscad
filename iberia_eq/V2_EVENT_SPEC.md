# v2 event-replay specification (12:32:00 – 12:33:24)

Draft 1, 2026-11-26, agent: claude-main (RUNLOG S30 §14). Every number traces to `iberia_eq/SOURCES.md`; the design
rules come from `iberia_eq/V2_BUS_UNIT_LIST.md` §3A/§4. Status: **D** data ready, **B** needs a bench, **M** in the model.

Model state this starts from: the v2 single-line case (162 nodes of 200, 47 pages of 64, 1 subsystem). The cold settle
(S30 §13) gives snapshot t = 28 s. The replay maps report time 12:32:00 to model time **t0 = 30 s** (after the settle);
12:33:24 is t0 + 84 s.

## 1. What must come out by itself (the emergent part, the replay gate)

| target | value | source |
|---|---|---|
| France export, 12:32:00 → 12:32:57 | ≈ 1,500 → ≈ 450 MW | [CA] p.104 (SOURCES §12.1) |
| net demand rise in the minute | ≈ 550 MW | [CA] p.88 |
| 400 kV max voltage, events 3 → 4a | 421.8 → 427.8 kV; 432.7 / 435.6 / 441.6 kV at 76.9 / 77.6 / 78.4 s | Fig 3-7a, §5 |
| order and times of the plant trips 4a…6b | Table 3-3 (19 rows) | §4 |
| frequency curve, collapse | Fig 3-5 [FR-dig] | §7 |
| France AC tie peak / reversal | import 4,609 MW AC at 19.620; export 5,587 at 20.520 | [CA] p.105, §12.5 |
| pump and LFDD steps crossed | 49.5 Hz at 20.180, 49.0 at 20.600 … 48.0 at 22.040 | [CA] p.57, §12.5 |

## 2. Forced drivers (causes outside the model)

| # | driver | realisation | numbers | status |
|---|---|---|---|---|
| F1 | events 2a/2b: wind/PV down | step reductions of RES `PSET` on the north (2a) and south (2b) aggregates at the listed times | 2a 174.9 MW (11 rows, 12:32:05–53), 2b 34.1 MW (7 rows) = 208 MW, Table 3-1 | D |
| F2 | RES secondary-regulation set-point ramp | linear ramp on all RES aggregates, pro-rata to zone RES | −270 MW over 57 s ([CA] p.88: 480 − 208) [inf] | D |
| F3 | Portugal schedule | the ES→PT flow is an outcome of the PT balance: ramp PT-N/PT-S load or generation by −545 MW, 12:27–12:32 (starts before t0, so it is part of the pre-event state; check that the snapshot has ≈ 2,100 MW) | 2,545 → 2,000 MW | D, check |
| F4 | line trips with unknown cause | breaker per line (+0 nodes if it replaces a series element, otherwise +3) | 9 Loeches–Arganda 220 kV (19.971; not in the equivalent), 36a/b (21.872 / 21.980), 42 | D, mostly outside the 400 kV equivalent → skip 9 and 36a |
| F5 | Morocco tie trip | breaker on the Morocco cable (MA-B side), opened at 16a 20.229 (Moroccan under-frequency relay with transfer trip) | +3 nodes | D; may become emergent with a 49.3 Hz relay ([CA] p.55: 49.314 Hz at 16b) |
| F6 | nuclear trips | `Ttrip`/`Ptrip` on G2 (1,045 at 22.702), G1 Almaraz II (653 at 23.515), G3 (1,692 at 23.590) | Table 3-1 41a/41c/46 | D (forced: auxiliaries' frequency protection, outside the model) |
| F7 | HVDC France block | the CAT HVDC load (1,000 MW export, Pmode 1) set to 0 at 51 23.960 | varrlc set-point | D |

## 3. Protection and defence plan (emergent)

| # | element | realisation | settings | status |
|---|---|---|---|---|
| P1 | RES plant overvoltage relays (19 trips, Table 3-3) | RES_Plant `Vt1/Tt1`, `Vt2/Tt2` per plant: timed stage plus instantaneous stage on the 400 kV-side voltage | Vt = "V at trip" from Table 3-3 (400 kV side, effective threshold incl. frozen collector taps, [CA] p.90–95); Badajoz-type structure 435 kV/1.5 s + 440 kV inst. ([CA] p.94); rows with V "NA" take the neighbour's value [inf] | D, set as **offsets from each plant's pre-event model voltage** (design change B) |
| P2 | rooftop PV (< 1 MW) OV trips, latched | `src_ccin` per zone, tripped fraction rising with bus voltage, no reconnection in 84 s ([CA] p.84–86) | calibrate to event 1 (+317 MW net load, 12:32:00–57) and Fig 1-13 | B (new block, bench first) |
| P3 | Spanish pump shedding | M1 Duero (1,049 MW) and M2 Ebro (1,017 MW) behind `breaker3`: f < 49.5 Hz → stage 1, f < 49.3 Hz → stage 2 (PLD steps + breaker, bench lt6 §28) | 2,168 MW at 49.5 and 588 at 49.3 (Table 3-9); the model carries 2,066 of the 3,031 MW connected, so split 2,066 in the same 79 / 21 % ratio [inf]; the remaining 965 MW sit in zone loads → frequency-switched load steps | D |
| P4 | Portuguese pump shedding | M3…M7 = one step each: breaker opens at 49.8 / 49.7 / 49.6 / 49.5 / 49.3 Hz | 381 / 450 / 438 / 470 / 359 MW (Table 3-11, matches the model exactly) | D |
| P5 | Spanish LFDD | per zone load: R/L scaled up (G reduced) in 6 steps at 49.0…48.0 Hz, using the **actual** % (Table 3-10), not the plan | 4.0 / 5.6 / 5.3 / 5.1 / 4.4 / 4.3 % of load | D (0 nodes, control only) |
| P6 | Portuguese LFDD + industry | same on PT-N/PT-S; industry 218 MW at 49.2 Hz | 315 / 293 / 315 / 323 / 282 / 427 MW (Table 3-13) | D |
| P7 | Portuguese DSO generation on frequency | two frequency-staged reductions of the PT RES/netted generation (150 ms delay) | 49.8 Hz → 321 MW, 49.5 Hz → 575 MW (Table 3-4); Table 3-1 event 24 estimates 1,073 MW in total; PT TSO units trip at f < 47.5 Hz | D |
| P8 | France out-of-step (DRS / Vic–Baixas) | breaker on the France source branch, opened by an out-of-step detector: angle FR–CAT through ±180° twice (second slip), or forced at 31a 21.407 | +3 nodes; detector = `trig` on the FR/CAT PMU angles (pmu.py logic in PSCAD: multimeter `Ph` difference via cos/sin, skill P3) | B |
| P9 | France tie meter | multimeter on the FR source branch (P, Q, Ph) | +3 nodes (can be the same series element as P8 if the breaker replaces it later) | D |
| P10 | France source impedance | Z of source3 so that the AC peak import is 4,609 MW | currently 20 Ω/85° [inf] | calibrate in replay |

## 4. Node and page budget

| item | nodes |
|---|---|
| now | 162 |
| P8 France breaker + P9 meter | +6 |
| F5 Morocco breaker | +3 |
| P3/P4 pump breakers | 0: all 7 PumpUnits are already behind `breaker3` (build_v2.py) |
| P2, P5, P6, F1, F2, F6, F7 | 0 (control signals on existing branches) |
| **total** | **≈ 171 of 200** (P3/P4 breakers already counted in the 162) |

Pages: control logic stays on Main (no new module instances), so 47 of 64.

## 5. Open data items

1. (done) Table 3-4 transcribed (SOURCES §13).
2. Fig 1-13 / §4.3.4: rooftop-PV trip fraction against voltage (P2).
3. Morocco inertia H 4.0 s source (SOURCES §11 open item).
4. Where the 965 MW of Spanish pumping not in M1/M2 is in the zone loads (P3).

## 6. Order of work

1. Settle snapshot (S30 §13) with the open calibrations: machine P −6 %, frequency drift, RES-bus oscillation.
2. Drivers F1, F2, F6, F7 and meters P9 (no new physics, 0–3 nodes): a "forced replay" run to see the
   pre-collapse minute.
3. Relays P1 from the snapshot voltages (design change B).
4. Pumps P3/P4, LFDD P5/P6, PT DG P7: the frequency-collapse part.
5. Ties P8/F5 and France Z calibration P10.
6. Rooftop PV P2 (bench first).
7. Replay gate against §1.
