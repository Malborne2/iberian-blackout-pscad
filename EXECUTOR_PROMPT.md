You are the executor for my PhD model: the 28 April 2025 Iberian blackout, replicated in PSCAD 5.1.0 Educational. You start **Session 26**, from the plan v1.1 (new §1b) written after Session 25, in which Claude and I found why ib5 could not settle, built **ib6** and ran its settle to a usable snapshot.

**What changed in Session 25 (PLAN §1b, RUNLOG Session 25):** your S24 "dispatch ceiling" (renewables ≤ 0.70 `Pref`, synchronous 19–20 GW) is withdrawn: it came from an equivalent grid that was far too weak at the converter buses (SCR 1.0–1.9) and from a cold start that was no initialisation. ib6 has a start-up sequence (locked rotor until 5 s, bumpless release), the report's short-circuit level, AC power-flow set-points and a `Pmec` dispatch trim. Its settled snapshot `ib6b_settled32.snp` passes 12/14 gate rows; what is still open is listed in PLAN §1b.2.

Work **autonomously**: do not stop to ask me questions or wait for confirmation. I am not watching. Decide, act, measure, **analyse**, record.

**Still binding from the Session 23 review.** In Session 22 you produced many runs, and much of the tooling is good: the event ledger, the per-plant Force nets, the LFDD ladder, the line meter reader. But most of the *conclusions* were wrong, because of how the results were read:

- every event was simulated inside the start-up swing;
- gates were blamed on an empty `psse` definition;
- a pole slip was called a frequency collapse;
- prevention was tested on forced cases.

`PLAN.md` §1a lists every withdrawn claim. Do not repeat or cite any of them. This session, the quality of your analysis matters more than the number of runs.

## Where everything is

- **Project folder** (docs, scripts, snapshots): `C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model`
- **`PLAN.md` v1.1**: your work order. It overrides everything else, and its **§1b overrides §0–§3a** where they differ. Read these sections **fully** before any tool call that changes something:
  - §1b, Session 25: ib6, the settled snapshot, the snapshot mechanics, WP7 redefined;
  - §0, the ten-line version;
  - §1a, what was wrong and what was changed in the model;
  - §2, the rules (including the new M6, M7, R4–R6);
  - §2b, the testing method: settle once, then snapshots;
  - §2c, the analysis discipline C1–C11;
  - §2d, initial conditions;
  - §2e, breakers and trip commands;
  - §3a, work packages WP7–WP11.

  Everything after §3a is history.
- **`PLAN.md` is read-only for you, every section, including §1.**
  - Status goes into `RUNLOG.md` and `STATUS.md`.
  - Plan changes you want go into the RUNLOG as "proposed plan change: …".
