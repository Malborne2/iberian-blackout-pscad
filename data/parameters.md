# data/parameters.md — every number that enters the model, with its report page

Source: `Resources\Final Report on the Grid Incident in Spain and Portugal on 28 April 2025.pdf`
(ENTSO-E Expert Panel, 20 March 2026). Page numbers are **PDF page numbers** (the printed page
number matches the PDF page number in this file).

Verification tags:

| tag | meaning |
| --- | --- |
| **[S]** | read in the final report this session (quote or sum reproduced) |
| **[P]** | page reference taken from `PLAN.md`; not re-read this session |
| **[T]** | digitised from a report figure this session — `data/targets_*.csv` |
| **[C]** | computed from the values above, formula shown |

**No number may be taken from the other PDFs in `Resources\`.**

---

## 0. Generator-bus operating point (Stage 1 output, Stage 2 input)

Read from the ten `source3` components of `iberia1_stage1.pscx` at the end of Stage 1. These are the
V∠θ, P, Q that each `SyncUnit` must start from (PLAN B4 / F2).

| gen | Vm (kV) | V (pu) | angle (°) | P (pu) | Q (pu) |
| --- | --- | --- | --- | --- | --- |
| 1 | 400 | 1.000 | −3.73 | 2.50 | 0.83 |
| 2 | 400 | 1.000 | −1.59 | 5.71 | 3.64 |
| 3 | 400 | 1.000 | +1.79 | 6.50 | 0.01 |
| 4 | 400 | 1.000 | +2.87 | 6.32 | 0.70 |
| 5 | 400 | 1.000 | +1.46 | 5.08 | 1.49 |
| 6 | 400 | 1.000 | +4.78 | 6.50 | 1.67 |
| 7 | 400 | 1.000 | +7.46 | 5.60 | 0.75 |
| 8 | 400 | 1.000 | +2.05 | 5.40 | −0.35 |
| 9 | 400 | 1.000 | +7.30 | 8.30 | −0.01 |
| 10 | 400 | 1.000 | −10.06 | 10.00 | −0.36 |

P and Q are per unit on the 410.4 MVA source base. Sum P = 61.25 pu ≈ 25,137 MW (matches the metered
flow total, PLAN Stage 1).

**Flag for Stage 2:** `source3` stores `Exph = RADIANS`, but the angle values are in the range
−10 … +7.5, which is degrees. Either the flag is not applied or PSCAD converts on write. Before those
angles are typed into a `SyncUnit` initial condition, confirm with one bench test which unit the
machine actually takes — do not assume.

## 1. System scale (Stage 1, Stage 4)### 1.1 Generation by technology at 12:32, Spain

Fig 1-4 (p.11) gives three regions; the Spain totals are their sums **[S, C]**:

| Technology | Region A | Region B | Region C | Spain total | Model element |
| --- | --- | --- | --- | --- | --- |
| Solar PV | 2,420 | 1,260 | 12,860 | **16,540** | the 18 `RES_Plant` converters |
| Wind | 710 | 110 | 2,810 | **3,630** | folded into the converters |
| Solar thermal | 70 | — | 1,420 | **1,490** | part of B1 "6,180" |
| Cogeneration | 400 | 520 | 280 | **1,200** | part of B1 "6,180" |
| Thermal RES + small hydro | 2,640 | 480 | 370 | **3,490** | part of B1 "6,180" |
| Nuclear | — | 2,740 | 660 | **3,400** | sync units 31, 32 |
| Combined cycle | 340 | 330 | 320 | **990** | sync units 30, 37 |
| Coal | 230 | — | — | **230** | sync units 30, 37 |
| Hydro | 290 | — | — | **290** | sync units 30, 37 |
| Pump storage (generating) | 860 | — | — | **860** | sync units 30, 37 |
| Region "Total production" | 6,170 | 4,330 | 18,720 | 29,220 | — |
| Region demand | 9,030 | 7,950 | 8,260 | **25,240** | ≈ 25.2 GW Spanish demand |

`B1`'s "6,180" = 1,490 + 1,200 + 3,490 **[C]**. Earlier plan text put 1,490+1,200+3,490 = 6,180 **[C]**.

### 1.2 Demand, pumping and inertia

| Quantity | Value | Page |
| --- | --- | --- |
| Spanish demand at 12:30:00 (closest estimate to LFDD) | 29,631 MW | p.200 **[S]** |
| Pumping (consumption) before the incident, Spain | 3,031 MW | p.198 **[S]** |
| Pumping before the incident, Portugal | 2,098 MW | p.203 **[S]** |
| Total pumping connected | 5,129 MW | p.203 **[S]** |
| Kinetic energy, Iberian area | 119,474 MW·s | p.51 **[S]** |
| Kinetic energy, Spain | 97,590 MW·s | p.51 **[P]** |
| Inertia constant on system base | H ≈ 2.2–2.7 s | p.51 **[P]** |

> **Note for Stage 1:** 25,240 MW (Fig 1-4, 12:32) and 29,631 MW (p.200, 12:30) are different
> quantities in the report — the second is the demand estimate used for the LFDD percentage. Use
> 25,240 MW for the load-flow base case and record the difference; do not average them.

---

## 2. Reactive behaviour (Stage 3, Stage 4)

| Quantity | Value | Page / figure |
| --- | --- | --- |
| Renewable plants run at fixed power factor | cos φ = 0.985 inductive | p.17, p.298 **[P]** |
| Granada evacuation transformer reactive absorption at trip | 165 Mvar | p.126 **[P]** |
| Badajoz substation 1 absorption at trip | 165 Mvar | p.126 **[P]** |
| Badajoz substation 2 absorption at trip | 38 Mvar | p.126 **[P]** |
| South-Spain RES absorption before the event | ≈ 2,300 Mvar | Fig 4-2, p.216 **[P]** |
| Reactive absorption actually realised by conventional units in the south | ≈ 74 Mvar | p.216 **[P]** |
| Shunt reactor unit size | 150 Mvar | p.217, p.310 **[P]** |
| Shunt reactors installed, south Spain | 2,700–3,015 Mvar | p.216 **[P]** |
| Shunt reactors connected at 12:32 | ≈ 1,300 Mvar | p.216 **[P]** |

Sensitivity checks required by gate G4 (p.217 footnote 58) **[P]**: removing the 355 MW /
165 Mvar Granada plant raises Carmona by 3–7 kV; inserting one 150 Mvar reactor lowers the local
bus by 3–4 kV.

---

## 3. Voltage and protection (Stage 3, Stage 5, Stage 7)

| Quantity | Value | Page |
| --- | --- | --- |
| Granada 400/220 kV transformer, 220 kV side at 12:32:56 | 233.4 kV = 1.061 pu | p.122 **[S]** |
| Same instant, 400 kV side | 417.9 kV | p.122 **[S]** |
| Trip threshold and delay, measured on the 220 kV side | 1.10 pu, 0 s | p.122 **[P]** |
| Network voltage above 440 kV from | 12:33:16.68 | p.123 **[S]** |
| Maximum 400 kV voltage at 12:33:17 | 442.5 kV | p.123 **[S]** |
| Maximum 400 kV voltage at 12:33:18 | 451.4 kV | p.123 **[S]** |
| Required stay-connected capability | 1.10 pu (440 kV) for 60 min | p.141–142 **[P]** |
| Observed OV protection settings in the fleet | 1.089 pu/1.5 s; 1.10 pu/0 s; 1.10 pu/0.5 s; 1.111 pu; 1.139 pu/0.2 s; 1.15 pu/0.6 s | p.160–172 **[P]** |

---

## 4. HVDC Santa Llogaia–Baixas (Stage 3)

| Quantity | Value | Page |
| --- | --- | --- |
| Rating | 2 × 1,000 MW, in parallel with Vic–Baixas 400 kV | p.101 **[P]** |
| AC-emulation gain / time constant | K = 360 MW/°, T = 50 s | p.102 **[P]** |
| Reactive limits per link | +400 / −600 Mvar, P has priority | p.102 **[P]** |
| Mode change to constant power | 12:09, set-point raised to 1,000 MW | p.71 **[P]** |
| AC voltage set-point, Spanish end | 405 kV | p.136 **[P]** |
| Reactive output at 12:33:00 with 410 kV at its bus | 7.7 Mvar | p.136 **[S]** |
| POD-Q authority | ±100 Mvar per pole | p.69 **[P]** |
| POD-Q blocked itself | 12:03:51, after ≈ 50 s of saturation | p.69 **[P]** |
| Blocking time | 12:33:23.960 | p.120 **[S]** |

**Open question for Stage 3 (`B9`):** why the link delivered only 7.7 Mvar at 410 kV. PLAN requires
this to be answered from Fig 2-97 (p.103) and p.136 **before** the HVDC controller is built — do not
guess it.

---

## 5. Frequency, load shedding, pump shedding (Stage 5)

### 5.1 LFDD steps — Spain (p.200, Table 3-10) **[S]**

| Step | Threshold (Hz) | Load shed (MW) | Crossing time (CEST) | t_sim (s) |
| --- | --- | --- | --- | --- |
| 1 | 49.0 | 1,175.9 | 12:33:20.600 | 80.600 |
| 2 | 48.8 | 1,669.1 | 12:33:20.760 | 80.760 |
| 3 | 48.6 | 1,574.6 | 12:33:21.000 | 81.000 |
| 4 | 48.4 | 1,523.9 | 12:33:21.380 | 81.380 |
| 5 | 48.2 | 1,294.3 | 12:33:21.820 | 81.820 |
| 6 | 48.0 | 1,267.1 | 12:33:22.040 | 82.040 |
| **Total** | | **8,504.9** | | |

Extra: 71.03 MW disconnected at 48.7 Hz by two DSOs whose relays were not yet updated; the report
adds it to the 48.6 Hz step (p.200) **[S]**.

### 5.2 LFDD steps — Portugal (p.202, Table 3-13) **[S]**

| Step | Threshold (Hz) | Load shed (MW) |
| --- | --- | --- |
| 1 | 49.0 | 315 |
| 2 | 48.8 | 293 |
| 3 | 48.6 | 315 |
| 4 | 48.4 | 323 |
| 5 | 48.2 | 282 |
| 6 | 48.0 | 427 |
| **Total** | | **1,955** |

Portuguese electro-intensive industrial load at 49.2 Hz: 218 MW (p.201) **[S]**.

### 5.3 Pump shedding (p.198, p.203, Table 3-15) **[S]**

| System | Threshold (Hz) | MW |
| --- | --- | --- |
| ES | 49.5 | 2,168 |
| ES | 49.3 | 588 |
| PT | 49.8 | 381 |
| PT | 49.7 | 450 |
| PT | 49.6 | 438 |
| PT | 49.5 | 470 |
| PT | 49.4 | 0 |
| PT | 49.3 | 359 |
| **Total** | | **4,854** |

Spanish total 2,756 MW; Portuguese total 2,098 MW (p.203) **[S]**.

---

## 6. Event timeline (Stage 6, Stage 7)

`data/events.csv` — 173 rows, 95 clusters, transcribed from Table 3-1 (p.117–120). Verified this
session against the report's own totals; see `stage0/check_events.out.txt`.

| Check | CSV | Report | Page |
| --- | --- | --- | --- |
| Event 3 | 355.00 | 355.00 | p.117 |
| Events 4a+4b | 727.00 | 727.00 | p.117 |
| Event 5, seven trips | 928.00 | ≈928 | p.118 |
| Table 3-2 total generation | 7,609.27 | 7,609.3 | p.131 |
| Table 3-2 nuclear | 3,390.00 | 3,390.0 | p.131 |
| Table 3-2 combined cycle | 719.00 | 719.0 | p.131 |
| Table 3-2 PV | 3,198.07 | 3,198.1 | p.131 |
| Table 3-2 pumped hydro | −2,756.00 | −2,756.0 | p.131, p.203 |

**Unresolved:** the Table 3-2 `Load` row (−8,504.3 MW) cannot be reproduced from the demand rows in
`events.csv` (ES rows 1,473.53; `IP` rows 8,635.58). Use **Table 3-10 above** as the load-shedding
source until this is settled. Recorded in `RUNLOG.md` §3.

Key instants used by the gates **[S]**:

| t_sim (s) | Clock | Fact | Page |
| --- | --- | --- | --- |
| 57.220 | 12:32:57.220 | first cascade trip (event 3) | p.117 |
| 76.443 | 12:33:16.443 | event 4a | p.117 |
| 76.680 | 12:33:16.680 | 400 kV network exceeds 440 kV | p.123 |
| 77.780 | 12:33:17.780 | 550 MW trip (event 5a2) | p.118 |
| 79.620 | 12:33:19.620 | loss of synchronism | p.130 |
| 81.407 | 12:33:21.407 | France–Spain AC ties open | p.119 |
| 82.702 | 12:33:22.702 | first nuclear trip (1,045 MW) | p.120 |
| 83.960 | 12:33:23.960 | HVDC blocks | p.120 |
| ≈87 | 12:33:27 | blackout | p.128 |

---

## 7. Digitised targets (Stage 6, Stage 7, Stage 8)

Produced this session by `stage0/fig1_10.py` and `stage0/digitise_targets.py`. Axis calibration
comes from the PDF text layer; the 360 kV reference line in Fig 1-10 reads back as 360.4 kV.

| File | Figure | Page | Columns | Range |
| --- | --- | --- | --- | --- |
| `targets_fig1-10.csv` | 1-10 | 16 | t, V Carmona, f Iberia, f CE | t 50.2–94.9 s |
| `targets_fig3-5.csv` | 3-5 | 127 | t, ES exchange MW, V Carmona | t −3.7–63.8 s |
| `targets_fig3-7a.csv` | 3-7 (panel a) | 129 | t, cumulative imbalance, 400 kV Vmax | t 0.9–79.6 s |
| `targets_fig3-7b.csv` | 3-7 (panel b) | 129 | same, cascade detail | t 70.0–83.5 s |
| `targets_fig4-89.csv` | 4-89 | 299 | t, f La Cereal (sim, PMU) | t 76.0–82.8 s |
| `targets_fig4-90.csv` | 4-90 | 299 | t, V La Cereal pu (sim, PMU) | t 76.0–82.8 s |
| `targets_fig4-91.csv` | 4-91 | 300 | t, Spain–France P (sim, PMU) | t 76.0–82.8 s |

Values read at the gates **[T]**:

| Quantity | Value | Source |
| --- | --- | --- |
| Carmona at 12:32:00 | 409.1 kV | Fig 3-5 |
| Carmona at 12:32:57 | 421.8 kV | Fig 3-5 |
| Exchange ES at 12:32:00 | 4,185 MW export | Fig 3-5 |
| Exchange ES at 12:32:57 | 3,240 MW export | Fig 3-5 |
| Carmona peak | 463.7 kV at ≈12:33:29 | Fig 1-10 |
| Iberian frequency | 47.4 Hz floor, 49.99 Hz start | Fig 1-10 |
| CE frequency | 49.85 Hz minimum | Fig 1-10 |
| Cumulative imbalance at 12:33:17 / :18 / :19 / :20 | 1,651 / 2,522 / 3,565 / 4,959 MW | Fig 3-7b |
| Spain–France flow | −3,847 MW import (sim) / −3,566 (PMU) at ≈12:33:19.5; +5,609 / +4,308 at ≈12:33:20.5; settles at ≈+1,000 MW import after the ties open | Fig 4-91 |

**Known inconsistency between two report figures:** Fig 3-5 puts Carmona at **409 kV** at 12:32:00
rising to 422 kV at 12:32:57; Fig 1-10 puts it at **426 kV** at 12:32:50. The two differ by ≈4–5 kV
at the same clock time. Do not reconcile them silently — use Fig 3-5 for the pre-event operating
point (gate G4) and Fig 1-10 for the cascade shape, and say so in the write-up.

---

## 8. Architecture constants (Stage 1–3)

| Quantity | Value | Source |
| --- | --- | --- |
| Base frequency | 50 Hz | PLAN B1 |
| 400 kV network | all buses 400–420 kV pre-event | p.12 **[P]** |
| Converter carrier | 1,050–1,950 Hz, odd multiple of 50 | PLAN B3 (design choice) |
| Filter reactor | L_f ≈ 0.15 pu on plant base | PLAN B3 (design choice) |
| DC rail | ≥ 1.35 × peak line-to-line collector voltage | PLAN B3 (design choice) |
| Current limit | 1.1 pu | PLAN B3 (design choice) |
| Default power factor | 0.985 | p.17, p.298 **[P]** |
| Educational node limit | 200 | PSCAD help, not the report |
| Educational module limit | 64 | PSCAD help, not the report |

Rows marked "design choice" are **not** report numbers; they are stated so the write-up can separate
report-derived values from modelling assumptions.

---

## 9. Still to be sourced (do not guess)

1. HVDC reactive behaviour at 12:33:00 (7.7 Mvar at 410 kV) — read Fig 2-97, p.103 and p.136.
2. Carmona measurement point in the model (bus 16 or 21) — decide from the Stage-1 V∠θ solution.
3. Tie reactance for the loss-of-synchronism test (gate G5) — tuning knob, but the initial value
   should come from the 9–39 / 1–39 line data scaled to Iberia, not from trial and error.
4. Cluster→bus assignment of the 18 plants (PLAN B1 table) — modelling choice, must be recorded here
   before Stage 4.

---

## 10. WP5 operating point (Session 21, measured)

| Quantity | Value | Evidence |
| --- | --- | --- |
| Line charging scale `k_c` | **2.5** (sum Cp1 84.45 -> 211.12 uF) | S20 §7, D11; charging **10,612 Mvar** at 400 kV |
| Load reactive demand `QO` | **0** on all 19 loads (P stays 25,238 MW) | S20 §4, lever 2 |
| Collector taps (bus 33/34/35/36/38) | **1.0352 / 0.9510 / 1.0486 / 0.9531 / 1.1905** | S21 §7, `stage5\tap_trim.py`, from run 4 |
| AVR gain `KA` (all five units) | **40** (was 400); KF 0.03, TF 1 s unchanged | S21 §7: 0.5 Hz mode zeta 2.7 % at KA 80 -> 6.6 % at KA 40 |
| Plant relay, parked | `Vt` 1.5, `Tt` 0.05 | S21 §3 (D21-2) |
| Shunt reactor (bus 9, survey) | 600 Mvar constant-Q equivalent (`fixed_load` PO 0 / QO 200 per phase) | S21 §10 (D21-7) |
| Collector voltages reached | 1.046-1.064 pu at all five buses | run 5, window 5-6 s |
| 400 kV reached (bus 30/31/37/39/9) | 439.9 / 449.1 / 427.8 / 412.5 / 446.1 kV | run 5 - **open, needs reactors** |
| Machine net Q | -8.3 Gvar (absorbing -> grid reactively surplus) | run 5 |
