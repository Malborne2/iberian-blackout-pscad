# Iberian blackout in PSCAD — plan v1.3 for the remaining work

**v1.3 (2026-11-23 afternoon, Session 27 — Claude, with the user):** read **§1d** first. (1) **Event fidelity
before prevention**: no P1–P7 run until the replay matches the report (§1d.1). (2) **What a snapshot freezes** is
now known from the generated Fortran (§2b-v1.2 S13, `stage12\snap_live.py`). (3) The pre-event reactive balance is
wrong (load buses 1.15 pu, units absorbing 7.4 Gvar); Batch 2b (§3a) fixes it with parallel cold settles.
v1.2 is kept as `stage0\PLAN_v1.2_before_S27b.md`.

**v1.2 (2026-11-23, Session 27 — Claude, with the user):** from S27 on **Claude is the executor** (no separate
executor agent; `EXECUTOR_PROMPT.md` is frozen). Read §0, the new **§1c** and **§2b-v1.2** first: work is done in
**batches of parallel runs** (§3a). §1c overrides §1b and the old §3a where they differ. v1.1 is kept as
`stage0\PLAN_v1.1_before_S27.md`.

**v1.1 (2026-11-22, Session 25 — Claude, with the user):** read the new **§1b** first; it overrides §0–§3a
where they differ. The working case is now **`C:\PSCAD_work\s25\ib6.pscx`** (generator
`stage12\prepare_ib6.py`), and every test starts from the settled snapshot **`ib6b_settled32.snp`** (t = 32 s).
ib5 and its S24 dispatch-ceiling conclusions are withdrawn (RUNLOG Session 25 §1). v1.0 is kept as
`stage0\PLAN_v1.0_before_S25.md`.

**v1.0 (2026-11-21, Session 23 — review of Session 22 by Claude, with the user):** read §0, §1a and the
new §2b first. They override everything below them. §1a lists the S22 conclusions that were **wrong**, so
they are not repeated. The working case is now **`C:\PSCAD_work\s23\ib5.pscx`**, made by
`stage11\prepare_ib5.py`. Every event test now starts from a **snapshot** of a settled state.
v0.9 is kept as `stage0\PLAN_v0.9_before_S23.md`.

**v0.9 (2026-11-17, Session 20):**

- WP5 rewritten: the grid must be made reactively *surplus*, as in the report.
- New §2b, accelerated testing (mandatory; **replaced in v1.0**).
- Rules P1, T4, T5, R3, M5.
- Decisions D10–D12.
- Status board updated after Sessions 19/19b.

**For the executor agent.** v0.7 written 2026-11-16 after Session 17. That session was a review of
Sessions 1–16 by a second agent, plus Stage 3 carried forward. v0.8 (2026-11-17, after Session 18)
marks WP1 (governor) done.

The old v0.6 plan, now **`..\PLAN_OLD.md`** (one folder up), stays the architecture reference:
Parts A, B, D and E there are unchanged and still apply. **This file replaces PLAN_OLD Part C (work
order) and Part F (execution) from Stage 3b onwards.** Where the two disagree, this file wins.
Every "PLAN B3", "PLAN F3c" etc. in `RUNLOG.md` Sessions 1–17 means `PLAN_OLD.md`.

**From S27 the executor is Claude**, who maintains this plan with the user; rule P1 (read-only) applied to the former executor agent. Status goes into `RUNLOG.md` and `STATUS.md`.
Proposed plan changes go into the RUNLOG as "proposed plan change: …".

---

## 0. The ten-line version (v1.2)

1. Tools: the MCP `pscad_*` tools for editing/inspection; parallel runs go through `stage12\run_instance.py`
   (own PSCAD instance each, §2b S8). If `pscad_status` fails, rule T1.
2. The working case is **`C:\PSCAD_work\s27<x>\ib6.pscx`** — the S27 bundle (§1c.2), the best of the three
   trim brackets — and its settled snapshot. The project is **always named `ib6`** (a snapshot needs `ib6.map`).
3. **No event in a cold start, ever.** Settle once (cold, 32 s, snapshot every 4 s), then every test is a short
   warm run from the snapshot (§2b S1–S7).
4. **Work in batches, not in sequence (§3a).** All structural changes of a batch go into **one** generator
   script, **one** build and **one** cold settle (or parallel brackets of it); the experiments of the batch then
   run **in parallel** (≤ 8, §2b S8) from that snapshot.
5. Before a long run, a **0.3–0.5 s smoke run** from the same snapshot proves the warm start, the new channels
   and the build (≈ 2 min wall). Smoke runs are cheap; long cold runs are not — minimise them.
6. One change per *experiment*: each parallel run differs from its batch control in one stated thing (`spec.json`).
7. Every sign (P, Q, current direction) is checked against a second measurement; every machine is printed (C4).
8. A gate passes only with numbers **and** figures, both produced by one script from the run's own `.psout`.
9. The RUNLOG entry is written as results land, including unfinished work and its state.
10. When something takes more than **3 batches** without progress, stop and write down what was measured.

---

## 1d. Session 27 (afternoon) — fidelity first, the snapshot rule, and where the event replay stands (overrides §1c, §3a)

1. **Order of work (user, 2026-11-23):** replicate the event with high fidelity **first**: the pre-event state
   (C7 band), the sequence and timing of trips, the 400 kV voltage ramp (Fig 3-7a: 421.8 → 427.8 kV between
   events 3 and 4a, then 432.7 / 435.6 / 441.6 kV at 76.9 / 77.6 / 78.4 s), frequency, PTIE (Fig 4-91), and
   `BRKFR` at 81.407 s. **Prevention runs (WP11) wait** until the replay gate in §3a "Batch F" passes. Parallel
   slots go to fidelity brackets.
2. **Case B as written cannot be emergent.** The report itself has no trip between event 3 and event 4a, and 4a/4b
   happened with the 400 kV maximum at 1.07 pu. The emergent replay is **Case B2**: events 3, 4a and 4b forced
   (Granada = PSOUT plant 18 at T0+1; 4a 582 MW → plant 5 (580 MW) at T0+4.000; 4b 145 MW → plant 6 (145 MW) at
   T0+4.377, both bus 34), every later trip from the relays (`stage12\batch1b.py`, scored by `stage12\b2_score.py`).
3. **What B2 showed on the S27 state (RUNLOG S27 §13):** the cascade starts on the peaks of the 20 µs numerical
   17 Hz mode (0 s relays, 39 ms after 4a), 18.5 GW in 2 s, `BRKFR` 3.9 s early; with a ≥ 60 ms relay filter
   nothing trips (margin 0.002 pu). Root cause: **the reactive balance is the reverse of the report's**. Iberian
   load buses are at 1.14–1.165 pu (report 400–420 kV), loads are constant current with QO = 0, and units
   32/37/30 absorb ≈ 7.4 Gvar on KA 40 voltage control (report: ≈ 74 Mvar), so they clamp the voltage after
   each trip and the report's sustained rise never forms.
4. **P1 from a snapshot is not bumpless** (b4: trips before the event). P1 needs its own re-settle when WP11 opens.
5. **Tools added:** `snap_live.py` (frozen/live classifier), `relay_emul.py` (offline relay emulation with a
   moving-average measurement; valid to the first trip, validated to 1 ms), `b2_score.py` (Fig 3-7a scoring on
   the Case A clock), `add_bundle_s29.py` (relay measurement lag `Trel`, LIVE), `batch2b.py` (cold-settle brackets).