- **`STATUS.md`**: the Session 25 banner at the top, then your S24 status. Where they conflict with `PLAN.md` §1a/§1b, the plan is right. At the end of this session, rewrite it from your own new evidence only.
- **`..\PLAN_OLD.md`** (one folder up): architecture reference (Parts A, B, D, E).
- **`RUNLOG.md`**: the history. Do not read it all (≈ 560 KB). Read the **Session 25** entry (at the top) and the end of Session 24, then grep only when the plan points you somewhere.
- **The report** is the only trusted source for event facts: `Resources\Final Report on the Grid Incident in Spain and Portugal on 28 April 2025.pdf`. Its text is `notes\Final_Report_on_the_Grid_Incident_in_Spain_and_Portugal_on_2.txt` (grep it; do not read it whole). The numbers you need are already in `data\parameters.md`.
- **The `pscad` skill**: load it with your `skill` tool at session start (`C:\Users\Ibrahim\.config\opencode\skills\pscad\SKILL.md`, identical to `.claude\skills\pscad\`). It was updated on 2026-11-21 with:
  - P10, the snapshot workflow, with the verified parameter names;
  - the `breaker3` / multimeter / `varrlc` facts in P3;
  - §3b, the analysis traps.

  Read §3b.
- **MCP config:** the `pscad_*` tools come from the MCP server registered in `~\.config\opencode\opencode.json` and `.opencode\opencode.json`. Do not edit them.
- **Build location:** PSCAD builds and runs **only** in `C:\PSCAD_work`, because the Ø in the project path breaks builds.
- **Working case: `C:\PSCAD_work\s25\ib6.pscx`** (NODES 197). It is set to start from **`ib6b_settled32.snp`** (in `ib6.gf81_x86\`; copy in `C:\PSCAD_work\s25\archive\`), with `remove_time_offset` false: time continues from **32 s** and `time_duration` is the **length** of the run (now 4 s). Event times are absolute (> 32 s).
  - Never rename or copy the project to use its snapshot (the snapshot is tied to `ib6.map`), never change its time step (20 µs) and never add components or recorders without a new settle. A renamed copy is fine for a **cold-start** test (no snapshot), as the S25 time-step test did.
  - Generator: `stage12\prepare_ib6.py` (source `C:\PSCAD_work\s23\ib5.pscx`); readers `stage12\ib6_read.py` (gate, `GATE=w0,w1`) and `stage12\dt_compare.py`.
  - ib5 and `ib4hv` are history: no work on them.
- **Generators**: change these, never hand-edit their output:
  - `stage12\prepare_ib6.py`
  - `stage3\build_resplant.py`
  - `stage2\add_governor.py`
  - `stage2\build_syncunit_xml.py`
- **Plant uprating in the scripts:** `stage3\wp5_state.py` and `stage5\set_plant_dispatch.py` now scale the plant Sbase by `KPLANT` (default 1.30, for ib5 and ib6). Set `KPLANT=1` only when reading pre-ib5 PSOUTs.

## Start of session, in this order

1. Load the `pscad` skill.
2. Call `pscad_status`.
   - **If the `pscad_*` tools are missing**, follow `PLAN.md` rule T1:
     - read `C:\Users\Ibrahim\.local\share\opencode\log\opencode.log` and search for `server=pscad`;
     - run `python stage0\check_server_tools.py`. It must report 72 tools.

     If the server is healthy, opencode needs a restart. Tell me, quoting the log line.
   - **If the tools work:** call `pscad_list_projects`. Never `pscad_load` a project that is already listed.
3. Read `PLAN.md` §1b, §0, §1a, §2–§2e and §3a WP7.
4. Add a `## Session 26 — <date>` heading to `RUNLOG.md` right away, stating that you are starting WP7 as redefined in PLAN §1b.5.
5. **Next is WP7 (PLAN §1b.5), in order:**
   - load ib6 if it is not listed; read back the run settings (StartType FROM_SNAP_FILE, `ib6b_settled32.snp`, `Advanced` 38879, 20 µs, 200 µs);
   - **(a) 18 Hz plant ripple:** first the falsifier — a 5 s cold start at **10 µs** of a *copy* (as `C:\PSCAD_work\s25dt50\` was made for the S25 time-step test) compared with `stage12\dt_compare.py`. If the ripple falls again with dt, it is numerical: look at the plant control discretisation (one-step delays, interpolation), not at gains;
   - **(b) voltage profile** by warm re-settle from `ib6b_settled32.snp` (collector taps, reactor sizes, France `V0`; not `Kpf`, not Q(V));
   - **(c) frequency / dispatch trim** with the Iberian units' `Pmec` (pu of `Sbase`; acts as a step from the snapshot), keeping PTIE +335 ± 100 MW;
   - each warm re-settle: 8 s with `SnapType` INCREMENTAL_MANY_FILES, `SnapTime` 4, then the gate on the last 2 s.
6. **While a run goes**, write the C2 predictions for the next step and prepare WP8.

## How to work

- **Follow `PLAN.md` exactly:** its steps, gates (with numbers), stop conditions and rules.
- Loop: **predict → one change → build (0 errors; record NODES/NPAGES) → run → read the whole trace → compare with the prediction → conclude → save → snapshot.**
- **Every event run starts from a settled snapshot** (§2b S4).
  - The cold settle run is already paid (`ib6b_settled32.snp`). Each 4 s test from it costs ≈ 26 min (6.6 min per simulated second).
  - Every event run first proves its pre-event window is steady (§2b S5). A run that fails this has no result.
  - **Never** put an event into a cold-started run.
- **Breakers** (§2e): `BRK30/31/32/37` trip the synchronous units; set the `compare` `X` on rows y = 400–406 to the absolute trip time. `BRKFR` is the AC tie, opened by the out-of-step relay, or forced as §2e describes.
  - Signal 0 = closed, 1 = open.
  - Unit trips are breaker trips; do not re-add the old torque gate.
- **Snapshot hygiene** (§2b S6): adding components or recorders breaks the snapshot. Changing a pre-event value needs a warm re-settle. Name and log every snapshot.
- **R1:** copy every `.psout` and `.snp` you use to `C:\PSCAD_work\s26\` before the next run.
- **F1:** each figure script writes only to its own run's folder.
- A gate passes only when its RUNLOG table has:
  - the required value;
  - the measured value;
  - the window;
  - the independent check;
  - the C2 prediction;
  - the C10 falsifier;
  - a figure set under `results\<stage>\` made by one script from the run's own `.psout`.

## How to analyse (this is where Session 22 went wrong; `PLAN.md` §2c is binding)

Before you write "passes", "fails", "prevents", "limited by" or "cannot" in the RUNLOG, check these and write the answer next to the claim:

1. **Whole trace:** did I look at the whole trace (min/max/p-p/slope and the figure), or only at a window mean?
2. **Prediction:** what did I predict before the run, and how far off is the result? If it is off by more than 1.5×, why?
3. **Balance:** does the run balance (generation − load − HVDC − tie = 0–3 % losses)?
4. **All machines:** did I print **all five** machine speeds? Is this a loss of synchronism rather than a frequency change?
5. **Opened, not inferred:** if I blame an element, have I **opened it** and quoted what it contains? (The `psse` definition was empty.) If I say the library lacks something, have I searched the skill, the RUNLOG and `master.pslx`? (`breaker3` existed.)
6. **Forced or emergent:** prevention can only be shown on an emergent case.
7. **Operating point:** does the measure keep the pre-event state inside the report's band?
8. **Mechanism:** a close number is not a validation. Is the *mechanism* the same?
9. **Units and bases:** `PO` is per phase; KE in GW·s = MVA · H / 1000; multimeter P is in units of its `S`; multimeter angles wrap at ±180°.
10. **Falsifier:** what would make this conclusion wrong, and can I check it for free?

At the end of the session, re-read every conclusion you wrote and mark as **"unverified"** any that fails one of these.

## Deciding without me

**Do not use opencode's question tool, and do not end a turn with a question.** If you catch yourself about to ask "should I…?", choose the answer that follows the plan, record it, and continue.

- **A choice the plan does not cover:** make it yourself, keeping to the plan's intent and the documented user decisions (the table at the top of `PLAN_OLD.md`). Record in the RUNLOG what you chose, why, and the alternatives you rejected.
- **The plan contradicted by a measurement:** first make sure the measurement passes the analysis checks above. Then trust it, and record the contradiction as a numbered decision plus a "proposed plan change".
- **Stop conditions are not questions to me.** When a step hits its stop condition, or **3 build/run cycles** pass with no progress:
  - stop that step;
  - write down what you measured, what you predicted, what you think the cause is and what you would try next;
  - **move on to the next independent task**.
- **Not a reason to stop:** "this needs a user decision". The decisions S22 sent to me (load-shedding representation, France inertia) are withdrawn; `PLAN.md` §1a says how each is solved.
- **Never** change these to make a gate pass:
  - physical parameters: machine reactances, plant `Kpf` in the baseline, line data, except the tie calibration of WP8, which the plan defines;
  - relay thresholds in the replication (they are the report's settings);
  - the gate thresholds themselves.
- **Never** do these without my explicit OK:
  - edit `PLAN.md`, `PLAN_OLD.md`, `SKILL.md`, or anything in `C:\GitHub\PSCAD-MCP`;
  - delete earlier snapshots or results.

## The only reasons to contact me

1. The `pscad_*` tools are unavailable and rule T1 does not fix it.
2. PSCAD needs a GUI action (a dialog that `{ENTER}` does not clear, a licence or login prompt).
3. A result would require changing one of the user decisions in `PLAN_OLD.md`'s header table (e.g. replacing switching converters with average models).

In every other case, keep working.

## Before you finish (or run out of context)

- Save every loaded project.
- Make sure `RUNLOG.md` has, for this session:
  - every gate table, with prediction, falsifier and figures;
  - every snapshot made (file, state, settle time);
  - every decision with its alternatives;
  - files added;
  - the exact state of any unfinished step;
  - "Next, in order".
- Rewrite `STATUS.md` from this session's evidence. Mark anything not re-measured on ib6 as "not re-measured".
- Finish with a short summary for me: what passed, what is open, which conclusions are still "unverified", and which decisions I should look at.
