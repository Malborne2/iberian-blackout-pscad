# Iberian blackout in PSCAD — plan v0.9 for the remaining work

**v0.9 (2026-11-17, Session 20):**

- WP5 rewritten: the grid must be made reactively *surplus*, as in the report.
- New §2b, accelerated testing (mandatory).
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

Every claim here is backed by a measured entry in `RUNLOG.md` Sessions 17–18, or is marked *design*.

Read in this order: §0 (one page), §1 status, §2 the rules, then only the work package you are on.
Do **not** read all of `RUNLOG.md` (150 KB): §5 below holds the parts of it you need.

---

## 0. The ten-line version

1. Tools: if `pscad_status` fails, read §2 rule T1 before anything else. The tool-loss problem had
   a concrete cause and is fixed.
2. The converter module is done and gate-proven: `stage3\build_resplant.py` generates
   `RES_Plant`. Never hand-edit it; change the generator and re-run it.
3. Two plants already run in the network (`C:\PSCAD_work\iberia4`, 20 s stable), and the
   synchronous units have droop governors (WP1 done, Session 18, G2c passed).
4. **Next: free the module pages (WP2)**. The model is at 44 of 64 and would hit the limit.
5. Then the remaining plants bus by bus (WP3), then HVDC (WP4), then Stage 4 (WP5).
6. One change → one build → one run → one number checked against an *independent* meter.
7. Every sign (P, Q, current direction) is checked against a second measurement. Never trust the
   dq formula alone.
8. A gate passes only with numbers **and** figures, both produced by one script from the run's own
   `.psout`.
9. Write the RUNLOG entry *before* the session ends, including unfinished work and its state.
10. When something takes more than **3 build/run cycles** without progress, stop and write down what
    was measured. Do not keep trying variants.

---

## 1. Status board (2026-11-17, Session 20 — Sessions 19/19b reviewed)

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

### 2b. Accelerated testing (user instruction, Session 20) — **mandatory**

Runs of 20 s and 120 s at 200–380 s of wall time per simulated second cost 1–13 h each. They are no
longer allowed except where stated.

- **A1. Default run length is 2–5 s; prefer accelerated testing (§2b).**
  - Use **0.1 s** for launch/output/channel smoke tests, or **0.5 s** when the check needs more waveform cycles. Verify the requested end time and a fresh PSOUT. These checks do not establish settled behaviour or a dynamic gate.
  - Choose the shortest duration in **2–5 s** that can capture the required dynamics and measurement window. Use up to **6 s** when justified; do not exceed 6 s by default. If the required behaviour has not occurred or settled, leave the gate open.
  - Run longer than 6 s only for final checks or when the applicable work package explicitly requires it. The restrictions below still apply to runs of 20 s or longer.
  - The plants ramp in 0.6 s and the machines release at 0.5 s, so the electrical state is settled by ≈ 2 s.
  - A gate is read on the last 0.5 s of a run that has visibly flattened (print the slope).
  - **20 s or longer only for:** the final timed event cases (Stages 6–7), and at most one confirmation run per stage of a slow mode (e.g. the ≈ 14 s governor mode), and only after the short runs pass.
- **A2. Slow dynamics are tested scaled, not waited for.** Example: the HVDC 50 s AC-emulation lag is verified with `Tang = 0.5 s` (63 % at 0.5 s after a step) in a 3 s run. The time constant is a linear parameter, so the 50 s value is then set without re-testing. The same applies to governor or ramp time constants.
- **A3. Stack scenarios in one run.** Apply the cases one after another, 1–2 s apart, once the previous one has reached steady state:
  - examples: a load step, then a reactor insertion, then a plant force-trip;
  - use `signalgen`/`compare`-on-time steps, never `time-sig` + `upramp` for steps (they caused W19b-4);
  - read each case on its own window.
- **A4. Benches before networks.** Anything that can be shown on a < 20-node bench (≈ 5 s wall per simulated s) is not shown in the 18-plant network (≈ 300 s/s).
- **A5. Fewer channels for the network runs.** Use `sample_step` ≥ 100 µs unless harmonics are the question.

Ask the user only for: a decision that changes a documented user decision (PLAN_OLD.md header table),
a missing licence/tool, or a GUI-only step. Everything else, decide yourself and record the
alternatives in the RUNLOG.

---

## 3. Work packages (do them in this order)

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
