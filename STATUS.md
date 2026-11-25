# Work claims (see AGENTS.md §3) — add a line before you start, remove it when done

| Agent | Working on | Files | Since |
|---|---|---|---|
| claude-main | v2 pre-event calibration (pandapower) | `iberia_eq/pp_v2.py`, `iberia_eq/SOURCES.md`, `iberia_eq/V2_BUS_UNIT_LIST.md` | 2026-11-25 |

# STATUS — Session 29 banner (25 Nov 2026; agent: claude-main)

- **Base v2 load flow ACCEPTED (S29 §10):** `python iberia_eq/base_v2.py` → `iberia_eq/pp_v2_state_s29_vk3.pkl`.
  - Network-derived corridor X (`reduce_fullnet.py`); Madrid at real demand; dispatch shifts ≤ 0.6 GW for the borders.
  - Voltages within 2.8 kV; borders and unit Q met; Fig 4-2 met.
  - TSO–DSO Q −1.29 Gvar (injecting, like Fig 4-84).
  - Trip checks met: max-V rise +5.05 kV (+4.9); Granada 25 kV/Gvar.
  - Fig 2-4 line flows are checks only (one bus per zone, S29 §9).
- **Pre-PSCAD review done (S29 §11): proceed.** PSCAD design changes:
  - A: two-layer unit voltage control, with a slow weak-droop outer Q loop (K ≈ 10–15 Mvar/kV per GW), so the drift
    emerges;
  - B: relay thresholds as offsets from the model's pre-event hub voltage;
  - C: France source X calibrated for the 4,609 MW AC peak.
- **Open:**
  - Spanish TSO–DSO Q +0.97 Gvar absorbing, but Fig 4-84 says the DSOs inject (−1.3 Gvar at 412 kV, 400 kV interface
    only). Suspected cause: the 3.2 % unit connection X from TRIPCAL. Next: remote voltage control (AVR line-drop
    compensation) in `fastpf`, then a PSCAD AVR bench.
  - PT tie Q +256 vs +100.
  - 4a+4b +7.0 vs +4.9 kV.
  - Fig 2-4 corridor checks; north/centre fault levels.

---

# STATUS — Session 28 banner (25 Nov 2026; agent: claude-mac; pandapower only, no PSCAD; merged in PR #1)

- **v2 load flow continued** (`RUNLOG.md` Session 28). The S27 state `iberia_eq/pp_v2_state.pkl` is unchanged.
  The new **candidate X6** is `iberia_eq/pp_v2_state_s28_X6.pkl`. It is not yet the default; that decision is open.
- **Fixed:** resume bug (Madrid knob read from the Morocco slot → 4 GW shift). `--route 1.0` is needed to reproduce
  s35b.
- **Corridor builder v2:** finds the missing **Vandellós–La Plana (CAT–VAL)** axis and extra circuits. Spanish
  400 kV circuit-km 18.4 → 21.4 thousand (REE ≈ 21.7). This cuts the fitted DSO capacitive injection
  −6.8 → −3.7 Gvar.
- **New gate `pp_v2_trip.py`** (static ΔV per trip):
  - s35b: 4a+4b **+12.8 kV** vs the report's 4.9, Granada 108 kV/Gvar vs 18–42;
  - X6 (unit connection X 5 %): **+7.1 kV**, **28 kV/Gvar ✓**, all border / unit-Q / Madrid targets met.