6. **Open structural question:** the four Iberian units total 47.8 GVA (sized to the report's 119 GW·s at H 2.5),
   so their reactive range is far larger than the 11.95 GW of real conventional generation. If Batch 2b cannot
   bring their absorption near the report's value, this is the next structural item.

## 1c. Session 27 — parallel runs, the one-build bundle, the regrouped work order (overrides §1b, §3a)

**1. Up to 8 runs at once (measured).** The Educational licence allows **8 simultaneous EMTDC runs**
(help: Getting_Started/Dimension_Limits). One EMTDC run is single-threaded (multi-threading is only across
electrical sub-systems; Educational has one), and each run also costs its PSCAD GUI ≈ 2 cores of plot
processing, so plan for ≈ 3 cores per run (24 logical cores → 7–8 runs). GPU / compiler: the build is
already `-O2`; the "GPU sparse" option does not help a 197-node network. Use `sample_step` 500 µs in event
runs to cut the GUI load (output only).
- **How:** `stage12\make_variant.py <case.pscx> <folder> <spec.json>` makes one experiment folder (event-only
  edits; project name stays **`ib6`**, so the `.map` and the snapshot stay valid — never rename);
  `stage12\run_instance.py <folder> --snap <file.snp>` launches **its own PSCAD instance** (mhi.pscad), builds,
  copies the snapshot in *after* the build, runs, waits, quits, and logs `run_instance.log` (+ the run config,
  which must show `-start-snap`). Start several in the background, ≥ 20 s apart.
- **Trap:** the agent shell sets `NoDefaultCurrentDirectoryInExePath=1`; a PSCAD launched from it cannot run
  `ib6.exe` ("not recognized"). `run_instance.py` clears it.
- **Trap:** `pscad_set_project_parameters` can reset `StartType` to 0 — always pass `StartType` explicitly and
  read it back in the `.pscx`.
- The MCP-driven PSCAD remains usable at the same time (it is one more instance).

**2. The S27 bundle (one build, `stage12\add_bundle_s27.py`):** every remaining event is now a *parameter*:
- `RES_Plant` **`Tforce`** [s] — per-plant forced trip time (Case A schedule, Case B initiator, WP8.4);
- `SyncUnit` **`Ttrip`/`Ptrip`** — a turbine-power step (pu of `Sbase`, negative = loss) for partial unit trips
  (the 1,045 MW nuclear trip etc.); whole-unit trips stay on `BRK3x`;
- **pump shedding** (WP9.3): 2,168 MW at 49.5 Hz (buses 3 + 21), 588 MW at 49.3 Hz (bus 27), latched;
- **tie** 90 → 83 Ω per circuit (WP8.3: 120° slip at ≈ 3.7 GW).
- Also corrected: bus-36 collector tap 0.9385 (its tap winding is on the collector side, V ∝ tap).
Cold settles (32 s, snapshots every 4 s) were run as **three dispatch-trim brackets in parallel**
(`C:\PSCAD_work\s27a/b/c`, PTIE 0 / +400 / −400 MW at constant system total); the best becomes the case.

**3. Work order:** the batches in §3a.

---

## 1b. Session 25 — ib6, the settled snapshot, and what changed in the method (overrides §0–§3a)

Evidence: RUNLOG Session 25 §1–§8.

1. **Working case `C:\PSCAD_work\s25\ib6.pscx`**, made by `stage12\prepare_ib6.py` from the S24 ib5 (same 15
   recorders, NODES 197). It differs from ib5 by:
   - a **start-up sequence** in `SyncUnit`: ideal source until 0.52 s, rotor locked at 50 Hz until `TREL` 5 s, then
     free with the turbine power = sample-and-hold of the filtered electrical power at release (bumpless);
   - **`Pmec` is now a dispatch trim** in pu of `Sbase`, ramped in over 5–7 s. After the ramp it is a plain
     additive term, so a new value acts as a **step from a snapshot** (warm trim, no cold start);
   - **network strength** to the report's short-circuit level (p.217 ⇒ 13–17 GVA): lines R, L ÷ 2.6, transformer
     `Tmva` × 2.6, line charging × 1.3, France ties unchanged; SCR at the collectors 2.6–4.6 (ib5 1.0–1.9);
   - set-points from an AC power flow (`stage12\acflow.py`, `ib6_setpoints.py`), reactors 1.5 Gvar at bus 29,
     1 Gvar at bus 1, 1 Gvar at bus 9; France P0 4,195.8 MW (the HVDC feeds the ideal DC source, not France).
2. **The settled state** `ib6b_settled32.snp` (in `C:\PSCAD_work\s25\ib6.gf81_x86\` and `archive\`), gate
   30–32 s 12/14: swing settled (speed p-p 3.7 mHz, spread 0.7 mHz), PTIE +323 MW, HVDC 1,002 MW, no trips.
   **Known deviations:** f **49.962 Hz** (≈ 830 MW short, voltage-driven demand), Iberian units 13.6 GW (report
   11.95), collectors 1.072–1.102 (Granada target 1.061), bus 38 0.940, 18 Hz plant ripple 0.009–0.013 pu.
3. **Snapshot mechanics (replaces §2b S4):**
   - `remove_time_offset` must be **false** (`Advanced` = 38879; set by XML edit, the API rejects it). With the
     default, PSCAD restarts the clock at 0 and the time-driven start-up sequence fires again.
   - Time then continues from the snapshot time, and **`time_duration` is the length added** (not the end time).
     All event times are absolute (> 32 s from `ib6b_settled32.snp`).
   - A snapshot is tied to the project's own `.map` (do not rename or copy the project to use it), to the build
     dimensions and to the **time step**.
   - Long runs: `SnapType` INCREMENTAL_MANY_FILES with `SnapTime` = interval, so a stopped run is not lost.
4. **Time step stays 20 µs** (S25 §7): 50 µs gives only 1.8× speed and triples the 18 Hz ripple, 100 µs gives 2.4×
   with a 7.5× ripple and a 1 GW France artefact; 500 µs is below the 1,650 Hz carrier.
5. **WP7 now means:** (a) the 18 Hz ripple — first the 10 µs falsifier (5 s cold start), then the plant control
   discretisation; (b) the voltage profile (step 5 levers) by warm re-settle from `ib6b_settled32.snp`; (c) the
   Iberian `Pmec` trim (+≈ 830 MW at the present voltages, less after (b)) for f = 50.00 ± 0.02 with PTIE kept at
   +335 ± 100. Then G7a and WP8+.
6. **Withdrawn (S24):** "the converter fleet is stable only at ≤ 0.70 `Pref` / ≤ 0.89 pu" and "the synchronous
   fleet must carry 19–20 GW" — properties of the too-weak ib5 equivalent, not of the report's state.

---

## 1a. Session 23 review — what was wrong in S22, and what was changed in the model

Checked against the archived PSOUTs in `C:\PSCAD_work\s21` (read only, no new simulation). **Do not
repeat these conclusions; they are withdrawn.**

| # | S22 claim | What the data show | Consequence |
|---|---|---|---|
| 1 | Pre-event states "settled", event at 3 s of a 6 s run | Every cold start has an Iberia-vs-France swing of **±0.6 Hz**, with collector voltages ±0.1–0.3 pu, lasting **8–10 s** (run 16, 20 s). Run 99 before its 3 s event: Granada 0.76–1.02 pu, f 49.3–50.8 Hz. Settled f is **49.84 Hz**, not 50 | **Every Stage 6–10 number (runs 85–124) was measured inside the start-up swing.** All are void as evidence. The method is replaced by §2b |
| 2 | "Network-limited by the `psse`-internal network"; "most demand is inside `psse`"; "4 GW of the bus-39 boundary is inside `psse`" | The `psse` definition is **empty** (two sticky notes). All 25,237.5 MW of load is in the 19 Main `fixed_load`s: **`PO` is per phase** (8,412.5 × 3). The 4 GW is the **4,531 MW load at bus 39** | Bus-37 band, LFDD and French-end conclusions built on `psse` are void. Rule **M6** below |
| 3 | No series switch exists in the library | `master:breaker3` was proven in **S18** (`stage2\su2_governor_island.pscx`): signal 0 = closed, 1 = open | Breakers are now in ib5 |
| 4 | Run 96 "collapse to 45.9 Hz"; G5 clause 3 fails; the France inertia (98 %) blocks it | In run 96 France stays at **49.89 Hz** while all four Iberian units slip **together** at **4.3–4.4 s**, then about 6 pole slips by 6 s **with the ties closed**. That *is* the report's loss of synchronism | The France inertia is **not** a blocker. What was missing: a realistic tie, an out-of-step trip and correct dispatch (all in ib5) |
| 5 | Machine "trip" by the `EN` torque gate | It zeroes torque only; the unit stays connected and keeps feeding stored energy and AVR support | Machine trips are now breakers (`BRK30/31/32/37`) |
| 6 | Pre-event voltage matched with Q(V) droop (`Qmode 1`, `Vset` 1.02–1.03) | The report: plants at **fixed PF 0.985** (RD 413/2014, p.298) | Baseline is **`Qmode 0` only**. Q(V) is a *prevention measure* (WP11), not the replication |
| 7 | Prevention: inertia +20 %, condensers "do not prevent" | Both were tested on the **forced** case, where the trips are imposed, so nothing can prevent them. The condensers sat on collectors **injecting** Q at 1.05 pu. The report puts them on the 400 kV grid, where their benefit is **voltage control** (p.310) | Void. Redo on the emergent case (WP11) |
| 8 | Kpf −0.30 "prevents 95 %" | The grid ran at **0.5–1.0 pu** in that run | Void (not a realistic operating point) |
| 9 | 8 × 250 MVA condensers = "5,000 GWs" | = **5 GW·s** (2,000 MVA × 2.5 s) | Arithmetic |
| 10 | Pre-event interchange: France injecting 5–8.7 GW (lever 3 moved 2.5 GW to France) | The report: Spain **exports 4,185 MW** (Fig 3-5): Portugal 2,100 and Morocco 750 (p.134, constant), France the rest (1,000 HVDC + ≈335 AC) | Fixed in ib5; lever 3 undone |
| 11 | Ties T1-39/T9-39 | **9.75 Ω each** (≈16 GW Pmax each): 13.3 GW lost in run 85 without separation | Raised to 90 Ω each in ib5 (≈3.9 GW Pmax), calibrated in WP8 |
| 12 | G4a clause 2: bus 37 "network-limited" (5× AVR gain buys 1.9 kV) | Measured inside the swing, and blamed on the empty `psse`. A unit that does not move with a 5× gain is at a **limit** (exciter ceiling or over-excitation) or is mis-initialised (`V0`/`Q0` from an old load flow) | Re-measure on the settled ib5; read the unit's `QOUT`/`VIT` and the exciter output before calling anything "network-limited" |
| 13 | G6: "no bus has the report's 3–7 kV sensitivity", so Carmona cannot be mapped | Measured inside a ±40 kV swing. S21 run 6 (settled) gave **−10.1 kV per 600 Mvar at bus 9 ≈ 2.8 kV per 165 Mvar**, already near the report's range | Redo the Granada sensitivity from the snapshot (WP7 step 6) |
| 14 | Stage 7: "first trip unreachable, control-mode window empty" | Built on Q(V) droop (row 6) and swing-driven peaks (row 1) | Void. Case B is redone with fixed PF from the snapshot (WP10) |
| 15 | Run 99: "cascade 12/18 plants, 7,028 MW, within 13 % of Fig 3-7" | Granada was forced at 3.0 s **on an up-swing**: before the event its voltage already ran from 0.76 to 1.02 pu, so the "peaks" are mostly the swing | Void |
| 16 | G10a: "0.690 Hz within 10 % of 0.63 Hz" | 0.69 Hz is close to the model's own Iberia–France inter-area swing (≈0.5–0.6 Hz), excited by a step. The report's 0.63 Hz was a **forced** oscillation from one plant (Fig 4-19) | Not evidence yet. Redo per WP11's G10 note |
| 17 | POD "cannot quiet the baseline oscillation", rejected as dispatch-coupled | The "baseline oscillation" was the start-up swing | Void; re-test POD only if a settled oscillation exists |
| 18 | Decisions D-load-shedding and D-France-inertia "need the user" | Neither is needed: signal-controlled shunts exist (WP9), and the inertia was not the blocker (row 4) | Both withdrawn |
| 19 | 34 corridor meters as a lever-3 prerequisite (6 run) | Lever 3 is undone, and the dispatch is set from the report's boundary flows | Stop corridor metering; use `PTIE`, HVDC P and the unit `POUT`s |
| 20 | `PLAN.md` §1 and the status sections edited (P1) | The old start prompt wrongly allowed §1 edits | The new prompt forbids all `PLAN.md` edits |

**Model changes made in S23** (`stage11\prepare_ib5.py`, from `stage5\ib4hv_lever3_pod04.pscx`; snapshot
copy `stage11\ib5_s23_prepared.pscx`; built in PSCAD: **0 errors, NODES 197, NPAGES 27**, only
type-conversion warnings; not yet run):

1. **Breakers** (`master:breaker3`, 0 = closed) between every SyncUnit and its 400 kV bus.
   - Buses 31/32/37: replace the survey multimeters (0 nodes).
   - Bus 30: unit moved 3 grid units up (+3 nodes).
   - France: tie breaker `BRKFR` on the bus-39 side of its multimeter (+3 nodes).
   - Trip commands `BRK30/31/32/37` = `compare(time > X)` at rows y = 400–406. `X` = 1e6 (never) by default; set `X` to trip.
   - The shunt-reactor labels `SH30/31/32/37` are now on the **bus** side, so a reactor stays when its unit trips.
2. **Out-of-step relay** (rows y = 412–426): `cos(Ph39 − Ph9) < cos 120°` **and** `time > 11 s` → latch → `BRKFR = 1`.
   - `Ph39` is now the France *terminal* angle and `Ph9` the Iberian end.
   - The cos() removes the ±180° wrap.
3. **Tie**: series R and L of T1_39 and T9_39 × 9.23 (9.75 → **90 Ω** each, ≈45 Ω in parallel, Pmax ≈ 420²/45 ≈ **3.9 GW**).
   - Target: the −3.6 to −3.9 GW import at which the ties lost synchronism (Fig 4-91, PMU −3,566 / sim −3,847 MW).
   - Line charging unchanged.
4. **French load**: the 4,531 MW load at bus 39 moved to the France terminal node `HE39_2` (France side of `BRKFR`).
   - It is France's own demand. When the tie opens it must leave with France; on the Iberian side it would make the separation *relieve* Iberia instead of leaving it short.
5. **Iberian demand**: the other 18 loads × 1.35644, giving **28,087.5 MW** at 1 pu.
   - That is Spain 25,237.5 + Portugal 2,100 + Morocco 750; the exports are modelled as constant load, spread uniformly.
6. **Generation**:
   - **Iberian SyncUnits**: P0 × 1.4298 = **11,950 MW**, the report's synchronous total (Fig 1-4: nuclear, CCGT, coal, hydro, pumped-gen, solar-thermal, cogeneration, thermal RES); `Pmec` = P0/Sbase.
   - **Plants**: uprated × 1.30 (Sbase, Ki, Lf, Cf; Rf unchanged), so total Sbase is **21,514 MVA**, near the report's PV + wind 20,170 MW.
   - **Plant Pref**: restored to the pre-lever-3 values (+0.1511 pu), giving ≈ 18.2 GW at 1 pu.
7. **France** P0 = 4,531 − 335 − 1,000 = **3,195.8 MW** (French load − AC export − HVDC far end).
8. **HVDC** unchanged: `PMODE 1` = constant P **1,000 MW** export.
   - This *is* the report's switch from AC emulation to fixed P at 12:09 (p.71).
   - Do not use `PMODE 3` for the replication.
9. **Recorders**:
   - `Ph31/Ph32/Ph37` removed (their multimeters are now breakers).
   - The France multimeter now outputs **`PTIE`/`QTIE` in MW/Mvar** (S = 1): the AC tie flow at the France terminal.
   - Its sign is unchecked: check it against France `POUT` − French load (M3).
10. **Run settings**:
    - The settle run is pre-set: 14 s, 20 µs, 200 µs, `SnapType ONLY_ONCE`, `SnapTime 12`, `snapshot_filename ib5_settle12.snp`. Read them back (T5).
    - `stage3\wp5_state.py` and `stage5\set_plant_dispatch.py` now scale the plant Sbase by `KPLANT` (default 1.30). Set `KPLANT=1` only for pre-ib5 PSOUTs.

**Known approximations (record them in the write-up, do not "fix" them silently):**
- Portugal and Morocco appear only as constant load: no Portuguese inertia or LFDD, and the Morocco tie does not trip at loss of synchronism.
- The dispatch was set by arithmetic, not a load flow, so the machine `Ph0/V0/Q0` initial values are from the old case. The settle run absorbs the mismatch.
- Load is `NP = 1` (P ∝ V), so the MW drawn depends on the settled voltage.

---

## 1. Status board — v0.9 HISTORY (superseded by §1a; the S22 status in STATUS.md is withdrawn where §1a says so)

**Session 21 (2026-11-18) — WP5 operating point, measured:** levers 1, 2 and 4 + AVR `KA` 40 +
parked relay `Vt` 1.5. Collectors now **1.046–1.064 pu at all five buses** (were 0.44–0.57),
machines **absorbing 8.3 Gvar** (grid reactively surplus), 0.5 Hz inter-area mode **ζ ≈ 6.6 %**
(target 5 %), G4a **sign check PASS**, no trips. **5 of 7 G4a clauses pass**; the open one is the
400 kV band (buses 30/31/37 at 428–449 kV), being closed with shunt banks at those buses
(`stage5\ib4hv_wp5_run6.pscx`, RUNLOG S21 §12–§16). NODES 191, NPAGES 27. AVR `KA` 400 was the
source of a zero/negative-damping 0.5 Hz limit cycle present since S19b.

**Session 21 addendum (runs 9–15, current best state = `stage5\ib4hv_wp5_run15_reverted.pscx`):**
lever 6 (`V0` France 0.9744 → 1.02) fixed bus 39 (392 → 410 kV); the 400 kV profile is now
**396.6 (bus 37) … 426.4 (bus 31)** with 409.9 (39), 413.8 (30/9) and collectors 0.976–1.030.
G4a clause 2 is **OPEN with a measured cause** (RUNLOG S21 §21–§29, D21-15): the five machine buses
span 30 kV > the 20 kV band, their terminals are the only reachable 400 kV nodes and are AVR-held
(`pscad_get_ports`: one `T` pin each), the collector-transformer `N1` pins give −1.5 kV per 600 Mvar
but collapse the plant converters beyond that (run 13: collectors 0.69 pu, −3.2 GW), and the two
offending units ride their Q limits (`V0` trim inverts, run 14; `KA` 120 moves 0.9 kV and worsens the
mode, run 15). Closing it needs extra 400 kV nodes in the `psse` equivalent — model data, not a lever.

**Current state (supersedes the Session-18 table below where they differ):**

- **Run settings of record from Session 21 (user):** 6 s maximum, **20 µs** step, 200 µs sample.
  D21-18: validated against the 2 µs runs — the steady-state numbers agree to ≤0.1 kV and ≤0.5 MW
  (run 17/18 vs run 12), so the coarser step is used for all steady-state gates from here on.
- WP2 is done (G1b): NPAGES 44 → 26.
- WP3: all 18 plants are placed and the per-bus plant clauses pass, but the system clause **fails**. With the last ideal source gone, the collector buses sit at 0.44–0.57 pu, there is a ≈ 7 GW deficit and the frequency falls (S19 §32–33, S19b §6–8).
- **Force trip path (S22): CLOSED.** `TRIP = (1 − EN) OR Force` added to the accepted case's XML (`stage5/add_force_or.py`, row y = 344); `run 74` (FRC `Max` 1) trips plants [1] and [16] at t = 0, `run 75` (forcing off) reproduces run 72 exactly (machines 15,361.7, plants 13,966.8, HVDC −1,000.9, 0 trips). Accepted snapshot `stage5\ib4hv_wp4_complete_force_or.pscx`.
- **Stage 5 (S22): LFDD relay built and gated; load shedding blocked.** `stage5/build_lfdd_relay.py` builds the six-step ladder (49.0/48.8/48.6/48.4/48.2/48.0 Hz, 0.1 s definite-time delay, proven latch) on Main as signal-only blocks (0 nodes); `run 77` latches the six steps at **1.189/1.424/1.659/1.895/2.130/2.365 s** against expected 1.188/1.424/1.659/1.894/2.129/2.365 (≤1 ms). It **does not shed load**: one breaker per `fixed_load` = 210 nodes vs 200 (9 fit), loads are constant-parameter, and most demand is inside `psse`. Snapshot `stage5\ib4hv_stage5_lfdd_relay.pscx`. **Correction (S22): `PLAN_OLD.md` Part C is not missing** — `PLAN.md` line 15 places it one folder up (`..\PLAN_OLD.md`), and Part C defines G5–G10. **G5 clause 3 measured and NOT passed** (`run 85`): forcing **13,275 MW** of plant loss at t = 3.0 s leaves `f` 50.291 → min 49.521 → 49.810 Hz and all five machine `THETA` at +3.13° — no loss of synchronism, no tie opening (the 200 GVA France equivalent absorbs 15,342 MW). The Force net reaches **16 of 18 plants** (1 and 16 stay on).
- **Stage 6 (S22): Case A event ledger built and matched to Fig 3-7.** `stage6/build_event_table.py` converts all 173 timed rows of `data/events.csv` into `stage6/event_table.csv` (net imbalance + gross lost generation; the report's `2a/b` summary row is dropped to avoid double counting). Self-checks: Table 3-2 window **7,609.27 MW (exact)**; gross ledger vs Fig 3-7a/b over 371 digitised samples **median |error| 11.4 MW** (max 683); G7 window 12:33:17/18/19/20 residuals **−43.5 / +14.2 / −33.5 / +191.1 MW**, all inside ±20 %. Figure `results\stage6\stage6_event_ledger\`. The forced-trip path is characterised (`stage6/set_global_force.py`, `stage6/set_timed_force.py`); forcing at t = 0 has no valid initial condition, and forcing at 0.5 s falls inside the plant start-up ramp (X1 0.1 / X2 0.6 s) — both recorded.
- **Stage 6 infrastructure (S22): per-plant Force nets + G5 clause 2.** `stage6/split_force_net.py` splits the global `FRC` net into **18 per-plant nets** (signal-only, 0 nodes; the global const stays at 0 because `HVDC_T` reads it). `RES_Plant[k]` is now **measured** to follow **ascending component id** (run-85 survivors + four dispatch values). `run 86` (build 0 errors, NODES 191) forces channels 2/4/11 at t = 3.0 s: exactly those three trip, **3,077 MW** lost, others untouched. **G5 clause 2 FAILS structurally:** there is no tie branch (France is a 200 GVA machine on bus 39) and its power already swings **-2,951..+14,747 MW** pre-event; the operating point is an **import** (mean ~+9 GW) while the report has **4,185 MW export** (Fig 3-5), so a 3 GW loss cannot reverse it. Closing it needs a modelled tie + an export-state dispatch (same family as the WP3 balance gap). Snapshots `stage6/ib4hv_perplant_force.pscx`, `..._3gw.pscx`.
- **Stage 6 / G6 Case A replay (S22, run 87): executed, NOT passed.** Applied the split to the adopted lever‑3 point with per‑channel force times and forced cluster equivalents at 3.0/3.2/3.4 s (454 / 897 / 905 MW; total **2,256 MW**; every trip fired at its commanded time, only the six named plants). Against A3: the 454 MW step moves the 400 kV buses **+9.1/+13.5/+11.6/+6.7/+0.1 kV** where A3 asks **+3…+7 kV** (2–4× too voltage‑sensitive; bus 31 reaches **445.3 kV**, past the 435 kV POI figure), and `f` moves only **−0.005 Hz** (49.9223 → 49.9174; A3 low edge 49.92) versus 49.8 ±0.05 at 12:33:18. **Baseline corrected (S22, measured):** the earlier “0.5 Hz” figure came from `run 63`; the real mode is **0.222 Hz (period 4.5 s)** and on the accepted point `f` p‑p is only **0.0033 Hz**. The frequency baseline is quiet — the **voltage** mode is not (**bus‑31 V p‑p 43–55 kV**), and a Kpod sweep cannot fix it: raising `Kpod` 0→0.5 damps bus‑9 speed 0.3290→0.1582 Hz but **grows** the voltage swing 43→55 kV and France speed 0.0071→0.0238 Hz. So G6's **voltage rows stand** (event +13.5 kV vs ~3 kV of mode in a 0.1 s window) while its **frequency rows are unmeasurable** (event −0.005 Hz vs mode 0.007–0.024 Hz). The missing device is a **PSS on the `SyncUnit` exciters** (or a voltage/angle‑fed POD), not a PV power POD. The 0.2 s spacing also compresses the report's ~19 s + 1 s, so an A3 comparison must be time‑scaled (A2). Snapshot `stage6\ib4hv_caseA_345.pscx`.
- **G6 baseline (S22, runs 88–90): the masking transient is the model's own start‑up.** The plant `upramp`s run 0 → dispatch in 0.5 s, a **14 GW step** that rings the 0.222 Hz mode (~0.22 Hz at 1 s, τ ≈ 3 s), so at t = 3 s the ringing is ~0.1 Hz — bigger than the event responses. `Y1 = Y2` is **inert** (run 89 = run 88 to 4 decimals); pre‑starting the ramp (`X1 = −1`, `X2 = 0`) **collapses the system** (f 45.74 at 5–6 s, run 90) because the ramp is load‑bearing for the initial condition. **Also a measurement trap:** runs 82/88 are the same physics yet differ **2× in p‑p**, so the Kpod 0.3/0.4/0.5 comparison must be redone on an envelope/decay metric. Next: lengthen the ramp to X2 = 2 s (same 14 GW over 2 s, IC untouched) to cut the excitation ~4×. Baseline case `stage6\ib4hv_split_lever3.pscx`.
- **G6 scored by paired difference (S22, runs 91/92) - and the run-87 voltage verdict is overturned.** The ramp is closed as a lever (`X2 = 2 s` is worse: pre-event f **48.906 Hz**, ring 0.82 Hz p-p). The split is proven neutral: forcing-ON (`run 92`) minus forcing-OFF (`run 88`) on the same netlist is **0.0 kV / 0.0000 Hz** before the event. The paired difference gives the first clean score: **dV bus-31 +0.3 / +0.4 / -6.3 kV** and **df -0.0031 / -0.0273 / -0.0884 Hz** at 454 / 1,351 / 2,256 MW lost (extremes +/-18 kV, +/-0.14 Hz). So the model is **12-30x too STIFF in voltage** (0.66 kV/GW vs A3's 8-20 kV/GW) - not too sensitive - while **frequency is ~2x too weak** (39 mHz/GW vs A3's 79 at 12:33:18 = 2,536 MW lost, f 49.8). G6 still fails, on voltage stiffness and an incomplete event set (~2.3 of ~4.5 GW). Snapshots `stage6\ib4hv_caseA_split_345.pscx`, `stage6\ib4hv_split_lever3.pscx`.
- **G6 full plant-side cascade (S22, run 93): frequency ~7x too weak, voltage not scoreable.** `stage6/build_caseA_schedule.py` turns the report's plant-type loss (7,812 MW of the 11,921 MW ES total) into a per-plant trip schedule, compressed to 2.5-4.5 s; 13 plants + 1 closing trip = **6,615 MW** (+4 % vs the report's cumulative at the same clock). The nuclear/CCGT/hydro **4,109 MW is machine-side and not forced** (recorded). Paired difference vs `run 88`: pre-cascade **0.0 kV / 0.0000 Hz**, and at the checkpoints **\u0394f \u22120.019 / \u22120.032 / \u22120.108 / +0.034 Hz** where A3 has **\u22120.20 / \u22120.25 / \u22120.50 / \u22122.00 Hz**; extremes **\u0394V \u221226.3\u2026+22.3 kV**, **\u0394f \u22120.265\u2026+0.167 Hz**. So even the whole forceable fleet moves `f` by at most 0.265 Hz - **~7\u00d7 too weak**, saturating around 40 mHz/GW against the report's ~250 mHz/GW. Cause: the unforceable machine-side loss plus the 200 GVA France swing machine. Absolute voltage rows stay unscoreable (Carmona unmapped). Snapshot `stage6\ib4hv_caseA_full.pscx`.
- **Frequency-gap root cause (S22, measured): the France equivalent carries 98 % of the model's inertia.** `SyncUnit` has **no EN/Force input** (17 constant imports + 1 electrical node; `Pmec` is a parameter), so nuclear/CCGT trips **cannot be commanded** as built - adding a gate is a definition change needing a bench test (Part C rule 2). And forcing would not close the gap: KE = **5,119.5 GWs** total, of which the France unit (200,000 MVA x H 25 s) holds **5,000 GWs = 98 %**, while the four Iberian machines hold **119.5 GWs** (= the G4 target). The model is **43x** the report's inertia; the swing equation gives 0.032 Hz/s for 6.6 GW (measured 0.092 with governor action) against 0.95 Hz/s at 119 GWs - the ~10x that matches G6's frequency gap and G5 clause 3's survival. Passing those rows requires **reconsidering the France equivalent's `Sbase`/`H`** - a model-design decision for the decision log, not a silent edit.
- **SyncUnit EN gate built; machine-side loss reproduces A3's frequency magnitude (S22, runs 94/95).** `stage6/add_syncunit_en.py` adds a signal `EN` port to `SyncUnit` and gates the mechanical-power net (`TMECH_g = TMECH*EN`); the interface needed three declarations (svg port, graphics Port with full paramlist, `import` with no `content` tag). `stage6/drive_syncunit_en.py` drives the five instance pins. The working driver is an **inverted compare** (`OL=1, OH=0`): `EN = (time > t)` broke the initial condition (pre-event f 46.07 Hz, run 94) and the `sumjct` version would not build. With it, **EN=1 is transparent** (pre-event df **0.0024 Hz**) and trips on buses 31/32/37 at 3.0/3.3/3.6 s give paired **df -0.34 / -0.52 / -2.15 Hz** (min -3.14). A3 wants **-2.0 Hz at 12:33:22** - so the **"7x too weak" of run 93 was an artefact of forcing converter plants only** (no inertia, no governor); the same loss on the synchronous units reproduces the report. Recorded limits: partial trip (bus 31 ~2.0, bus 32 ~4.4 GW remain), Tm pin inferred from the label position, voltage still unscoreable. Snapshot `stage6/ib4hv_machine_trip.pscx`.
- **Full Case A replay (S22, run 96): model collapses like the report; G6 frequency passes, voltage does not.** Plant cascade (14 plants, 6,615 MW, 2.64-5.12 s) **plus** machine trips (buses 31/32/37 at 3.0/3.3/3.6 s via the EN gate), paired against `run 88` (pre-window **0.0000 Hz**): **df -0.019 / -0.161 / -0.588 / -2.489 / -3.984 Hz** at the 12:33:18 / :19 / :20 / :22 / collapse checkpoints, where A3 has -0.20 / -0.25 / -0.50 / -2.00 / collapse. Absolute f at 5-6 s **45.877 Hz** (forcing off 49.861) - a genuine collapse below A3's 47.5 Hz threshold, within **25 %** at 12:33:22. **Voltage stays unscoreable** (Carmona unmapped; paired dV -49.6..+22.6 kV). Trap fixed: both driver sets made a `time-sig` named T6 (`source contention`) - EN drivers now use T7. Also corrected: the machines decelerate to 47.6 Hz and release inertia, so the trip is genuine (not a partial governor effect). Snapshot `stage6\ib4hv_caseA_fullreplay.pscx`.
- **Carmona mapping attempt (S22, run 97): blocked by stiffness, measured twice.** `RES_Plant[2]` is Granada (355 MW, bus 33). Forced alone at 3.0 s (TRIP verified, ID -> 0.226), paired vs run 88, the measured 400 kV buses move only **+1.2 / +1.4 / +2.2 / +1.0 / 0.0 kV** (9/31/32/37/39) - the report's Granada-loss sensitivity at Carmona is **3-7 kV**, so **no bus in the model has the local response**. Single-event stiffness: **6.2 kV/GW** vs A3's 8.5-19.7 (1.4-3.2x too stiff), confirming G6's 0.66 vs 8-20 kV/GW from an independent test. Absolute-value matching cannot separate bus 31 (423.6 kV) from bus 32 (418.4) against Carmona's 421.8 +-4. So the A3 **voltage rows remain unscoreable for a measured reason**, not an unfinished search. Snapshot `stage6\ib4hv_granada_only.pscx`.
- **Stage 7 started (S22, run 98): fleet OV settings applied, cascade propagates weakly.** `stage7/tune_ov_relays.py` assigns the six observed settings (1.089/1.5, 1.10/0, 1.10/0.5, 1.111/**0.1 assumed**, 1.139/0.2, 1.15/0.6) round-robin across the 18 plants (each 3x); snapshot `stage7\ib4hv_ov_tuned.pscx`. First Case-B run (base dispatch, one forced 154 MW plant at 3.0 s): **3/18 plants trip** - initiator + ch13 at 3.264 s + ch15 at 3.408 s, **802 MW**, f 49.918 Hz, buses 413/426/419/397/410 kV. So propagation exists but is ~0.8 GW vs the report's ~7.6 GW, and the emergent trips fire **before their configured OV delays** (1.5 s / 0.5 s) so they are **not** the block-1 OV relays - the path must be identified before G7 can be gated. **Correction:** Granada is psout **ch1** (356 MW, document order vs ascending-id channel index differ by one), so runs 97/98 tripped a 154 MW plant, not Granada; Granada's Force is already driven by an inert `signalgen`, so forcing it needs the inverted-compare treatment like the `SyncUnit` gate.
- **Stage 7 cascade (S22, run 99): 12/18 plants, 7,028 MW - cascade fraction MET, first-trip criterion NOT met.** `stage7/force_granada.py` now **deletes the inert FRC33 `signalgen`** at (100,48) and drives Granada's Force from `compare(time > t, OL=0, OH=1)`; Granada (psout **ch1**, 356 MW - the channel correction is confirmed) trips at exactly 3.000 s, build 0 errors/NODES 191. Tuned relays then propagate to **12 of 18 plants, 7,028 MW**, f 49.749 Hz - **87 % of the report's 8,109 MW at the equivalent clock, inside G7's +-20 %**. Diagnostic: ch9/ch10/ch15/ch3/ch4 trip with VDF **above** their Vt1 (OV path plausible), but **ch7 (VDF 1.0488 vs 1.089) and ch13 (1.0555 vs 1.089) trip 0.06 s after the initiator**, far inside their 1.5 s delays - path still unidentified. First trip: Granada is *forced*, whereas G7 requires LV-side OV with POI < 435 kV. Snapshot `stage7\ib4hv_granada_initiator.pscx`.
- **Stage 7 trip path resolved; first-trip criterion is structural (S22, run 99 re-read).** All five early trips are the **block-1 OV relay**: VDF **peak** in the 20 ms before each trip is **1.1017 / 1.1007 / 1.1760 / 1.1362 / 1.1485** against thresholds 1.10 / 1.10 / 1.111 / 1.111 / 1.111 - ch7 and ch13 are simply the two channels assigned **Tt1 = 0 s**, so a 0.7-1.7 mpu spike fires them. (The earlier "unidentified path" came from using a 0.1 s mean and from a **mapping error**: `tune_ov_relays.py` assigns in document order while psout channels follow ascending id, so the per-channel table is 1,7,13 = 1.10/0; 2,8,14 = 1.10/0.5; 3,9,15 = 1.111/0.1; 4,10,16 = 1.139/0.2; 5,11,17 = 1.15/0.6; 6,12,18 = 1.089/1.5. Each setting still appears three times.) **G7's first-trip criterion needs a 220 kV LV bus at Granada** - the model connects the plant at the 400 kV collector 33, so the report's 400/220 kV transformer relay has nothing to measure. That is an architecture addition, not a setting.
- **Stage 7 first trip: no relay fires without forcing, and the 220 kV build would not fix it (S22, run 100).** Tuned relays, no forcing: **0 trips**, `f` 49.958 Hz, peak VDF per plant **1.069-1.120 pu** against thresholds 1.089-1.15 (ch15 even peaks at 1.1198 vs 1.111 but the spike is shorter than its 0.1 s delay). A 400/220 kV transformer has the **same per-unit ratio**, so a Granada 220 kV level would show the **same 1.03-1.07 pu** - below every threshold. **Not built, for a measured reason** (~6 nodes saved). The report has Granada's LV side at **1.061 pu at 12:32:56 and >1.10 a second later**, while the model peaks at 1.069-1.097 with no rise: G7's first-trip criterion is **coupled to WP5's reactive balance**, the same stiffness gap measured in G6 (0.66 kV/GW) and run 97 (6.2 kV/GW). Stage 7 status: cascade fraction **met** (87 %), first trip **not reachable without the pre-event voltage being right**.
- **Pre-event voltage lever measured and rejected at Vset 1.10 (S22, run 101).** Baseline (`run 100`): steady plant terminals **0.979-1.032 pu**, `Qmode = 0` (Vset inert), Granada 0.9789 vs the report's 1.061 - a **~0.08 pu** gap. Applying `Qmode = 1` / `Vset 1.10` to all 18 plants (build 0 errors, NODES 191) **rejected**: ch1/ch7/ch13 (the Tt1 = 0 channels) trip at **~0.51 s** on the start-up overshoot, and steady terminals **scatter** (ch2-4 0.707, ch12-14 0.921, ch5-11 1.009, ch15-17 1.028) because the Q-limited units redistribute rather than lift; peaks 1.19-1.27, f 49.699 Hz. So the WP5 reactive lever needs a **smaller, per-collector set-point** (target the report's 1.061, not 1.10) and staggered zero-delay relays - the direction is right, the magnitude is wrong. Snapshot `stage7/ib4hv_qdroop_v110.pscx`.
- **Pre-event voltage CLOSED at Vset 1.02 (S22, runs 103/104).** The droop's sign is right but its gain saturates: at Vset 1.06/1.10 IQ swings to **+0.13..+2.51 pu** (ch2 2.5 pu against a 1.1 limit) and the terminals **collapse** (ch1 0.405). At **Vset 1.02** the fleet is stable: **ch1 1.0586**, ch2 1.0681, ch5 1.0617, ch12 1.0780, ch15 1.0817, IQ -0.077..-0.123 (absorbing, inside limits), no trips, f 49.886. Granada is **0.002 pu** from the report's **1.061** - the pre-event voltage now matches, which is the condition G7's first trip was missing. The report's >1.10 occurs *after* clusters 1-2 and the transformer trip, so the next Case-B run starts from this snapshot with the cluster 1-2 loss applied. Snapshot `stage7\ib4hv_qdroop_v102.pscx`. Trap recorded: editing while the case is loaded is silently reverted on unload (run 102 = run 100) - unload, edit, verify on disk, load.
- **Case-B first-trip attempt (S22, run 105): Granada reaches 1.0898 pu - 0.010 short.** On the Vset-1.02 snapshot with `Tt1 = 0` restored, forcing the report's cluster 1-2 equivalent (ch3+ch7 = **517 MW**) at 3.0 s lifts Granada's terminal **1.0622 -> 1.0898** (+0.0276 pu, **5.3e-5 pu/MW**) against its **1.10** relay - **no trip**; the report needs +0.04 pu for the same 525 MW (7.6e-5 pu/MW), so the model is still ~30 % less sensitive there. On this slope **~750 MW** would cross 1.10, but inflating the initiator was not done (it would no longer be the report's event). Also measured: **ch13 trips at 1.306 s on the start-up transient**, before the event, so the run is one plant down when the initiator lands - the plant ramp needs softening before `Tt1 = 0` channels can stay live. Snapshot `stage7\ib4hv_caseB_attempt.pscx`. G7 first trip: not met, gap now quantitative (0.010 pu).
- **Clean Case-B run (S22, run 106): the 0.010 pu shortfall is reproducible.** With only ch7/ch13 parked and **Granada's relay live at 1.10/0 s**, the 517 MW initiator gives ch1 peak **1.0899** (run 105: 1.0898) and **no spurious trips** - so the gap is real, not caused by ch13's early loss. Sensitivity: **+0.0286 pu for 517 MW = 5.5e-5 pu/MW** vs the report's 7.6e-5. Closing it needs either a **~700 MW initiator** (5.5e-5 x 700 = 0.039 pu) or a further reactive lever (collector taps / slightly higher Vset) worth 0.010 pu. Neither applied silently: G7's first-trip criterion stays **unmet by 0.010 pu**, now a clean reproducible number. Snapshot `stage7\ib4hv_caseB_clean.pscx`.
- **Vset 1.03 (S22, run 107): Granada at 1.0987 pu, and an emergent OV trip fires by protection.** One parameter changed from run 106: **Vset 1.03**. Granada steady **1.0692**, peak **1.0987** - **0.0013 pu** short of its 1.10 relay. ch13, meanwhile, **trips at 3.211 s by its own relay** (peak 1.1259 > 1.10 with the 0.05 s park) - a genuine post-event, voltage-driven trip, unlike the 1.306 s start-up trip of run 105. Measured slope: **dV/dVset ~= 0.88**, so **Vset 1.032** predicts a peak of ~1.100. G7 first trip: unmet by 0.0013 pu with the mechanism demonstrated and the closing step quantified; three runs spent on this symptom (105/106/107), so it stops here. Snapshot `stage7\ib4hv_caseB_vset103.pscx`.
- **Vset lever exhausted at 1.030 (S22, run 108).** `Vset 1.032` trips Granada at **0.506 s on the start-up** (peak 1.1619) before the event, and the steady terminals collapse (0.65-1.02) - the same failure mode as 1.06/1.10. The usable window is **<= 1.030**: 1.020 -> peak 1.0899; 1.030 -> peak **1.0987** (0.0013 short); 1.032 -> premature start-up trip. So the set-point that would cross 1.10 is the one that trips Granada first - **the window is empty**, and G7's first-trip criterion cannot be met by `Vset` tuning at this dispatch. Remaining routes: soften the start-up ramp so 1.032 survives, or accept a **~700 MW initiator** at Vset 1.030 as a documented deviation. **Cascade fraction recorded:** run 107 gives **634 MW = 25 %** of the ledger (outside +-20 %) - a real trade-off against run 99's 87 %, which needed Qmode 0 and all relays live. Snapshot `stage7\ib4hv_caseB_vset1032.pscx`.
- **G7 first trip is control-mode limited, measured both ways (S22, runs 109/110).** Softening the ramp (`X2 = 1.0 s`) does not help: Vset 1.032 still trips Granada at **0.528 s** (the overshoot is the droop's response to the initial voltage error, not the Pref ramp), f 45.370 Hz. Raising the initiator from 517 to **671 MW** moves Granada only **1.0987 -> 1.0989 (+0.0002)** - the **Q droop absorbs Q to hold its set-point and clamps the excursion near 1.099**. So: **Qmode 0** gives the cascade fraction (87 %, run 99) but pre-event terminals of 0.98 and no trips; **Qmode 1** gives the report's 1.061 pre-event but clamps the excursion under 1.10 and drops the cascade to 25-31 %. **The two G7 criteria pull the control mode in opposite directions**, and closing the first trip would need the 220 kV transformer dynamics (not modelled) or a different reactive-control design. Snapshots `stage7\ib4hv_caseB_vset1032.pscx`, `stage7\ib4hv_caseB_671.pscx`.
- **Stage 8 opened (S22, run 111): +20 % inertia does not prevent collapse - G8 counterfactual 1 PASSES.** `stage8/raise_inertia.py` sets **H 2.5 -> 3.0 s** on the four Iberian `SyncUnit`s (France equivalent left at 25 s, being an artefact) on the run-96 full-cascade case; build 0 errors/NODES 191. Baseline `f` 5-6 s **45.877** (min 44.227) vs **46.875** (min **45.727**) at +20 % - both far below A3's 47.5 Hz threshold, so the collapse persists and the criterion is met, with the model showing the report's qualitative behaviour (extra inertia **slows but cannot stop** the collapse, ~1.0 Hz). Remaining counterfactuals: ideal LFDD percentages (blocked by the missing series switch, may reduce to the signal-only ladder) and eight 250 MVA condensers (expected to succeed, p.310). Snapshot `stage8\ib4hv_g8_inertia120.pscx`.
- **G8 counterfactual 3 does NOT reproduce (S22, runs 112-114).** `stage8/add_condensers.py` adds **8 x 250 MVA `SyncUnit` condensers** (P0 = 0, exciters at 1.05 pu, H 2.5 s) at the collector nets B33/B34/B35/B36/B38 - **NODES stays 191** (they tie to existing nodes). Making them genuine took three runs: clones as-is generated **126 MW**; zeroing `Kgov/GovLim` left 113 MW (`Pmec` is separate); **`Pmec = 0`** finally gives **P +69 MW / Q +163 MVAr**, the residual P being **inertial release while f falls**. Result: **f 5-6 s 46.684 (min 45.453)** vs baseline 45.877 - **still collapsed**, where the report says condensers *prevent* it (p.310). The 2,000 MVA (5,000 GWs, equal to the whole France equivalent) buys only **+0.8 Hz**, the same order as +20 % inertia (+1.0 Hz) - consistent with the model's 98 %-France inertia structure. **Stage 8: 1 of 3 passes (inertia), 1 does not reproduce (condensers), ideal LFDD still blocked** by the missing MW-shedding path. Snapshot `stage8\ib4hv_g8_condensers.pscx`.
- **Fourth corridor metered; G4a bus-37 lever identified as a flag (S22, run 115).** `lm_T16_21`: end 1 **+1,466.0 MW**, end 2 **-1,461.4 MW**, sum **+4.6 MW (0.31 %)** loss, opposite signs, implied R **0.41 ohm**, NODES 197, figure `results\stage6\lm_T16_21\`. Coverage **4 of 34** (T1_39 327, T9_39 802, T16_19 2,157, T16_21 1,466 MW = **4.75 GW, 34 %** of the 13.94 GW plant output). G4a clause 2 checked before a run: every `SyncUnit` has **`Vctl = 0`**, so that parameter is a **flag, not a voltage** (V0 carries 1.0247/0.9946/1.0239/1.0625/1.02); the reference is set through the AVR's **`VREFO`** path, so the next step is to read that wiring, then make one set-point change on the bus-37 unit.
- **G4a clause 2 closed as network-limited, measured three ways (S22, run 116).** The AVR reference was traced offline: `VREFO -> sandhdefn` (a **sample-and-hold**) `-> VREF`, i.e. the reference is the machine's **initial voltage**, not `Vctl` (0 on every unit, unused). At the adopted point bus 37 sits **387.4 kV against its own 405.6 kV reference**, Q only **+1,180 Mvar (0.09 pu)**, so it is not a reactive limit. Raising `KA` 40 -> **200** on that unit alone buys **+1.9 kV (389.3)** with Q unchanged; the other four 400 kV buses stay in band (403.3 / 409.9 / 409.4 / 410.7), f 49.834 Hz. **Set-point is a flag, gain buys 1 kV, Q is not engaged** - bus 37 is pinned by the imported **`psse` network**, the same D21-15 mechanism as bus 31. Closing the band there needs the imported network's capacitance or a modelled tie, not this plant's controller. Snapshot `stage5\ib4hv_ka200_b37.pscx`.
- **Stage 10 opened (S22, run 117): forced plant step excites 0.690 Hz - within 10 % of the 0.63 Hz target.** A single **367 MW** plant trip (ch7 at 3.0 s) on the adopted point, 6 s at 20/200 us, Hanning FFT over 3.1-6.0 s: **bus-9 f 0.690 Hz** (amp 0.069 Hz, p-p 0.494), and the **same 0.690 Hz** in every Iberian bus voltage - **bus 31 largest (10.8 kV amp, 67.3 p-p)**, then 32 (10.1), 9 (8.2), 37 (6.8); France 0.3 kV (no participation). G10a frequency **+9.5 % vs 0.63 Hz, inside 10 %** - the closest any gate has come to its report value; location stated at generator-bus resolution (swing concentrated in the Iberian machines, absent at the equivalent = inter-area mode). The pre-event window measures the separate **0.222 Hz** start-up mode, so the two modes are resolved. G10b (emergent) not attempted - needs the POD/droop work runs 103-110 showed unstable. Snapshot `stage10\ib4hv_scenarioO_step.pscx`.
- **Stage 9 opened (S22, runs 118/119): OV-threshold desensitisation removes 95 % of the emergent cascade.** Control `run 118`: parking all plant `Vt1/2/3` at **1.5 pu** on the run-96 **forced** case changes **nothing** (5-6 s f **45.877**, identical in every window) - confirming that cascade is scheduled, not relay-driven. Measure `run 119`: same parking on the **emergent** case (`stage7/ib4hv_granada_initiator.pscx`) drops the cascade from **12 trips / 7,028 MW** to **1 trip / 356 MW (-95 %)**, f 5-6 **49.871** (min 49.705 vs 49.470). So plant **overvoltage relays** are the propagation mechanism, and desensitising them is the most effective prevention measure found. **Stage 9 table:** OV park on forced = no effect; +20 % inertia = -1.0 Hz; condensers = +0.8 Hz; **OV park on emergent = prevents 95 %**. Snapshot `stage9/ib4hv_stage9_parkOV.pscx`.
- **Stage 9 measure 2 (S22, run 120): capacitive support at the collector WORSENS the cascade.** +150 Mvar at Granada's collector (`B33`, DELTA `capacitive_load`, NODES 191) gives **14 trips / 8,217 MW** against the run-99 baseline of **12 / 7,028** (+17 % loss, +2 trips) - the expected direction for an **overvoltage-driven** cascade, and the reason the report's "dynamic reactive support" cannot be reproduced with a static bank here. Build trap: the STAR version clashed with an existing `GND` net (`dimension mismatch 1 != 3`); DELTA needs no star point. **Stage 9 table:** OV park on forced = none; +20 % inertia = -1.0 Hz; condensers = +0.8 Hz; **OV park on emergent = prevents 95 %** (run 119); **+150 Mvar = worsens +17 %** (run 120). Snapshot `stage9\ib4hv_stage9_capB33.pscx`.
- **Stage 9 measure 3 (S22, runs 121/122): reactive absorption prevents the cascade; the `Imax` route is inert.** `Imax` 1.1 -> **1.0 pu** changes **nothing** (12 trips, 7,028 MW, f 49.749 - the current never reaches the clamp). Raising the fixed-PF absorption ratio **Kpf -0.175 -> -0.30** removes the cascade: **1 trip, 356 MW, f 49.953** - the same 95 % reduction as parking the OV relays (run 119). Together with run 120 (capacitor **worsens** +17 %), the mechanism is triangulated: propagation is **overvoltage-relay driven**, so effective prevention lowers collector voltage. **Stage 9 table:** OV park/forced = none; +20 % inertia = -1.0 Hz; condensers = +0.8 Hz; OV park/emergent = -95 %; +150 Mvar = +17 %; Imax 1.0 = inert; **Kpf -0.30 = -95 %**. Snapshot `stage9\ib4hv_stage9_kpf030.pscx`.
- **Fifth corridor metered (S22, run 123).** `lm_T16_17`: end 1 **+1,084.9 MW**, end 2 **-1,078.1 MW**, sum **+6.8 MW (0.63 %)** loss, opposite signs, implied R **1.15 ohm**, NODES 197, figure `results\stage6\lm_T16_17\`. Caveat: the flow is **still rising at 6 s** (829 MW averaged over 0.4-6.0 s vs 1,085 over 5-6 s), so this reading is a lower bound, not a settled value. Coverage **5 of 34** (T1_39 327, T9_39 802, T16_19 2,157, T16_21 1,466, T16_17 1,085 MW).
- **Sixth corridor metered and Stage 9 measure 4 (S22, runs 123b/124).** `lm_T16_24`: **-143.1 / +143.3 MW**, sum **+0.21 MW (0.15 %)**, implied R **2.05 ohm**, NODES 197, figure `results\stage6\lm_T16_24\` - a **low-flow** corridor, which shows the reader is not saturating on large flows. Coverage **6 of 34**. Stage 9 measure 4: `Tt1` raised to **1.0 s** on the emergent case **prevents the cascade** (12 trips / 7,028 MW -> **1 / 356 MW**, f 49.871) - the **third independent preventative**, alongside parked thresholds (run 119) and more absorption (run 122), consistent with the OV excursions being short spikes. **Stage 9 table:** OV park/forced = none; inertia = -1.0 Hz; condensers = +0.8 Hz; OV park/emergent = -95 %; +150 Mvar = +17 %; Imax 1.0 = inert; Kpf -0.30 = -95 %; **Tt1 1.0 s = -95 %**. Snapshot `stage9\ib4hv_stage9_tt1_1s.pscx`.
- WP6: **items 1–4 done and measured.** `RampLim` (S21 §36): all 18 plants ramp at 0.198–0.201 pu/s for 0.2 pu/s. Sub-block staging (S21 §38): shares measured 0.668 / 0.334 against 0.667 / 0.333. `meas_side` (S21 §48): `MeasSide` 0 trips at 0.551 s (`Vt1` 0.9), `MeasSide` 1 does not, baseline unchanged (13,940.6 MW). Relay rewrite (S21 §47): three identical chains, block 1 now trips (`run 47`, 0.903 s at `Vt1` 0.8). Remaining: `Qmode` 2 (grid-forming), `POD`.  **Item 5 (`Qmode` 2): mini-plan written (`stage3\design_qmode2.md`), `Qmode` parameter published (default 0), build clean - but the simulation stopped launching after that build (S21 §49: `run_project` ok, PSCAD idle, no `.psout`, no runtime message, reproduced 3x), so the `Qmode = 0` equality gate is pending a GUI-level check of PSCAD.  **Update S21 §51:** run path restored (queue restart); **`Qmode = 0` equality gate PASSES** (`run 52`: 13,940.6 / 15,333.4 / −1,000.6 MW); GF stage 2 (P/Q measurement + droop integrator) in and `run 53` reproduces the baseline; stages 3‑4 (voltage PIs + selectors on `IDREF`/`IQREF`) were refused by the label graph (`IND:Dim`, `IQREF` double‑driven) and reverted — **D21‑22: build the grid‑forming loops as a separate `RES_GFM` definition**, reusing mini‑plan stages 1‑2. No GF gate yet.  **D21‑22 scaffolding done (S21 §52):** `RES_GFM` is now generated as a separate definition (copy of `RES_Plant`, own name/id), build 0 errors / NODES 191, and `run 54` reproduces the baseline (13,940.6 / 15,333.4 / −1,000.6 MW). Next: build the GF loops inside `RES_GFM` (it owns `THETA`, `IDREF`, `IQREF`), place one instance, gate `Qmode = 0` equivalence, then ±5 % V‑step with Q within 2 %.  **Item 5a `Qmode = 1` (Q(V) droop) BUILT and GATED (S21 §55):** `run 55` reproduces the baseline (13,940.6 / 15,333.4 / −1,000.6 MW); `run 56` with `Vset` 1.05 gives `IQ` −0.0615 against the law `2.0·(1.05 − VDF=1.0807)` = −0.0614 → **0.0001 pu error (0.1 %)**; the 3.6 % offset against `2.0·ΔVset` is the closed‑loop voltage rise, not a droop error. The last build error was a missing `Vset` parameter (its label had no driver).  **GF v1 (`Qmode = 2`) built (S21 §56) and stable on one plant, but its voltage-loop tuning is not measurable in the network:** `run 58` and `run 59` (PIs 2.0/0.02 vs 1.0/0.1) give statistically identical operating points. **D21‑23:** the GF gate needs a bench (one plant + controllable source); the `rp1` bench is unusable until its `Pref` label is fixed (§39). Network reverted to the verified `Qmode = 1` state, build 0 errors / NODES 191.  **Bench status (S21 §58):** `rp1`'s `Pref` still does not drive the module after removing the three `PREF` datalabels and wiring the upramp directly (`id` constant 0.47 for a 0→1 ramp; the bench definition does contain the `Pref` import and `Ratelimit`). Next: diff the bench instance's `paramlist` against the definition's form (stale mapping, as in §41–§43) or re‑place the instance.  **GF FIXED and GATED (S21 §59):** the `Qmode` carrier was `min(1, Qmode)`, so `QM2` was always 0 and every "GF" run was really the droop (proved: `IQ` = 2·(Vset−VDF) to 0.001). A second carrier with input 2.0 fixed it; `run 62` (three bus‑38 plants, `Qmode` 2) gives **VDF 1.0096 vs Vset 1.0 (0.96 %)**, `IQ` −0.011, no trip. Remaining GF item: the angle droop (P set‑point), then POD.  **Angle droop attempt 1 (S21 §60): UNSTABLE** — `theta_GF` starts at 0 (no bumpless start) and `Kp` 0.314 rad/s/pu is too weak, so `Qmode = 2` with the droop collapses the bus (`VDF` 0.029, `ID` 3.39). `Qmode = 0` stayed exact (`run 63`). **Attempt 2 (bumpless deviation, Kp 2.0) also collapses** (`run 65`: VDF 0.217, ID/IQ at the ±1.1 limit) → the failure mode is the **current limit**, not the angle start. Recorded design item: virtual impedance + current-limiting/anti-windup (S21 §61).  Reverted to the gated voltage‑source GFM (`run 62`: VDF 1.0096 vs Vset 1.0).  **Cycle 3 (virtual impedance 0.06 pu, S21 §62): still at the current limit** (`run 66`: VDF 0.187, ID 1.099) — closed per the 3‑cycle rule with a written diagnosis: needs virtual impedance of the order of the grid impedance, a current‑limiting state machine with PI anti‑windup and the P filter. **Final item‑5 status: 5a and 5b complete and measured; 5c a documented design gap.**  **Item 6 (POD, S21 §63): designed (washout on PMEAS, Kpod 0.5, into the power reference) but the module edit was refused by the `Pref` chain** (`PSET_T` contention twice, `div` `IN1:Dim`) and reverted — the power-reference chain must be rebuilt as a single explicit chain before POD can be inserted. Next: rebuild `Pref -> PODSUM -> ratelimit -> div` in the generator, then gate POD by the 0.5 Hz mode decay (`f` p-p in 5–6 s) with Kpod 0 vs 0.5.  **POD BUILT and MEASURED (S21 §64):** injected on `IDREF_FF` (single-driver point) after the `Pref`‑chain route was refused; build 0 errors / NODES 191; `run 67` vs `run 63` gives **f p‑p 0.5435 → 0.3108 Hz (−43 %)** but with a steady‑state cost (`f` mean 49.963 → 49.763 Hz, plant `id` sum −1.69 pu), so `Kpod` 0.5 is **rejected**; next: `Kpod` 0.1–0.2 and `YO = PMEAS(0)` for a true zero‑steady‑state washout.  **Tuning (S21 §65):** `Kpod` 0.15 + `YO` 0.9 → no steady-state cost (`id` 14.416 vs 14.397) but *no* damping benefit (p‑p 0.6311 vs 0.5435); `Kpod` 0.5 gives −43 % damping with a 0.20 Hz / 1.7 pu shift, and `YO` has **no effect** (runs 67 ≡ 69). The shift is **current‑limit rectification** of the POD signal (it sits before `Imax`). Fix recorded: inject POD before the limit with its own limiter, or scale it by the remaining headroom. Note the baseline `f` mean is 49.9633 Hz, so the 49.99–50.01 criterion applies as "unchanged", not absolute.  **Headroom analysis (S21 §66):** the plants run at `id` 0.90 of `Imax` 1.1, so only **0.2 pu of headroom** exists while a damping `Kpod` 0.5 needs ±0.5 pu → any effective POD rectifies against the limit. Recorded as a **coupling with the pre-event dispatch**, not a tuning failure. Two routes: headroom-scaled injection (`POD·(Imax−|IDREF|)/Imax`) or **lever 3**, which lowers `id` and frees the headroom — lever 3 is the better next step and is itself an unstarted plan item.  **S21 §67:** line-flow channels do not exist (`pi_section` has only `N1/N2/G`; the `.psout` has no line channels) — series ammeters are the prerequisite. Baseline: machines 15,333.4 MW (France 5,119.1), plants 13,966.3 MW.  **POD headroom-scaling measured (S22, run 78):** `POD·(Imax−IDREF)/Imax` removes the steady-state cost (id sum 14.389 vs 14.397) **and the damping** (f p‑p 0.5456 vs 0.5435) because the headroom factor at id 0.90 is **0.18**, cutting the effective gain to 0.09. POD is therefore closed as **coupled to the pre-event dispatch**: only lever 3 (lowering `id`) or a redesigned limiter can free the headroom. Build `stage5\ib4hv_pod_headroom_build.pscx`.
- **Lever 3 metering (S22, continued):** two corridor pilots PASS — `lm_T1_39` and `lm_T9_39`, build 0 errors / NODES 197 each; at 5–6 s the paired end meters read **T1‑39 ≈ 327 MW** (−324/+330, +5.83 MW loss) and **T9‑39 ≈ 802 MW** (−799/+804, +4.89 MW), the operating point unchanged (machines 15,332.8, plants 13,939.7, TRIP 0). Both run below SIL. The two bus‑39 corridors total ≈1.13 GW against the France unit's 5.12 GW ⇒ **~4 GW of the bus‑39 boundary is inside `psse`** and unmeterable, so the French‑end gate needs a different decomposition. Meter budget: three meters fit before the 200‑node limit (D22‑2).  **Lever 3 EXECUTED (S22 runs 79/80):** plants −2,500 MW and France +2,500 MW → plant `id` 0.493–0.751 (headroom 0.32), plant total **11,448.4 MW**, France 8,711.8, machines 18,101.2, 0 trips, **f p‑p 0.3290 Hz** (base 0.5435). 400 kV: bus 31 **420.8 kV (0.8 over — best recorded)**, bus 37 **394.3 (under)** — the band trades one bus for the other. **POD on this dispatch: f p‑p 0.1582 Hz (−71 % vs base)** with the shift reduced to −1.07 pu — the §66 headroom coupling is confirmed and broken. Snapshots `stage5\ib4hv_lever3_dispatch.pscx`, `…_lever3_pod.pscx`.  **POD sweep on the lever‑3 dispatch (S22 runs 81/82):** `Kpod` 0.3 → f p‑p **0.5102** (worse than no POD, non‑monotonic), **`Kpod` 0.4 → 0.2469 (−25 % vs the 0.3290 lever‑3 baseline, −55 % vs the 0.5435 base) with the plant `id` sum within 0.9 %** → **accepted**, `Kpod` 0.5 → 0.1582 but −9.1 % dispatch shift. Bus trade‑off at lever 3: bus 31 **420.8 kV (0.8 over — best recorded)**, bus 37 **394.3 kV**; the re‑dispatch trades one bus for the other, and bus 37's unit is at its over‑excitation limit. Snapshot `stage5\ib4hv_lever3_pod04.pscx`.  **ADOPTED WORKING POINT (S22): `stage5\ib4hv_lever3_pod04.pscx`** (lever 3 + `Kpod` 0.4). At it, **bus 31 is in band for the first time (413.4 kV; 414.8 with a 300 Mvar shunt at the bus‑36 transformer `N1`, run 83)**, and the band has **one violator: bus 37 at 387.4 kV**. The shunt moves bus 32 +5.5 kV, bus 31 +1.4, bus 37 only **+1.1** per 300 Mvar ⇒ ~3 Gvar would be needed for bus 37 and would over‑volt the rest. Bus 37 needs machine capability or `psse` data (D21‑15, second route). The shunt also improves damping (f p‑p 0.2469 → 0.1794).  **Third pilot (S22, run 98): `lm_T16_19` PASS** - end 1 **+2,157.2 MW**, end 2 **-2,126.8 MW**, sum **+30.4 MW (1.41 %)** loss, opposite signs, implied R **1.12 ohm**; NODES 197, figure `results\stage6\lm_T16_19\`. Coverage **3 of 34** corridors (T1_39 327 MW, T9_39 802 MW, T16_19 2,157 MW).
- WP4: `HVDC_T` is bench-proven, including the lag (S20, accelerated test). It is placed at bus 9 in `C:\PSCAD_work\ib4hv` (load Q = 0, **NODES 191**) and holds 1,000 MW for 2 s. **Network gate (S21 §31, run 16, 20 s): P = −1,000.0 MW PASS, no trip PASS, steady PASS (f p-p 0.0093 Hz over 15–20 s); the Q clause FAILS: −219 Mvar at 410.1 kV** (the bus's natural voltage is 413.8, so holding 410 costs 219 Mvar; needs a V deadband or a different baseline). **French end: not built, and the reason is a design gap (S21 §32–§34):** the three cheap routes are measured dead, a far-end converter was built and run, and it showed that `HVDC_T` has **no Vdc control**, so its DC side is a stiff node — the far end injects ~0.9 GW of *net generation* instead of transferring it. Fix = a Vdc-controlling terminal variant (new module work, D21-19). **Update (S21 §35, run 20):** `HVDC_T` has *no DC-side model at all* (`xnode DCP/DCN` + AC-side current sources only), so a Vdc terminal is impossible; the far end is implemented as a **matching re-dispatch** (`stage5\set_plant_dispatch.py --set-total-mw 1000` + `set_french_end.py --drop 1000`). Measured: **France −907 MW (works)**, but Spain **+329 MW of the commanded +1,000** because the collectors sag to 0.92–1.00 pu — the export case is coupled to WP5's missing reactive support (D21-20).  **Q clause CLOSED (S22):** `Kq` 20→2 changed Q only −240.7→−237.8 Mvar (the channel is a PI, so the gain is not the lever). Raising `Vset` to the baseline voltage is: 1.036 → Q −61.5 Mvar at 417.3 kV (`run 71`); **1.040 → Q +2.6 Mvar at 418.5 kV, P −1,000.6 MW, no trip (`run 72`)** — clause met, bus 9 stays in band. The gate script's "Q follows the Kq droop: FAIL" is an artifact of its hard‑coded 1.025 design point. Snapshot `stage5\ib4hv_wp4_qclause_vset1040.pscx`.  **FRENCH END CLOSED (S22):** re-running the +1,000 MW re-dispatch on the corrected operating point (`Vset` 1.040) gives **France −932.1 MW (93 %)** and **Spain plants +992.7 MW (99 %)**, HVDC −1,000.5 MW, no trip (`run 73` vs `run 72`). The earlier partial result (run 20: Spain +329) was a property of the old operating point's collector headroom. Boundary reconciliation: the two metered bus‑39 corridors total 1.13 GW against France 5.16 GW ⇒ ~4.0 GW is `psse`‑internal and unmeterable, so the result rests on the unit‑level balance. Experiment archived at `stage5\ib4hv_frenchend_redispatch_vset1040.pscx`; the accepted state is unchanged.
- Loads are NP = NQ = 1.
- Budget: **NODES 188 / 200, NPAGES 26 / 64**, 2 µs, ≈ 200–380 s wall per simulated second.
- Working project for WP5: `C:\PSCAD_work\ib4hv` (= `iberia4` + load Q = 0 + HVDC). `iberia4` holds the executor's S19b state.
- **WP5 levers 1, 2 and 4 are already in `ib4hv`** (S20 §7, `stage5\wp5_levers.py`): line charging ×2.5 (10.6 Gvar), load Q = 0, collector taps 0.962. **Not yet run.** The first job is the stacked check run described in RUNLOG S20 §7.
- **Next: WP5, rewritten in v0.9 — make the grid reactively *surplus*, as in the report.**

Session-18 table, kept for history:

| Stage | State | Evidence | Open |
| --- | --- | --- | --- |
| 0 Setup | done | RUNLOG S1–S2 | node-limit error text never recorded (T6); not blocking |
| 1 Base network | done, one accepted deviation | S3–S4, S8 | the 2–8 % flow deviation is **not** explained by "PI vs Bergeron" (see S17 §1). Stage 4 re-dispatches everything, so leave it |
| 2a SyncUnit bench | done | S8, S10 | — |
| 2b 4 units + France | done for 30 s | S10 | — |
| 2c governor + AVR gains (WP1) | **done (G2c)**: island bench Δf within 3.1 % of the droop law; network 40 s within ±0.005 Hz | S18, `results\stage2c_governor_*\` | slow ≈ 14 s governor mode, ζ ≈ 0.04, 4 mHz: watch it when the last ideal source goes. Kgov/P_rated are *design* values: calibrate in Stage 5 |
| 3a converter bench | **done (G3a all clauses)** | S16, S17 §3 | `Qmode`, `RampLim`, `POD`, sub-blocks, 1.1 pu current limit not in the module yet (WP6) |
| 3b converters in network | **2 of 18 plants** (bus 33: Granada + temporary bulk-33), 20 s stable | S17 §4, `results\stage3i_network_b33\` | 16 plants + HVDC → WP3, WP4 |
| 4–10 | not started | | |

Budget now (`iberia4` build, state = `stage2\iberia4_gov.pscx`): **NODES 152 / 200, NPAGES 44 / 64**,
38–40 s wall per simulated second.

---

## 2. Rules — what went wrong before, and the rule that prevents it

The left column is what cost whole sessions in Sessions 1–17. The rule is the countermeasure.

| What happened (session) | Rule |
| --- | --- |
| The `pscad_*` tools vanished repeatedly and the executor drove PSCAD through a fallback script (S1, S5, S9). Cause found in S17: the client ignored `cwd` in `.mcp.json`. | **T1.** At session start: `pscad_status`. If the tools are missing, read the client's MCP log (Claude Code: `%LOCALAPPDATA%\claude-cli-nodejs\Cache\<project>\mcp-logs-pscad\`; opencode: `~\.local\share\opencode\log\opencode.log`) and quote the error to the user. `pscad_mcp` is now importable from any folder (a `.pth` file), so a `ModuleNotFoundError` should not recur. |
| The Ø in the project path breaks the build (S2). | **T2.** All PSCAD projects live in `C:\PSCAD_work`. Snapshots are *copied* into the project folder (`stage*\…pscx`) and never built there. |
| PSCAD exited and an unsaved bench was lost (S5). | **T3.** `pscad_save_project` after every successful step; copy a numbered snapshot after every gate. |
| Four sessions lost to per-unit bases (machine base S6, `source3` units S6, exciter base S7). | **M1.** Before tuning anything, compute the expected steady-state value by hand and compare it with a single measured number. If they disagree, the model is wrong, not the gains. |
| Four sessions lost to a controller fighting a 50 Hz rotation it did not know about (S13–S16). | **M2.** When a loop gets *worse* as the gain is reduced, stop tuning: the structure or the sign is wrong. Write down the plant equation in the frame you actually have. |
| The fixed-PF law "passed" with the wrong sign: the plant injected Q (S16; found S17). The current-measurement sign was assumed (S17). | **M3.** Every sign is checked against an **independent meter** in the same run: a source's own `P`/`Q` outputs, a multimeter, or a DC current. Write the check into the RUNLOG table. |
| `source3`/`source1` `Type` default "1 = R" made a "weak grid" purely resistive (S17). `source1` `R1p`/`L1p` are shunt (S16). | **M4.** For any source used as a grid: `Type = 4`, `Imp = IMPEDANCE`, `Z1`/`Phi1`, `ZSeq = YES` with `Z0`. Read all of it back. |
| Placing 240 components by tool calls; geometry fights; overlaps (S1–S4). | **B1.** More than ~10 components = **generate XML with a script** (pattern: `stage2\build_syncunit_xml.py`, `stage3\build_resplant.py --update`). Use tools only to place instances, read ports back and build. |
| The unbuilt `build_resplant1.py` had electrical tags on data ports and had removed the only current feedback (S16, found S17). | **B2.** A generated module is not done until (a) an instance shows the right ports (`pscad_get_ports`), (b) it builds with 0 errors, and (c) one run reproduces the bench numbers it was copied from, to the digit. |
| Work existed on disk but not in the RUNLOG (S7b, end of S16). | **L1.** The RUNLOG entry is written **before** the last build of the session, and updated after. Unfinished = say so, and give the file that holds the state. |
| `SyncUnit[n]` order changed between builds and Q values were swapped (S10). | **L2.** Identify instances by a unique measured quantity (`P/Pmec`, `Sbase`-scaled P, `VIT`), printed in the same row. For `RES_Plant[n]`, use the P magnitude (Sbase differs per plant). |
| Gates claimed on partial checks (THD window; PF magnitude only). | **G1.** A gate row has: required value, measured value, the window, and the independent check. If any is missing, the row is "open". |
| Long runs blocked the client (S1). | **R1.** Runs > 60 s wall: `pscad_run_project(wait=False)`. Completion = `pscad_get_run_output` shows `Simulation has ended`. Copy the `.psout` to `C:\PSCAD_work\<session>\<name>.psout` before the next run overwrites it. |
| A governor was first "tested" against an ideal source, which fixes frequency (S18). A figure script re-used for a new run overwrote an earlier stage's evidence (S18). | **R2.** Test a controller where its output can move the quantity it controls (governor → island; voltage control → a weak bus). **F1.** A figure script writes only to the folder of the run it was given; a new run gets its own folder name. |

More rules from Sessions 19–19b:

| What happened | Rule |
| --- | --- |
| The executor edited `PLAN.md` against instructions and then reverted it | **P1.** `PLAN.md` is **read-only** for the executor. Status, decisions and proposed plan changes go into the RUNLOG ("proposed plan change: …"). |
| PSCAD wedged with the project held, and every project call timed out (S19 §31, S19b §11) | **T4.** `pscad_disconnect` → `pscad_connect(prefer_launch=False)`; if still stuck, stop the PSCAD process and connect with `prefer_launch=True`. Then re-read and re-set the run parameters (T5). |
| A reload reset `time_duration` and `time_step` (D19-1, S19b §13.6) | **T5.** Set the run parameters **after** the last load and read them back just before every run. |
| A tripped module made a 120 s run "finish" in 15 s (S19b §18) | **R3.** A run that ends early or fast is a trip symptom until shown otherwise: check TRIP and VDF before using any number. |
| A run's per-bus numbers were lost because the next run overwrote the `.psout` (S19b §4) | R1 applies to **every** run whose numbers are used, however short. |
| `source3` `Vm` is the base voltage; the magnitude is `Es` (S19b §13.5) | **M5.** To change a source voltage, change `Es`; `Vm` silently changes the per-unit impedance. |
| Five cycles on one clause (W19b-4) | §0.10 is a hard stop at **3**. |

Rules from the Session 23 review of S22:

| What happened | Rule |
| --- | --- |
| Gates closed as "network/psse-limited" on a definition that is empty; "no series switch" while `breaker3` was proven in S18 | **M6.** Open the element or definition and quote its content before calling anything structural (§2c C5). Search the RUNLOG for the primitive before declaring it missing. |
| `fixed_load` `PO` read as total MW (8.4 GW instead of 25.2 GW) | **M7.** Write the unit/base of every number you read from a parameter (§2c C9). |
| All Stage 6–10 events inside the start-up swing | **R4.** Event runs start from a settled snapshot and prove the pre-event window (§2b S4–S5). |
| Prevention "tested" on forced cases, and "prevention" that moved the operating point | **R5.** §2c C6 and C7. |
| A pole slip read as a frequency collapse | **R6.** Print all five machine speeds whenever the frequency moves (§2c C4). |

### 2b. Testing method v1.0: settle once, then every test from a snapshot — **mandatory**

**Why it changed.** The v0.9 rule allowed 2–6 s runs "once values reach steady state", and assumed the
state settles in ≈ 2 s. It does not. The cold start releases the machines at 0.5 s from initial values
that do not match the network's real load flow. That excites the Iberia-vs-France inter-area swing
(±0.6 Hz, collector voltage ±0.1–0.3 pu), which needs **8–10 s** to die out (run 16). Every S22 event
at 3 s landed inside that swing (§1a.1). Short runs are still right; **cold-started** short runs are not.

**Cost.** A network run costs ≈ 5.5 min of wall time per simulated second (S22: a 6 s run took
≈ 30–35 min).

| Way of testing one event | Simulated | Wall | Valid? |
|---|---|---|---|
| S22 style: cold start, event at 3 s, 6 s run | 6 s | ≈ 33 min | **no** (event inside the swing) |
| Cold start, event at 12 s, 16 s run | 16 s | ≈ 88 min | yes |
| **Snapshot at 12 s once (≈ 77 min), then each event from it, 4 s run** | 4 s each | **≈ 22 min each** | **yes** |

So after the one-off settle run, every test is about **4× cheaper** than a valid cold-started one,
and a third cheaper than the invalid S22 runs. Ten event tests: ≈ 4 h instead of ≈ 15 h.

- **S1. Settle once.** Run ib5 from a cold start to 14 s with `SnapType = ONLY_ONCE`, `SnapTime = 12`,
  `snapshot_filename = ib5_settle12.snp` (pre-set in S23; read back, T5). Copy the `.snp` **and** the
  `.psout` to `C:\PSCAD_work\s23\` under a numbered name before anything else.
- **S2. The settle gate (G7a).** Read on 10–12 s and print every row; the snapshot is usable only if all pass:

  | quantity | required |
  |---|---|
  | all five machine speeds (`Wspd/2π`) | 50.00 ± 0.02 Hz, spread between machines < 5 mHz, p-p < 10 mHz |
  | collector `VDF` (all 18 plants) | p-p < 0.005 pu, no drift > 0.002 pu/s |
  | `TRIP` (18 plants), `BRKFR`, `BRK30/31/32/37` | all 0 |
  | `PTIE` (AC tie, Spain → France) | +335 ± 100 MW, sign checked (M3) |
  | HVDC P | 1,000 ± 10 MW export |

- **S3. Trim, don't guess.** If S2 fails:
  - **Frequency.** Settled f below 50 Hz means generation is short. The whole system's droop is ≈ **21.8 GW/Hz** (S22), so **1 mHz ≈ 22 MW**. Raise the France `Pmec` by that amount (France P0/Pmec in `prepare_ib5.py` or with `stage5\set_french_end.py`).
  - **Tie flow.** If `PTIE` is off its 335 MW, shift the plants together with `stage5\set_plant_dispatch.py --set-total-mw` by (335 − measured), and France by the opposite amount.
  - **Initial values.** Write each machine's settled `POUT`, `QOUT`, `VIT` back into its `P0`, `Q0`, `V0`, and set `Pmec = POUT/Sbase`. This makes the next cold start quieter (§2d).
  - Each trim is a cold re-settle, or a warm one by S6. **3 cycles maximum**, then record and stop.
- **S4. Every event test starts from the snapshot.**
  - Set `StartType = FROM_SNAP_FILE` and `startup_filename = ib5_settle12.snp`.
  - Time **continues from 12 s**, so every event time is absolute (> 12 s), and `time_duration` is the **end** time (12 + test length).
  - Verify both on the first snapshot run from the PSOUT time axis. If PSCAD restarts the clock instead, record it and shift all times.
  - Test length is 3–6 s after the snapshot.
- **S5. Pre-event proof in every event run.** The first 0.5 s after the snapshot start, before the event, must pass the S2 frequency and voltage rows. Print them as the first row of the gate table. A run that fails this has no result.
- **S6. What a snapshot survives.**
  - **Breaks it:** any edit that changes the build dimensions (`NODES`, `BRANCHES`, `PGBS`, `STOR*` in the `.map`: compare the files) or the component count.
  - **Recorders:** adding a recorder (`pgb`) changes `PGBS`, so choose every channel you will need **before** the settle run.
  - **Survives:** a value change in a signal block that acts only at or after the event, such as `compare X` (trip times), relay thresholds and delays, forcing times or the out-of-step threshold.
  - **Changes the pre-event state:** `Kpf`, `Qmode`, `Vset`, taps, reactor sizes, dispatch, line data. These need a new settled snapshot. Get it cheaply as a **warm re-settle**: start from the old snapshot with the new value, run 8 s, and take a new snapshot at the end (`SnapTime` = end). Check on the first warm re-settle that the new value is really active (one number in the PSOUT); if it is not, cold-start.
  - Name each snapshot after its state (`ib5_kpf030.snp`) and log it.
- **S7. Stacking** (old A3) only for checks whose cases each return to the S2 state before the next one (a reactor step, a load step). **A cascade is never stacked**: one cascade per run.
- **A2** (scaled time constants), **A4** (benches before networks) and **A5** (`sample_step` ≥ 100 µs) still apply.
  - 0.1 s and 0.5 s smoke runs are still fine for "does it build, run and write channels".
  - Runs of 20 s or more only for the final timed Case A/B replays.

### 2b-v1.2. Parallel and snapshot mechanics (S8–S12, measured in S25–S27) — **mandatory**

- **S8. Parallel runs.** Up to **8** EMTDC runs at once (Educational licence). Each run = 1 core for EMTDC +
  ≈ 2 cores for its PSCAD GUI → keep ≤ 7 when the machine is also in use, and set `sample_step` 500 µs in event
  runs. Tools: `stage12\make_variant.py` (experiment folder from a case + `spec.json` of event-only edits),
  `stage12\run_instance.py` (own PSCAD instance per run: build → copy `.snp` → run → wait → quit → log), and a
  batch launcher (`stage12\batch1.py` is the pattern). Launch ≥ 20 s apart. The MCP PSCAD is one more instance.
- **S9. Snapshot validity.** A snapshot is valid only for the **same project name** (`ib6` → `ib6.map`), the
  same build dimensions (`NODES`/`PGBS`/`STOR` in the `.map`) and the same **time step**. Copying the project
  folder elsewhere is fine; renaming is not.
- **S10. Warm-start checklist.** `StartType` = 1 (pass it explicitly — `pscad_set_project_parameters` can reset
  it to 0), `remove_time_offset` false (`Advanced` 38879), the `.snp` copied **after** the build (a rebuild wipes
  the build folder), then check the run config for `-start-snap` and the PSOUT `t0` (= snapshot time).
  `time_duration` is the run **length**.
- **S11. Long runs** write `SnapType` INCREMENTAL_MANY_FILES every 4 s, so a stopped or failed run is not lost.
- **S12. Agent-shell trap.** The shell sets `NoDefaultCurrentDirectoryInExePath=1`; a PSCAD launched from it
  cannot start `ib6.exe` ("not recognized"). `run_instance.py` clears it; any other launcher must too.

- **S14. Fixed run slots (firewall prompts).** Each `ib6.exe` listens on 0.0.0.0; Windows Firewall asks once per exe
  **path**. `run_instance.py` therefore builds and runs in one of 8 fixed folders `C:\PSCAD_work\slots\slot1..8`
  (lock file per slot, stale locks freed) and moves `ib6.gf81_x86` back to the experiment folder at the end (plus
  `ib6_as_run.pscx`). While a run is going, its PSOUT is in the slot (the lock file names the experiment).
  Allow or block makes no difference to the run (measured S27). `--noslot` = old behaviour.

- **S13. What a snapshot freezes (S27, from the generated Fortran — no test runs needed).** A snapshot restores
  all EMTDC storage. Parameters used only in `<Def>Dyn_Begin` (set-up at t = 0) keep their **snapshot value**;
  parameters read in the per-step `<Def>Dyn` body take effect. Check any parameter with
  `python stage12\snap_live.py <build folder> [Def ...]` before relying on it.
  FROZEN: `SyncUnit` H, ratings, P0/Q0/V0/Ph0, Vctl, Tstart, **KA/KF/TF** (AVR reference = start-up voltage);
  `fixed_load` **PO/QO/NP/NQ/VBO** (stored inside the `.snp`); `RES_Plant` Sbase, Lf/Cf/Rf, CarrPh, Nsub; any
  structural edit; the time step.
  LIVE: Pmec, Kgov/Tgov/GovLim, Ttrip/Ptrip, `BRK3x`; all other `RES_Plant` controls and relays (Pref, Kpf, Imax,
  RampLim, Vt/Tt 1–3, MeasSide, Qmode, Vset, Tforce, Trel); control-block constants (LFDD/pump/P2 thresholds,
  HVDC Qmax/Qmin); run length and output step. Evidence: r6 (H) bit-identical; trim3 (Pmec) worked; load PO
  literal found inside `ib6f_07.snp`.

### 2c. Reading results — the analysis discipline (new in v1.0)

S22 produced many numbers and many wrong conclusions. In almost every case the error was in the
**interpretation**, not the simulation. Before any sentence of the form "X passes / fails / prevents /
is limited by Y" goes into the RUNLOG, do these checks and write their result next to it.

- **C1. Look at the whole trace, not a window mean.**
  - Print min / max / p-p and the slope of every quantity you quote, over the full run, and make the figure before writing the conclusion.
  - A mean of an oscillating signal is not a state (S22 averaged 0.34–1.40 pu voltages into "1.05").
- **C2. Predict first (M1).** Write the expected number from a one-line formula *before* the run, then compare:
  - RoCoF = ΔP · 50 / (2 · KE), where KE is in MW·s: the Iberian KE is 119,500 MW·s, so 1 GW lost ⇒ ≈ 0.21 Hz/s after separation;
  - tie angle δ = asin(P · X / V²);
  - ΔV ≈ ΔQ × the measured sensitivity (≈ 17 kV/Gvar at bus 9, S21 run 6);
  - frequency offset × 21.8 GW/Hz = imbalance.

  If measurement and prediction differ by more than a factor of about 1.5, find out why before going on.
- **C3. Balance every run.** Σ generation (unit `POUT` + plant P) − Σ load (at the measured V, `NP = 1`) − HVDC − `PTIE` = losses, which should be 0–3 %. A run that does not balance is not understood.
- **C4. All machines, every time.** When the frequency moves, print **all five** machine speeds, France included.
  - Divergence between Iberia and France is **loss of synchronism**, not a frequency collapse (run 96).
  - After a breaker opens, that unit's channels describe an isolated machine: stop using them.
- **C5. Never blame what you have not opened.** "Network-limited", "structural" or "the library cannot" is allowed only after you have (a) opened the element or definition in question and quoted what it contains, and (b) shown the claim with one independent measurement.
  - The empty `psse` (§1a.2) and the "missing" breaker (§1a.3) both failed this.
- **C6. Forced vs emergent.**
  - A forced trip schedule tests how the system **responds** to the trips. It can **never** show that a measure *prevents* them.
  - Prevention is tested only on an **emergent** case, where the trips come from the relays.
- **C7. A prevention result must keep the operating point.** Before calling a measure "prevents", show that the pre-event state with the measure is still inside the report's band: 400 kV 400–420 kV, collectors ≈ 1.06 pu, f 50 Hz, the same dispatch and tie flow.
  - A measure that drops the grid to 0.5–1.0 pu (Kpf −0.30) is not prevention.
- **C8. Match ≠ explain.** A number near the report (0.690 vs 0.63 Hz) is evidence only if the **mechanism** is the same: the same source, the same mode shape, the same trigger. Say which.
- **C9. Units and bases.**
  - `fixed_load` `PO`/`QO` are **per phase**.
  - KE in GW·s = MVA · H / 1000.
  - Multimeter P is in units of its `S` (S = 1 gives MW).
  - `Ph` from a multimeter is an absolute angle wrapping at ±180°: use cos/sin of a difference, never a raw difference.
- **C10. Write the falsifier.** For each conclusion, write one line: "this would be wrong if …", and the cheapest check of it. Do that check when it costs no extra run.
- **C11. Self-review before the session ends.** Re-read your conclusions of the session against C1–C10. Mark any that fail **"unverified"** rather than "pass/fail".

### 2d. Initial conditions — what the cold start does, and how to make it quieter

- **SyncUnit.**
  - Until `Tstart` (0.5 s) each unit is an ideal source at `V0` ∠ `Ph0` (Ph0 in **radians**). At `Tstart` it is released to its swing equation with `Pmec` and its AVR.
  - `P0`/`Q0`/`V0`/`Ph0` are only the source's initial point. If they disagree with the network's real load flow, the release is a step, and that step is the inter-area swing of §2b.
  - In ib5 the dispatch changed by several GW but `Ph0`/`V0`/`Q0` are still those of ib4hv: **expect a larger start-up swing**. That is why the settle runs to 12 s and why the tie relay is armed only after 11 s.
- **Plants.** Pref ramps on a `master:upramp` (`X1`–`X2` s) from `TSIG`, at fixed PF (`Kpf` −0.1752, `Qmode 0`). The overvoltage relays are parked at `Vt 1.5` for the settle; set the report's fleet values (`stage7\tune_ov_relays.py`, `data/parameters.md` §3) **only in the event runs**. That is a post-event-safe change by S6.
- **HVDC.** Constant P 1,000 MW (`PMODE 1`) from the start.
- **France.** It runs at 200 GVA / H 25 s and governs the frequency while the tie is closed (`Kgov` 5). Its 5,000 GW·s matter only *while connected*; once `BRKFR` opens, Iberia runs on its own 119.5 GW·s, as in the report.
- **Making it quieter (after the first settle):** write the settled `POUT`/`QOUT`/`VIT` back into each unit's `P0`/`Q0`/`V0` and `Pmec` (S3). `Ph0` can stay: the swing is driven by the P mismatch.
  - Record the settle time (when every S2 row first passes) before and after. If it falls below about 8 s, the settle run may be shortened in a later session; until then, keep 12 s.

### 2e. Breakers and trip commands (ib5 → ib6; S27 adds `Tforce` per plant and `Ttrip`/`Ptrip` per unit)

| Breaker | Where | Control signal | Default | How to operate it |
|---|---|---|---|---|
| `BRK30` | 6,113 MVA unit ↔ Bus30 | `compare(time > X)`, row y = 400 | X = 1e6 (never) | set `X` = absolute trip time |
| `BRK31` | 13,548 MVA unit ↔ Bus31 | row y = 402 | never | same |
| `BRK32` | 15,292 MVA unit ↔ Bus32 | row y = 404 | never | same |
| `BRK37` | 12,838 MVA unit ↔ Bus37 | row y = 406 | never | same |
| `BRKFR` | France terminal (with the French load) ↔ Bus39 = **the AC tie** | out-of-step relay, rows y = 412–426, latched | trips at \|Δδ\| > 120° after 11 s | automatic. **To force it at time T** (Case A replay): set the threshold compare (row 412) `X` = 1.01 (always true) and the arming compare (row 418) `X` = T |

- **Polarity:** `breaker3` signal **0 = closed, 1 = open** (S18, and `NINT(1.0−BRK…)` in the compiled `Main.f`).
- **Opening:** at current zero (`OPCUR 1`), with `ROFF` 1e6 Ω (0.16 MW leakage at 400 kV: negligible).
- **Unit trips are breaker trips.** The old `EN` torque gate is not in ib5; do not re-add it. After a unit breaker opens, that unit is an isolated machine, so ignore its speed and power from then on (C4).
- **Reactors stay.** The 400 kV reactor labels `SH30/31/32/37` are on the bus side of the breakers.
- **The relay** compares `Ph39` (France terminal, machine side of `BRKFR`) with `Ph9` (Iberian end).
  - WP8 calibrates the tie so that the slip happens at the report's import (−3.6 to −3.9 GW).
  - If the relay chatters or trips on a non-slip transient, add a 20–50 ms `delay` before the latch, as one build.
- **Node budget: 197 of 200.**
  - Signal-only additions cost nothing.
  - A new series element costs 3. The free nodes are reserved; ask yourself whether the measurement can come from an existing channel first (`POUT`, `QOUT`, `VIT`, `PTIE`, `VDF`).

Ask the user only for: a decision that changes a documented user decision (PLAN_OLD.md header table),
a missing licence/tool, or a GUI-only step. Everything else, decide yourself and record the
alternatives in the RUNLOG.

---

---

## 3a. Work order v1.2 — batches (WP7–WP11 regrouped for parallel runs)

Each batch: (1) all structural edits in **one** generator script and **one** build; (2) one cold settle — or
several in parallel when a pre-event quantity must be bracketed; (3) a smoke run; (4) the experiments in
parallel from the settled snapshot; (5) one analysis script per batch and the gate tables in the RUNLOG.
The WP texts below define the **gates**; the batches define **when** they are run.

### Status of Batches 0–1 and Batch 2b / F (v1.3)
- **Batch 0 done:** G7a 13/14 at `C:\PSCAD_work\s27\trim3\ib6e_03.snp` (t 36 s).
- **Batch 1 done** (RUNLOG S27 §9, §12): r2 WP8.4 PASS; r3 WP7.6 PASS per Gvar; r1 relay + LFDD/pump PASS, import
  6 % short (tie → 76 Ω in s28); r8 Case A sequence as in the report (`BRKFR` 0.58 s early); r4 Case B no cascade;
  r6 invalid (H frozen); r5/r7/r9 stopped. **Batch 1b (Case B2) done** (§13): onset ripple-driven, invalid as a replay.
- **s28 settle done** (`C:\PSCAD_work\s28\snaps\ib6f_01..07.snp`): clean, but load buses 1.14–1.165 pu.
- **Batch 2b running** (`C:\PSCAD_work\s29b\c1..c5`, case `C:\PSCAD_work\s29\ib6.pscx` = s28 + `Trel`): cold 28 s
  brackets of the FROZEN reactive items — load absorption 4 / 6 / 8 Gvar (NQ 2, shared by PO), 6 Gvar + unit
  KA 10, 6 Gvar at 10 µs. Pick: load buses 400–420 kV, unit absorption small, collectors ≈ 1.06, Granada 1.061.
- **Batch 2b done (RUNLOG S27 §19):** uniform load Q (by PO) lowers the collectors faster than the load area; no single
  value fits both targets. Snapshots in `C:\PSCAD_work\s29b\c1..c4\snaps\`. The PF tool does not match the EMT yet
  (`qdesign.py`, §19) — design by EMT brackets. **Batch F0 running (§20):** parked Case B2 from c1–c4 (voltage-rise
  sensitivity, relay filters offline) + cold settles d1/d2 with absorption off the RES buses (KA 40 / 10).
- **Batch F0 done (RUNLOG S27 §21):** local dV per GW tripped matches the report (+0.011 vs +0.012 pu; Table 4-26
  short-circuit power predicts it); the units do not clamp; the pre-event profile geography, the slow drift after event 3
  and the Iberia-France dynamics are wrong. **Direction under discussion: a reduced Iberian equivalent (≈ 13–15 buses)**
  in place of IEEE-39; Batch F below is on hold until that is decided.
- **Batch F (fidelity) next, from the picked snapshot, in parallel:** warm Pmec trim (LIVE) to PTIE ≈ +335 MW and
  Iberian units ≈ 11.95 GW; then Case B2 with `Trel` 0.001 / 0.02 / 0.06 s, the parked control (C6), and
  Case A. **Replay gate:** no trip between events 3 and 4a; slow 400 kV rise after event 3 (+4 kV over 19 s);
  after 4a a relay-driven cascade tracking Fig 3-7a's cumulative loss within ±20 % at 77.6 / 78.4 / 79.1 s;
  `BRKFR` 81.407 ± 0.5 s on the Case A clock; Iberia f and PTIE vs Fig 4-91. Only after this gate: WP11 (P1–P7,
  P1/P7 from their own cold or warm re-settles per S13).

### Batch 0 — the S27 bundle and its settle (WP7 close-out) — *running in S27*
- Build: `stage12\add_bundle_s27.py` (Tforce, Ttrip/Ptrip, pump tranches, tie 83 Ω) on the S26/S27 case.
- Settle: three cold 32 s brackets in parallel (`C:\PSCAD_work\s27a/b/c`, PTIE 0 / +400 / −400 MW at constant
  system total). Pick the bracket and the snapshot (16…32 s) that pass §2b S2 best; interpolate the trim if
  none passes PTIE, and carry the residual into Batch 2.
- **Gate G7a** (§2b S2 rows; the 17 Hz collector-ripple row is known-open at 20 µs, D26-1) and the WP7 step 5
  voltages (Granada 1.061 ± 0.01; 400 kV 400–420 kV).

### Batch 1 — eight experiments from the Batch-0 snapshot (`stage12\batch1.py`)

| run | experiment | gate |
|---|---|---|
| r1 | `BRK31` at T0+1, `BRK32` at T0+1.5 | **G8a**: peak PTIE import −3.6…−3.9 GW before the slip; `OOS1`/`BRKFR` at 120°; France ≈ 50 Hz; WP9: S1…S6 and SP1/SP2 fire in order and each tranche's current → 0 |
| r2 | plants 5 + 6 forced (≈ 0.94 GW) | **WP8.4**: `BRKFR` stays closed |
| r3 | Granada plant 1 forced, relays parked | **WP7.6**: Granada/Carmona +3…7 kV (p.217); also the Case B control |
| r4 | **Case B**: report OV settings (`ov_report`), HVDC Q = 0 (report: 7.7 Mvar), Granada initiator | **WP10.2**: first trips, cascade fraction vs Fig 3-7, `BRKFR` time |
| r5 | r4 + **P5** (no OV setting ≤ 1.10 pu: raised to 1.111) | WP11 row (C7 check) |
| r6 | r4 + **P7** (Iberian H 2.5 → 3.0) | WP11 row — expected **not** to prevent (p.302) |
| r7 | r4 + **P6** (HVDC Q(V), limits +0.4/−0.6 pu) | WP11 row |
| r8 | **Case A** forced replay (`stage12\caseA_spec.py`: plants by `Tforce`, nuclear/CC by `Ptrip`, real time from 76.4 s) | **WP10.1**: f Iberia vs France, PTIE swing, 400 kV `VIT`, `BRKFR` time vs 12:33:21.4 |

r5–r7 are speculative: interpreted only if r4 cascades (C6). If r1 misses the import band, the tie value is one
more line-data item in Batch 2's build.

### Batch 2 — pre-event measures, the final trim, and fixes found in Batch 1
- One build with every structural item Batch 1 asks for (e.g. P2 switched reactors as `varrlc` L at the 400 kV
  reactor buses, closing on V > 1.05 pu; a corrected tie X if r1 needs it).
- Parallel **warm re-settles** (12 s each) from the Batch-0 snapshot, one per pre-event change: P1 (RES Q(V)
  with the pre-event Q unchanged), P3 (unit absorption), the final dispatch trim (PTIE / f residual).
- Then Case B on each re-settled state, in parallel.

### Batch 3 — confirmation
- From the final snapshot: Case B and Case A once more; the measures that prevented in Batch 2 with the C7
  check; **one** 20 s confirmation of the best case.

### WP gate definitions (content unchanged, ib6 wording)

### WP7 — Settle, close the balance, set the pre-event state (G7a, G4 at fixed PF) — Batch 0

**Input:** `C:\PSCAD_work\s23\ib5.pscx`, run settings pre-set (14 s, 20 µs, 200 µs, snapshot at 12 s).

**Steps:**
1. **Load and build** (T5): expect 0 errors, NODES 197, NPAGES 27. Check the recorders you will need: tie (`PTIE`/`QTIE`), angles (`Ph9`/`Ph39`), `BRK*`, `OOS1`. Add any missing **now** (S6).
2. **Cold settle run**, `wait=False` (R1). Archive the `.psout` and `ib5_settle12.snp` (≈ 77 min wall).
3. **Settle gate** (§2b S2): print the table plus the §2c C3 balance and the five machines' `POUT`/`QOUT`/`VIT`.
   - Record the time at which every row first passes. That is the measured settle time.
4. **If any row fails:** trim (§2b S3) and re-settle. 3 cycles maximum.
5. **Pre-event voltages, fixed PF only (`Qmode 0`).**

   | quantity | target (report) |
   |---|---|
   | Granada collector (bus 33, plant ch1 `VDF`) | 1.061 pu (p.122) |
   | 400 kV units' `VIT` | 400–420 kV (p.12); Carmona 409 kV at 12:32 (Fig 3-5) |
   | Iberian units' `QOUT` | absorbing (reactive-surplus grid) |

   Levers, in this order, each by **warm re-settle** (§2b S6):
   - collector taps (`stage5\tap_trim.py`);
   - 400 kV reactor sizes (`SH*` loads);
   - France `V0`.

   **Not** Q(V) droop, **not** `Kpf`.
6. **Sensitivity check from the snapshot** (one run, two stacked steps, S7):
   - +165 Mvar off at Granada, i.e. a 165 Mvar step of a shunt **capacitor** at B33 (signal-switched; or trip ch1 if no switchable element exists);
   - then +150 Mvar of reactor at bus 31.

   Report: Carmona/Granada region +3–7 kV for the first, −3–4 kV for the second (p.217). Record what the model gives; do not tune to it yet.

**Gate G7a:** every S2 row passes on 10–12 s **and** step 5's targets are within ±5 kV / ±0.01 pu. Archive `stage11\ib5_g7a.pscx` and the `.snp`.

**Stop:** 3 cycles on one row → record the measured numbers, the predicted ones (C2) and why they differ, then go on to WP8 with the best snapshot.

### WP8 — The France tie: breaker tests, loss-of-synchronism calibration (G5 clause 3, G8a) — Batch 1 r1/r2

All runs from the G7a snapshot, 4 s each.

1. **Unit breaker test.** `BRK31` X = 13.0 s. Read:
   - the unit's terminal current, which must go to 0 within one cycle;
   - all five speeds: France stays ≈ 50 Hz, Iberia dips;
   - `PTIE` rising toward import.

   Compare the RoCoF with C2: ΔP = the unit's `POUT`, KE = 5,119.5 GW·s while connected.
2. **Loss-of-synchronism calibration.** Trip `BRK31` at 13.0 s and `BRK32` at 13.5 s (≈ 8.4 GW lost together: well beyond the ≈ 4 GW tie capability).
   - Read `PTIE` peak import before the slip, the time `OOS1` first fires, `BRKFR`, and the Iberian speeds after separation.
   - **Target:** peak import before slip −3.6 to −3.9 GW (Fig 4-91: PMU −3,566, sim −3,847 MW); `BRKFR` opens; after opening, France ≈ 50 Hz and Iberia falls at the C2 RoCoF with 119.5 GW·s.
3. **If the peak is off:** Pmax ∝ 1/X, so `K_TIE,new = K_TIE · (measured peak / 3,700)`.
   - In ib6 the tie is the two pi-sections 1600000039 / 1600000099 (S27: 83 Ω each). A new value goes into the
     next batch's build script and its cold settle (no extra cycle).
4. **Relay robustness.** In a run with a large but *stable* disturbance (one plant group force-tripped, about 1 GW), `BRKFR` must **not** trip.

**Gate G8a:** steps 1–4 pass; the tie flow and angle traces are in the figure set.

### WP9 — Real LFDD MW shedding (G5 clause 1, Stage 8 counterfactual 2) — built S26/S27; gate in Batch 1 r1

The S22 blocker is withdrawn (§1a.18). The shed is modelled as **signal-controlled shunts at the load buses**, which cost no nodes.

1. **Element:** `master:varrlc`, a signal-controlled R/L/C branch with ports A–B; each phase from the bus to ground.
   - Use it as a resistor R = V² / P_tranche while connected and ≈ 1e8 Ω once shed, driven by the LFDD ladder signals `S1…S6` (already built, `stage5\build_lfdd_relay.py`).
   - Fallback: `master:src_ccin_1`, a current source driven by a signal on its `Mag` pin. Use it in parallel with the load, injecting −i_load · share after the shed: three per bus, bus to ground.
   - Bench it first (A4): one bus, one load, one tranche. Read the ports with `pscad_get_ports`; do not assume them.
2. **Tranches:**
   - **Where:** put the six Spanish tranches (`data/parameters.md` §5: 1,175.9 / 1,669.1 / 1,574.6 / 1,523.9 / 1,294.3 / 1,267.1 MW) on the largest Iberian loads.
   - **Total demand unchanged:** reduce those `fixed_load` `PO` (per phase) by the same MW.
   - **Gate:** each tranche sheds its MW ±3 % within 0.2 s of its threshold crossing, measured by the load bus P balance.
3. **Pumping load** is part of the shed in the report (Table 3-2, −2,756 MW of pumped hydro). Represent it as one more switchable tranche at the threshold the report gives, and record the choice.

### WP10 — Replay the event from the snapshot (Stages 6–7, redone) — Batch 1 r4/r8

1. **Case A (forced)**, 6 s from the G7a snapshot.
   - Plant trips by the per-plant `Force` nets (`stage6\build_event_table.py`).
   - Unit trips by `BRK3x`: nuclear 1,045 MW at 12:33:22.7 etc. (`data/parameters.md` §6).
   - The tie opens **by the relay**, not forced.
   - Compressed clock as in S22 (`t = 12 + 0.5 + (t_rep − 77.22) · k`). Choose k and record it.
   - **Score against A3 and Figs 3-7/4-91:** frequency (Iberia vs France), the `PTIE` swing, the 400 kV `VIT`, and the time of `BRKFR` vs 12:33:21.4 (p.119).
2. **Case B (emergent).**
   - Report fleet OV settings applied (event-only change, S6).
   - Only the Granada initiator forced: ch1 trip at its report MW and its 165 Mvar absorption, p.126.
   - Everything else must come from the relays.
   - Score: first trips, cascade fraction vs Fig 3-7, `BRKFR` time.
   - **Do not tune relay thresholds to the result** (the S22 `tune_ov_relays` values are the report's settings, keep them). If the cascade does not emerge, report the measured voltage margin to each relay (C1) and the C2 prediction.
3. Each case gets its figure set in its own folder (F1). Then **one** 20 s confirmation of the best case only.

### WP11 — Prevention measures (Stage 9), on the emergent case only (C6, C7) — Batches 1–3

Each measure is one change, tested from its own settled snapshot (warm re-settle) if it changes the pre-event state, or from the G7a snapshot if it acts only after the event. Each row of the table reports the C7 pre-event check, the trips, the plant MW lost, whether `BRKFR` opened, and the Iberian f minimum.

| # | Measure (report source) | How in the model |
|---|---|---|
| P1 | RES in voltage control instead of fixed PF (p.298, §4.4.3.4: "voltage regulation by static generators") | `Qmode 1` Q(V) droop, Vset = the measured fixed-PF pre-event voltage, so the pre-event point is unchanged |
| P2 | Automatic shunt-reactor connection during the voltage rise (§4.4.3.4) | signal-switched 150 Mvar units (`varrlc` as L, or `breaker3` if nodes allow) at the 400 kV reactor buses, closing on V > 1.05 pu |
| P3 | More reactive absorption by the synchronous units (§4.4.3.4) | AVR/limit setting so the units absorb, or raise their Q capability |
| P4 | Eight 250 MVA synchronous condensers **on the 400 kV grid**, voltage-controlling (p.310) | as S22's clones, but on 400 kV buses, `Pmec 0`, `Kgov 0`, AVR at the bus's pre-event voltage (so they absorb when V rises) |
| P5 | OV protection compliant with the 1.10 pu / 60 min requirement (p.141–142) | fleet `Vt` ≥ 1.10, the delays of the requirement |
| P6 | HVDC reactive support / power reversal (§4.4.2.4; −600 Mvar capability, p.102) | HVDC Q at its absorption limit during the rise; reversal 1 GW export → 1 GW import at maximum import |
| P7 | Inertia +20 % (report: does *not* prevent, p.302) | the control case, which should **not** prevent |

The prevention claim needs P7 to behave like the report (no prevention) **and** at least one of P1–P6 to prevent with the C7 check passed.

---

## 3. Work packages WP1–WP6 — v0.9 HISTORY (WP1, WP2, WP4 done; WP3/WP5/WP6 are superseded by WP7–WP11 in §3a)

Each package has inputs, steps, a gate with numbers, a stop condition and a size estimate. A
"cycle" is one build + one run + one check.

### WP1 — Governor and AVR gains in `SyncUnit` — **DONE (Session 18, G2c passed)**

What exists now (details and numbers: `RUNLOG.md` Session 18):

- **`stage2\add_governor.py`** patches the `SyncUnit` definition. To give another project the same
  definition, run `python stage2\add_governor.py --src <pscx holding an UNPATCHED SyncUnit> --dst <pscx>`.
  The unpatched canonical copy is `C:\PSCAD_work\s17\iberia4_pre_gov.pscx`. The script refuses to
  patch twice; to copy an already-patched definition, take it from `stage2\iberia4_gov.pscx`.
- **Governor:** `Wspd → ×1/314.159 → (1 − w) → ×Kgov → realpole(Tgov, +GovLim/−0.3) = DPGOV`;
  `TMECH = Pmec + DPGOV`. New parameters `Kgov`, `Tgov`, `GovLim`. **Kgov is on the unit's own
  Sbase, which is inflated for inertia,** so `Kgov = (1/R)·P_rated/Sbase` and
  `GovLim = (P_rated − P0)/Sbase`.

  | unit | Kgov | Tgov | GovLim |
  | --- | --- | --- | --- |
  | hydro 30 | 5.726 | 2 s | 0.054 |
  | CCGT 37 | 4.362 | 5 s | 0.043 |
  | nuclear 31/32 | 0 | — | — |
  | France 39 | 5.0 (20 GW/Hz) | 3 s | 0.05 |

  All are *design* values; calibrate them in Stage 5 against the report's frequency traces (Fig 1-10 and p.198-200).
- **AVR:** `KA`, `KF`, `TF` are now instance parameters bound to the exciter (`KA_1`, `KF_1`, `TF_1`),
  with defaults equal to the proven values. A fast AVR (M6) is a parameter change. `Vctl` is
  obsolete; leave it at 0.
- **Island bench** `stage2\su2_governor_island.pscx`: two units, 132.6 MW load, +13.3 MW breaker step
  at 10 s (`BRK = 1` = open). Reuse it for any later governor or AVR change.

Carry forward:

- The ≈ 14 s governor mode (ζ ≈ 0.04, driven by France) must be re-checked when the last ideal
  source is removed (WP3).
- The governors do not damp the ≈ 0.6 Hz electromechanical mode; that stays a WP5 item.

### WP2 — Free the module pages: flatten the 34 PI line modules

**Why:** NPAGES is 44 now. 16 more plants + HVDC + Defence + Sequencer + TieProt = 64 = the limit,
with no spare. PLAN_OLD.md B2 intended PI *components* on Main; the conversion (S3) left each line
inside its own `T<a>_<b>` module page.

**Steps (script, rule B1):** `stage1\flatten_lines.py`. For each `T<a>_<b>` instance on Main:

1. read the PI component and its parameters from the definition canvas;
2. place the same component on Main at the instance's position, with its two ports on the instance's two port coordinates (read both with `pscad_get_ports` first; compute orientation from them);
3. delete the instance.

Do three lines, build and compare; then do the rest.

**Gate G1b:** NPAGES drops by 34 (to ≈ 10); NODES unchanged (±0); every multimeter `Pd`/`Qd` and
every `VIT` equal to the pre-flattening run within 0.1 % (same 3 s run, same `.psout` channels).

Size: 3–5 cycles. **Stop if** NODES changes. A node change means a port was not landed exactly.

### WP3 — Remaining plants, one collector bus at a time (G3b)

**Inputs:**

- `stage3\build_resplant.py` and its `plant_params(Sbase, Vbase=400, pf=0.985, vt, tt, carr_ph)`;
- `iberia4` (bus 33 done);
- PLAN_OLD.md B1 table (plant list per bus);
- `stage3\s17\plant_report.py`.

**Generate the placement too (rule B1).** The pattern per plant is known:

- Instance at (x, y). Its ports are AC (x+3, y−2), DCP (x+3, y), DCN (x+3, y+2), Pref (x−3, y−2), Force (x−3, y), Trip (x−3, y+2).
- Labels sit on those points: nodelabel `B<bus>`, `RAILP`, `RAILN`; datalabel `PR<k>`, `FRC`.
- One `upramp` per plant from the shared `time-sig`.

Write `stage3\place_plants.py`, which adds these to Main's XML for a list of plants (unload the
project → script → load → build, i.e. skill P12; this is a bulk structural edit, which P12 allows).

**Dispatch during Stage 3 (structure only, decided):**

- Every plant gets its PLAN_OLD B1 **Sbase** (named plants: MW/0.9 rounded up; cluster and bulk plants: the sum of their sub-blocks).
- The **Pref** of all plants on a bus is scaled by one factor `k_bus`, so that the bus total equals what that bus's ideal source delivered: bus 34 2,104 MW, bus 35 2,708 MW, bus 36 2,323 MW, bus 38 3,452 MW (S10 `Pg5…Pg9` × 410.4 MVA).
- Stage 4 then sets the real dispatch.
- **Do not let `k_bus` exceed 1.0.** Bus 34's B1 plants sum to ≈ 3.2 GW > 2.1 GW, so `k_34` ≈ 0.66. That is fine. If a bus's plants sum to *less* than its source, add the shortfall to that bus's bulk/cluster plant and record it.
- Bulk-33 (the temporary 2,550 MVA plant) becomes PLAN_OLD B1's bulk plant 1 when Stage 4 moves the bulk to bus 35/38. Leave it at bus 33 until then.

**Carrier phases:** stagger per bus: 0°, 90°, 45°, 135°, 22.5°, … Keep a table in
`data\parameters.md`.

**Relays during Stage 3:** `Vt = 1.25`, `Tt = 0.05`, i.e. parked; real settings come in Stage 7.

**Order:** bus 36 (6 plants), 34 (7), 35 (3), 38 (4 incl. bulk 2); then remove the last ideal
source. WP1 has passed; when the last ideal source goes, re-run the G2c network check (±0.02 Hz after 20 s) and watch the ≈ 14 s governor mode.

**Per bus, the gate:**

- 0 errors;
- NODES increase = 3 × plants − 3 (the deleted source) + 0, or +3 if a multimeter terminal becomes a node — write down which;
- 20 s run: every plant's id/iq within 2 % of reference after 5 s, no trip, every machine frequency within ±0.02 Hz after 15 s, figure set `results\stage3j_bus<N>\`.

**Node budget (projected):**

| item | nodes |
| --- | --- |
| current state | 152 |
| 4 more ideal sources removed (hidden nodes) | −12 |
| 16 more plants × 3 | +48 |
| HVDC terminal | +3 |
| Granada evacuation transformer + breaker (Stage 4, B2) | +6 |
| **total** | **≈ 197 / 200** |

If the build exceeds 200, cut in this order: (1) remove the 5 multimeters at the collector buses
(3 nodes each; measure bus voltage inside a plant instead: `VA_PU`/`VDF`); (2) PLAN_OLD A4's list
(merge the smallest named plants into their cluster plant). Record the exact licence error text,
which Stage 0 still owes.

**Run time:** 38 s per simulated s with 2 plants. Expect ≈ 150–250 s/s with all plants. Each 20 s
check is then ≈ 1 h; use `wait=False` (rule R1) and write the RUNLOG meanwhile.

**Known artefact (do not chase):** each plant's phase current shows 10–30 % THD. This is
common-mode current circulating between plants through the shared DC rail, because the model has no
plant transformer. It cancels in the grid current (1.5 % THD) and the dq controllers cannot see it
(S17 §3). Check grid-side currents (bus multimeters, `stage3\s17\cm_check.py`), not plant phase
currents.

Size: 2–4 cycles per bus.

### WP4 — HVDC Spanish terminal (`HVDC_T`)

**Design (decided):** a second definition generated by the same script. Add a `--hvdc` mode to
`build_resplant.py` that copies the same bridge, PLL and current loop and replaces the outer
references:

- **P channel:**
  - `PMODE = 1`: `id_ref = −P0/Sbase`. Negative means the terminal absorbs P from the AC side, i.e. exports to France; check the sign with the grid-side meter (rule M3).
  - `PMODE = 3`: `id_ref = −K·(θ9 − θ39)/(1 + s·T)/Sbase` with K = 360 MW/°, T = 50 s. The angles come from the bus-9 and bus-39 multimeter `Ph` channels, which already exist.
- **Q channel:** `iq_ref = PI(Vset − VDF)` with limits +0.4/−0.6 pu on 2,000 MVA (report p.102: +400/−600 Mvar per link) and P priority. Baseline must reproduce ≈ 0 Mvar at 410 kV (report p.136). Read Fig 2-97 (p.103) for why before choosing `Vset`/the deadband.
- **Block:** the same latch; trip on AC undervoltage (Case B) or `Force` (Case A at 83.96 s).
- **French end:** PLAN_OLD.md says "equal injection at bus 39". **Measure first** which is cheaper:
  - (a) a second `RES_Plant` instance at bus 39 with `Pref = +P_hvdc` (3 nodes, exact);
  - (b) a `fixed_load` with negative P (0 nodes; S1 found negative `PO` drew zero power, so probably not usable);
  - (c) a controlled current source (search `master.pslx` for one; check its node cost on a bench).

  Pick the cheapest that works.

**Gate G3c (bench, then network):**

- Constant-P mode holds 1,000 MW ± 2 % through a ±5 % AC voltage step.
- AC-emulation mode follows a forced 2° angle step with the 50 s lag (63 % at 50 s; run 120 s on the bench only).
- Q stays ≈ 0 at 410 kV in baseline.
- In the network: 1,000 MW export, 20 s stable.

Size: 8–12 cycles.

### WP5 — Stage 4 operating point: turn the IEEE-39 equivalent into a **reactive-surplus** grid (v0.9, NEXT)

**The missing mechanism (Session 20, measured from the model file).** The event needs a grid with
*excess* reactive power *before* anything trips. The 400 kV lines were lightly loaded (below their
surge-impedance loading), so their charging exceeded their I²X losses: voltage rose along them, and
operators needed reactors (PLAN_OLD A1, p.12, p.17). Only then does a plant trip *raise* the voltage
(less absorption on a capacitive grid), which is the positive feedback the cascade is made of. The
IEEE-39 equivalent is the opposite:

| | model now | Spanish grid (order of magnitude) |
| --- | --- | --- |
| line charging, 400 kV | **4.2 Gvar** (34 PI lines, ΣC = 84.45 µF) | **≈ 11.5 Gvar** (≈ 21,000 km × 0.55 Mvar/km), plus the 220 kV grid |
| load Q | **5.8 Gvar inductive** (PF 0.975, IEEE data × K) | small or capacitive at midday, seen from 400 kV (report §4.1.2: DSO→TSO reactive flow) |
| line loading | IEEE-39 transfers, near or above SIL | lightly loaded |
| result | reactive **deficit**: machines at the AVR ceiling, collectors collapse | reactive **surplus**: 410–420 kV with reactors in |

In such a grid a plant trip *lowers* the voltage, so the event cannot be reproduced on it whatever the
plant settings. This is the root of D19b-4. **Do not** fix it with Q(V) droop, synchronous condensers
or STATCOMs in the baseline: those are mitigations M1, M4 and M5.

**Levers, in this order — each a parameter edit by script (rule B1), each checked with a short stacked run (§2b):**

1. **Line charging to Spanish scale.** Multiply every `pi_section`'s capacitance (`Cp1`, and `Cz1` in
   proportion) by `k_c`, keeping R and X. Start with `k_c` = 2.5 (≈ 10.5 Gvar).
   - Why: each of the 34 equivalent lines aggregates many lightly loaded parallel circuits, whose
     charging adds while their flows divide.
   - Cost: 0 nodes.
   - Record `k_c` and the resulting Gvar in `data\parameters.md`.
2. **Load reactive demand to the report's state.** QO → 0, then slightly capacitive if needed (QO < 0
   on part of the loads, representing distribution cables and PV). P stays at 25.2 GW. Session 20's
   run `ib4q0` (QO = 0, 3 s) is the first data point: see RUNLOG S20.
3. **Light line flows.** Re-dispatch the machines and the France import/export so that the 400 kV
   lines run well below SIL (≈ 500–600 MW per circuit at 400 kV). Generation near load.
4. **Evacuation-transformer taps.** Set the collector-side taps so the plant side sits 3–6 % above the
   400 kV side. This reproduces the report's event-3 condition (220 kV side 1.061 pu with 417.9 kV on
   the 400 kV side, p.122).
5. **Shunt reactors (B6, `var_impedance`, 0 nodes) as the counterweight.** With levers 1–3 the
   profile should overshoot 420 kV. Insert reactors at the southern buses until 410–420 kV holds, with
   ≈ 1.3 Gvar connected of ≈ 2.7–3 Gvar installed (Fig 4-2).
6. Machine `V0` (the AVR set-point, D19b-2): trim only.

**Gate G4a ("the grid is capacitive"):**

- Collector buses 1.00–1.06 pu and 400 kV buses 400–420 kV, with the plants absorbing at fixed PF (D4).
- Machines below 60 % of their AVR ceiling.
- **Sensitivity sign check:** blocking one plant (Force) at t = 2 s *raises* its bus voltage, and
  inserting one 150 Mvar reactor lowers it by 3–4 kV (PLAN_OLD G4).
- All of this in one stacked run of ≤ 6 s (§2b).

Then the original G4 numbers (Carmona 410 ± 4 kV, export, RES absorption ≈ 2,300 Mvar, inertia).

Unchanged from PLAN_OLD.md C row 4, plus these specifics measured in S17:

- Bus 33 is at 0.92 pu with the plants absorbing at fixed PF. The report's south sat at 410–420 kV.
  The levers, in order: (1) machine Q set-points / `VREF` of the 4 units; (2) taps of the
  generator step-up transformers at the collector buses; (3) shunt reactor state (B6, needs
  `var_impedance` — `Variable` R/L/C, 0 nodes expected; verify on a bench, this is the open T7
  item). **Never** change plant `Kpf` to fix voltage: fixed PF absorbing is the root cause under study.
- Re-take the snapshot after every accepted change (P10).
- The ≈ 0.6 Hz inter-machine mode seen in S17 must be damped (≥ 5 % damping ratio) in the final
  snapshot, or explained, before Stage 6. It is also the starting point for Scenario O.

### WP6 — Module features still missing (needed by Stage 7 and Part D)

Add to `build_resplant.py`, one at a time, each proven on the `rp1` bench with its own small gate:

| feature | used by | bench check |
| --- | --- | --- |
| current limit 1.1 pu on `id_ref`, with `iq_ref` priority options | all cases | ramp Pref to 1.3 pu: id stays at 1.1 |
| `RampLim` (rate limiter on Pref) | M2 | ramp 0 → 1 pu in 1 s with RampLim 0.2 pu/s: takes 5 s |
| sub-block staging (`Nsub`, shares, per-block Vt/Tt; P/Q/limit scaled by untripped share) | cluster plants, Case B | 3 blocks with Vt 1.05/1.08/1.10: P steps down by the right shares |
| relay measured on the LV side vs POI (`meas_side`) | Granada event 3, M7 | needs the evacuation transformer (WP5) |
| `Qmode = 1` Q(V) droop | M1 | ±5 % V step: Q follows the droop within 2 % |
| `Qmode = 2` grid-forming | M11 | design item — write a separate mini-plan before building |
| `POD` | M15, Stage 10 | — |

### Stages 5–10

As in PLAN_OLD.md Part C, with the rules of §2. Two additions:

- The `Defence`/`Sequencer`/`TieProt` modules are pure signal modules. Generate them with a script
  like the plant (rule B1) and unit-test each relay with a `signalgen` ramp on a bench (as S16/S17
  did for the plant relay).
- **Definite-time relays:** use `master:delay` (on-delay, resets at once) followed by the latch pattern
  in `RES_Plant`. Do not use `realpole` timers (S16 trap 2).

---

## 4. Decisions taken in Session 17 (the user may overrule any of them)

| # | Decision | Alternatives considered |
| --- | --- | --- |
| D1 | C_f inside each plant module, scaled with Sbase (PLAN_OLD B3 said one C_f per bus) | per-bus C_f (needs per-bus sizing as plants trip; no node difference) |
| D2 | Keep the shared DC rail despite the inter-plant common-mode current | separate rails (5 nodes/plant, does not fit); same carrier for all (harmonics add coherently); DC choke per plant (+1 node each, 207 nodes) |
| D3 | Staggered carrier phases | identical carriers (0 circulating current, 2.25 % vs 1.47 % grid THD) |
| D4 | `Kpf < 0` (absorbing), sign fixed by measurement | — (the plan requires absorption) |
| D5 | Temporary bulk-33 plant to keep the operating point through Stage 3 | Granada alone (2.3 GW hole at bus 33) |
| D6 | Droop governor from control blocks instead of `hy_gov`/`hy_tur` | PSCAD's hydro pair (failed initialisation in S2–S5) |
| D7 | Snubber losses (≈ 120 MW/plant on the ideal DC side) left as is | smaller `CD` (changes the proven bridge for a DC-side-only effect) |
| D8 | Governor Kgov scaled to an assumed real rating (P_rated), not to the inertia-inflated Sbase; France 20 GW/Hz | 5 % droop on Sbase (≈ 5 GW/Hz from one Iberian unit, unphysical) |
| D9 | `Vctl` replaced by exposed AVR gains `KA`/`KF`/`TF` | a 0/1 switch with `select` blocks (more wiring, less flexible for M6 sweeps) |
| D10 (S20) | The baseline stays fixed-PF absorbing (D4). The collapse of S19 is fixed by giving the *grid* the report's reactive surplus (WP5 levers 1–5), not by changing the plants | executor's D19b-4(a) Q(V) droop baseline (removes the studied mechanism; it is mitigation M1); condensers/STATCOMs in the baseline (M4/M5); accepting 0.45 pu |
| D11 (S20) | Line charging scaled by `k_c` to Spanish scale (≈ 10–12 Gvar), R and X kept | longer lines (changes X and angles, breaks the G1 flows); extra shunt capacitors at buses (same effect but not physical) |
| D12 (S20) | Accelerated testing (§2b) replaces 20 s/120 s gate runs | — (user instruction) |

---

## 5. Measured traps you will meet (rules 1–19; full evidence in RUNLOG)

| # | Trap | Where |
| --- | --- | --- |
| 1–4 | Module parameters: `content_type="Constant"`, publish each with `master:import`, unique definition `id`, `<form><category>` without a `<categories>` wrapper | PLAN_OLD F3c |
| 5–8 | `xnode` per electrical port; `const.Value` is literal; Integer params need integer bounds; an `import` port sits 2 grid units right of its placement point | PLAN_OLD F3d |
| 9–12 | dq plant is a rotation (decouple); filter the voltage feedforward; `source1` `R1p`/`L1p` are shunt | PLAN_OLD F3e |
| 13 | Instance ports come from `<graphics>` `Port` elements (mode 1 in / 2 out / 3 electrical; datatype 3 Real) | S17 |
| 14 | Electrical labels are `master:nodelabel`; signal labels `master:datalabel` | S17 |
| 15 | `inductor.L`, `capacitor.C`, `resistor.R`, `const.Value` cannot hold a parameter (Literal); use `rtcbranch` (Constant). Check `content_type` in `master.pslx` | S17 |
| 16 | `rtcbranch` `I` field = branch current output, 0 nodes | S17 |
| 17 | Ammeters **and multimeters** split a node (+3 nodes each, three-phase) | S17 |
| 18 | `source3`/`source1` `Type` defaults to purely resistive | S17 |
| 19 | `iq > 0` = injection; check P/Q sign against an independent meter | S17 |
| — | `signalgen` PULSE starts at Max; `P = 180` starts it at Min | S16, S17 |
| — | `pscad_create_node_label_pair` renames a reused label to `<name>_2` (breaks the connection). To connect a third point to an existing label, place a `nodelabel`/`datalabel` component with the exact `Name` | S17 |
| — | PSOUT channel paths of module instances are `Root/Main/<Defn>[n]/<chan>/0/1`; with one instance it is `Root/Main/<Defn>/<chan>/0/1` | S17 |

## 6. Open questions for the user (none blocking WP1–WP4)

1. D1–D9 above: confirm, or say which to revisit.
2. The 2–8 % G1 flow deviation is probably not "PI vs Bergeron". It is not re-opened because Stage 4
   re-dispatches. Confirm that is acceptable for the write-up.
3. Inter-plant common-mode current: is a plant transformer per *named* plant (3 nodes each,
   12 plants = 36 nodes) worth exploring later, if the node budget allows after WP2/WP3?