- **Later in S28:**
  - `fastpf.py` (own Newton on pandapower's Ybus, exact to 2e-16 pu) cuts a cold fit from 4–9 min to **40–60 s**.
  - The SVD showed the S27 objective was under-determined (2 null directions). `OBJ=2` fixes it (condition number 15).
  - The trip gate is now inside the fit (`TRIPCAL=1`).
  - **Portugal loop fixed** with `PT_TIE_SW=2.6`: North→PT **+200** (target +200).
  - **New candidate R2:** `pp_v2_state_s28_R2.pkl`.
- **Open:**
  - Spanish TSO–DSO Q +1.2 Gvar vs Fig 4-84's −1.0…−1.8;
  - Portuguese unit absorbs 1.3 Gvar;
  - 4a+4b +7.1 vs 4.9 kV (the tripped plants' Q is unknown);
  - Table 2-12 lines still open at 12:32 are not yet removed;
  - north/centre fault levels;
  - AVR line-drop compensation proposed instead of a few-% step-up.

---

# STATUS — Session 27 banner (23 Nov 2026, 14:05); the Session 26 status follows unchanged below

- **Executor:** Claude (from S27; `EXECUTOR_PROMPT.md` frozen). Work runs in parallel batches (PLAN v1.2 §1c/§3a),
  one PSCAD instance per run (`stage12\run_instance.py`, `make_variant.py`). Detail: `RUNLOG.md` Session 27.
- **Corrections to S26:** the "unit 32 runaway" was the tripped unit; the bus-36 transformer is reversed (tap 0.9385
  → 1.056); PSOUT plants 1 ↔ 18 were swapped (Granada = `RES_Plant[18]`).
- **G7a state for Batches 2–3:** `C:\PSCAD_work\s27\trim3\ib6e_03.snp` (t = 36 s), 13/14: f 49.992, PTIE +352,
  collectors 1.056–1.060. Only the 17 Hz ripple row fails (current-limit cause falsified). Open: Iberian units
  15.24 GW vs 11.95.
- **Batch 1 (`C:\PSCAD_work\s27b1`):** WP8.4 PASS; WP7.6 PASS per Gvar; r1 relay + LFDD/pump PASS, peak import
  6 % short (tie 83 → 76 Ω in Batch 2). **Case A** reproduces the report's sequence (`BRKFR` 0.58 s early).
  **Case B (Granada only) does not cascade** (min relay margin 0.020 pu). The report has no trip between event 3 and
  event 4a either, so **Case B2** forces events 3 + 4a + 4b and leaves the rest to the relays (`C:\PSCAD_work\s27b1b`,
  running with P1/P5/P6 and the parked control).
- **Trap:** machine parameters (H) are restored from the snapshot, so P7 needs a cold settle.
- **Batch-2 build `C:\PSCAD_work\s28`** (tie 76 Ω, load-bus meters, P2 reactors disabled): cold settle running.

---

# STATUS — rewritten from Session 26's own evidence only (23 Nov 2026, 02:20)

**This replaces the Session 25 banner and the S24 status below it.** Anything inherited from an earlier
session that Session 26 did not re-measure is marked **not re-measured**; anything `PLAN.md` §1a withdrew
is not repeated. Provenance: `RUNLOG.md` Session 26 §1–§12; archived PSOUTs/snapshots in
`C:\PSCAD_work\s26\`; figures in `results\stage26\*`.

---

## 1. Headline

**There is now a valid pre-event state on ib6, and the model's tie separates on its own out-of-step relay.**

- **Working case `C:\PSCAD_work\s25\ib6.pscx`** — collector taps trimmed, dispatch trim applied, trip
  compares back at "never", `StartType FROM_SNAP_FILE` → **`ib6b_settled80.snp`** (t = 80 s),
  `Advanced` 38879, 20 µs / 200 µs, `time_duration` 8 (length).
- **G7a state `ib6b_settled80.snp` (t = 80 s), gate 13/14:** f **49.9835 Hz** on all five machines,
  speed spread **0.1 mHz**, speed p-p **3.7–5.4 mHz**, collector drift −0.0003 pu/s, `PTIE` **+329**
  (p-p 28), HVDC **1,000**, no trips, no relay action. **Granada (bus 33) VDF 1.0604** (target 1.061);
  collectors 34/35/36/38 = 1.101 / 1.060 / 1.084 / 1.059; 400 kV units 413–420 kV; Iberian units
  **13.19 GW** (report 11.95), plants **19.24 GW** (report 18.155).
- **The one failing row is the 20 µs numerical 17 Hz ripple** (collector p-p 0.028–0.036 against
  0.005). At 10 µs its amplitude falls **5.2×**; the plan fixes 20 µs, so the row is declared
  **known-open** in every event gate (D26-1, D26-5).

## 2. What was measured this session

| item | result |
|---|---|
| **WP7(a) 18 Hz ripple** | a **marginally damped plant-control mode** at 17.0–18.7 Hz, **common-mode on all five collectors, in phase to 2.3°**, uniform 3.8–6.8 % of each plant's rating. Amplitude ∝ dt^2.4 (10/20/50/100 µs: 0.0013 / 0.0069 / 0.028 / 0.086 pu); frequency dt-independent. **Damping is numerical; the mode is real.** |
| **WP7(b) voltage profile** | collector transformer taps confirmed as the lever (`Main.f`: `RT_24…RT_30` → `TRTAP5` on 3 transformers each). Tap law **V ∝ 1/tap** reproduced to 0.2–0.3 % on buses 33, 35, 38; buses 34 and 36 moved less than predicted (cause **unverified**). |
| **WP7(c) dispatch** | Iberian units −434 MW / France +434 MW → `PTIE` **+769 → +350**, f moved **−1.8 mHz**. Both gates pass. |
| **WP8.1 unit breaker** | `BRK31` at 84.0 s: `PBK31` 3,375 → 0 MW within 0.2 s; Iberia dips to 49.67 Hz; `PTIE` to −3.9 GW; **no slip**; France holds 49.98. |
| **WP8.2 two-unit slip** | `BRK31` 84.0 + `BRK32` 84.5: peak import **−3,199 MW**; **`OOS1` and `BRKFR` both at 84.956 s with \|Δδ\| = 120.0°** — the relay opened the tie **on its own 120° threshold**. |
| **post-separation island** | **Not coherent**: unit 32 rises to 57.9 Hz while 37/30 fall to 40.6 Hz (spread 17.3 Hz). No single RoCoF applies. |
| **LFDD ladder** | Present but **inert**: `S1…S6` read a constant 10 from t = 0 (also in the steady pre-event window). Nothing switches a load with them. |
| **operations** | A **rebuild wipes the build folder including the `.snp`** — two 24-min runs were lost to silent cold starts before this was found. Rule: set parameters → build → **copy the `.snp` in** → run → check `ib6_1.config` for `-start-snap`. Wall cost **2.9 min per simulated second** at 20 µs. |

## 3. Open items, in priority order

1. **WP9 — DONE through step 2; the WP8.2 re-run is done.** The ladder is repaired and verified; **all
   six `varrlc` tranches are built** (labels only, no wires: 0 errors, NODES 197, PGBS 370), host `PO`
   reduced by `P_k/3`, **cold settle `ib6c_settle12.snp` (t = 12 s, gate 10/14)**, and the WP8.2 re-run
   proves the chain: `S1…S6` fire in order at 17.27–17.77 s and **every tranche current goes from
   1.80–2.81 kA to 0.0000 kA**. **New blocker found:** after the tie opens the Iberian island
   **pole-slips internally** (unit 32 → 58.6 Hz vs units 37/30 → 43.4 Hz) — LFDD cannot fix that, so
   G8a's "Iberia falls at the C2 RoCoF" clause is **not testable yet** (D26-9).
   **Next:** (i) re-trim the pre-event dispatch for the **+643 MW `PTIE`** offset with a warm re-settle
   (D26-8); (ii) measure the internal angle spread/transfer limits across the Iberian island to find why
   the four machines diverge; (iii) then WP10 on the emergent case, and WP11.
2. **WP8.2 re-run with the shed in place** — the island should hold, and G8a's RoCoF clause becomes
   testable. Then the tie calibration **on the angle trace** (X 90 → ≈ 83 Ω if the 3.6–3.9 GW target is
   kept; line data ⇒ cold settle).
3. **WP10** Case A / Case B from `ib6b_settled80.snp` (or its successor).
4. **WP11** prevention, on the emergent case only.
5. Optional: bench one `RES_Plant` at SCR ≈ 3 to identify the 18 Hz loop (candidates: the 8 ms `VDF`
   filter, the 1650 Hz carrier = 30.3 steps at 20 µs), then choose 10 µs vs a control fix.
6. Meter fault: **`V9` reads 0.003 pu** in every run — it does not measure the bus it is named for.
   No gate depends on it; needs a fix in a build that breaks the snapshot.
7. Units' reactive split: 32/37/30 absorb −2.45/−2.44/−2.19 Gvar but **31 injects +1.84** (cause not
   tested; `Q0`/AVR is the candidate — **not** a "network limit").

## 4. Withdrawn / corrected

- **Withdrawn (S24, restated in S25):** the "converter dispatch ceiling" (≤ 0.70 `Pref`, ≤ 0.89 pu,
  synchronous 19–20 GW) — a property of the too-weak ib5 equivalent.
- **Corrected this session:** the S25 `results\stage12\cont12_32\read.txt` **point** table (identical rows
  at 20/24/28/32 s) is void (pre-fix index); the S25 **gate** table is unaffected and was reproduced
  exactly.
- **Corrected:** the C2 RoCoF recipe — for the first ≈0.2 s after a trip, the **Iberian KE (119.5 GW·s)**
  is the right one (0.71 Hz/s predicted, 0.68–1.06 measured); the combined 5,119.5 GW·s form applies only
  after the tie responds.
- **Corrected:** §3a WP9's "LFDD ladder already built" — it exists but does not work.

## 5. State of the files

- **Case:** `C:\PSCAD_work\s25\ib6.pscx` (= `C:\PSCAD_work\s26\ib6_WP9_shed_final.pscx`), **NODES 197 /
  NPAGES 27 / PGBS 370 / STOR 10019, 0 errors** — ladder repaired, six `varrlc` tranches in place, host
  `PO` reduced, trip compares at 1e6, `StartType FROM_SNAP_FILE` → `ib6c_settle12.snp`.
- **Snapshots:** **`ib6c_settle12.snp` (t = 12 s) is the only valid one** (10/14; `PTIE` −308, D26-8).
  Everything earlier — `ib6b_settled80.snp`, `ib6b_trim68`, `ib6b_taps52`, `ib6b_settled32` — is
  **invalid** (components changed after them).
- **Readers:** `stage12\ib6_read.py` (gate + trace figure, L2 map + residual check),
  `stage12\wp8_breaker.py` (breakers/PBK/all speeds/RoCoF), `stage12\wp8_slip.py` (peak import, angle,
  coherence), `stage12\check_ladder.py`, `stage12\ripple_*`.
