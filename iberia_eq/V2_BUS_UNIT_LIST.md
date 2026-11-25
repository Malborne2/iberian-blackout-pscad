# Iberian equivalent v2 — bus and unit list (DRAFT 4, 2026-11-25: + substation buses BAD-TS, WAN-TS)

Draft 2 resolves the open items of Draft 1. Nothing is built yet.

**Tags:**
- **[FR]** ENTSO-E final report (page / table / figure).
- **[T3-1]** the full event table, parsed into `table3-1_events.csv` (173 rows; checked against Tables 3-9 and 3-15 below).
- **§n** a section of `SOURCES.md`.
- **[EXT-n]** an external source (listed in `SOURCES.md` §9).
- **[inf]** our inference, with the reason given.

## 0. Selection rule
Two pieces of equipment get separate models only if they differ in something that changes the event:
- electrical location;
- protection setting or trip time;
- control behaviour;
- the report giving them separately.

Otherwise they are merged.

**What is emergent and what is forced.** An event is emergent (produced by a relay or control in the model)
whenever the report gives its trigger: a voltage, a frequency, or a correlation with voltage. An event is forced
(time-scheduled) only when the report says its cause is unknown or lies outside the modelled system.

## 1. Buses (22)

| # | Bus | Covers | Why separate |
|---|---|---|---|
| 1 | GRA | Caparacena, Tajo Enc., Cártama, Archidona, Huéneja | events 3, 6a8; later waves 40, 43b (Fig 3-1 dark-blue area) |
| 2 | WAN | Guillena, Don Rodrigo, Arcos, Pinar del Rey, Tarifa, Huelva | 5a2, 5b2, 6a1, 6a6–7; waves 8a, 21; 12.3 GVA (Table 4-26); Morocco tie |
| 3 | BAD | Bienvenida, Brovales, Balboa, S.Serván, Carmonita | 4a, 4b, 5b1, 5b4, 6a2–3; waves 8b, 12b, 19, 32, 38b; 8.4 GVA; Portugal tie (Alqueva) |
| 4 | CAC | Almaraz, Arañuelo, J.M. Oriol, Cedillo | 5b3, 6a4; Almaraz II; Portugal tie (Falagueira) |
| 5 | SCE | Guadalquivir Medio, Cabra, Valdecaballeros, Brazatortas, Manzanares | transit corridor; 416–418 kV at 12:32 (Fig 2-4) |
| 6 | MAD | Morata, SS Reyes, Galapagar, Villaviciosa, Loeches, Trillo | load centre; receives ≈ 3.2 GW (§8b) |
| 7 | CYL | Segovia, Lastras, Mudarra, Tordesillas, Villarino, Aldeadávila | 5a1, 5a3; Duero hydro; Portugal tie (Lagoaça) |
| 8 | NW | Mesón, Cartelle, Soto, La Robla, Montearenas | coal / hydro; Portugal tie (Lindoso) |
| 9 | N | Aguayo, Herrera, Güeñes, Itxaso, Hernani, Vitoria | France west tie |
| 10 | ARA | Aragón, Magallón, Escatrón, Mequinenza | |
| 11 | CAT | Vic, Rubí, Sentmenat, Vandellós, Ascó | all Spanish east nuclear; France east AC + HVDC |
| 12 | VAL | La Eliana, Catadau, Cofrentes (off), Minglanilla, Olmedilla | 6b Cuenca; wave 12a |
| 13 | SE | Rocamora, Litoral, Romica, Pinilla, Tabernas | 6a5 Murcia |
| 13a | BAD-TS | 400 kV substation of the Badajoz trips (TS1/TS2/TS3-Badajoz) | behind ≈ 14 Ω (≈ 55 km equivalent) from BAD: fault level 8,395 MVA = Table 4-26 Bienvenida 8,386. Tripping plants R2/R3/R4/R7 and the BAD aggregate connect here; Fig 2-4 voltage target (412 kV) applies here (RUNLOG §32–33) |
| 13b | WAN-TS | 400 kV substation of the Sevilla / Cádiz trips | behind ≈ 6.8 Ω (≈ 27 km) from WAN: 12,212 MVA = Table 4-26 Guillena 12,271. R6, R9 and the WAN aggregate connect here |
| 14 | PS-CYL | pump station behind CYL | pump cluster 13a (Duero), Fig 3-1 |
| 15 | PS-ARA | pump station behind ARA | pump clusters 13b + 14 (Ebro), Fig 3-1 |
| 16 | PS-PT | pump station behind PT-N | Portuguese pump clusters 7a, 7b, 11, 27, 34 (northern Portugal), Fig 3-1 |
| 17 | PT-N | Portugal north / centre | ties to NW, CYL, CAC |
| 18 | PT-S | Portugal south | ties to BAD, WAN; Alqueva |
| 19 | FR | France equivalent | |
| 20 | MA | Morocco equivalent | |

## 2. Synchronous machines (20: 10 generators, 3 embedded, 7 pump motors)

### Generators (sized at their online rating; P at 12:32)

| # | Unit | Bus | P [MW] | Trip (forced, [T3-1]) | Source |
|---|---|---|---|---|---|
| G1 | Almaraz II | CAC | 653–680 | 41c, 12:33:23.515 | [EXT-5] CSN unit status (Almaraz I cold shutdown); [T3-1] 653 MW; Fig 3-1 Extremadura area |
| G2 | Catalonia nuclear A | CAT | 1,045 | 41a, 12:33:22.702 | [T3-1]; [EXT-5]: Ascó I/II and Vandellós II in service, Cofrentes and Trillo off |
| G3 | Catalonia nuclear B | CAT | 1,692 | 46, 12:33:23.590 | [T3-1]; sum 653 + 1,045 + 1,692 = 3,390 MW ([FR]); CSN unit sum 3,522 MWe (SOURCES §11) |
| G4 | North thermal (CCGT 340 + coal 230) | NW | 570 | 54 (CC 78/83/140, 12:33:24.2–24.8) | Fig 2-41 N; Fig 3-1 north area |
| G5 | North hydro | CYL | 290 | — | Fig 2-41 N hydro 290 / 1,100 |
| G6 | South-west CCGT | GRA | 320 | 41b 166 + 47 87 | Fig 2-41 SW CC 320 / 760; Fig 3-1 places 41b in the dark-blue Granada–Almería area [inf] |
| G7 | East CCGT | VAL | 330 | 12a 165 | Fig 2-41 E CC 330 / 820; Fig 3-1 black area [inf] |
| G8 | Portugal conventional | PT-N | ≈ 600 | 44, 48, 49, 53, 57–60 (hydro, CC) | Fig 2-19 [read]; [T3-1] |
| G9 | France | FR | as ib6 | — | Fig 4-91 tie calibration |
| G10 | Morocco | MA | 570–750 export from Spain | ties trip at 16a/16b, 12:33:20.229 and 20.473 | Fig 2-41, Fig 2-22; size [EXT] (O4 below) |

**Unit voltage control in two layers (S29 §11, change A).**
- **Fast:** AVR with ≈ 80 % line-drop compensation on the 15 % step-up, for the seconds-scale trip steps.
- **Slow:** outer Q loop (T ≈ 20 s [inf]) toward Q0 − K·P·ΔV(400 kV), with K ≈ 10–15 Mvar/kV per GW.
  - Report data point: Fig 4-2 → 4-3, ≈ 6.5.
  - Without it the 12:32 drift does not emerge (+1–3 kV vs the report's +13–15).

**Relay thresholds as offsets (S29 §11, change B):** threshold = V_model(12:32:00) + (V_trip − V_12:32:00 from the
report), because zone hubs are averages.

**France source (change C):** its impedance is calibrated in PSCAD for the 4,609 MW AC import at loss of synchronism
([CA] p.54; ≈ 38 Ω total; ties 15.9 Ω).

**Unit step-up and AVR (S29 §5, §10).**
- The accepted pre-event state uses a 3 % connection reactance for Spanish units G1–G7.
- Build each unit with a realistic step-up (≈ 15 % on rating) and an AVR with reactive line-drop compensation of
  ≈ 80 % of X_T, so the regulated point sees (1 − 0.8) × 15 % = 3 %.
- Bench it on the 2-bus case before the full build.

### Embedded synchronous generation (inertia-carrying, no voltage control: fixed power factor)

| # | Unit | Bus | P [MW] | Basis |
|---|---|---|---|---|
| E1 | North embedded | N | ≈ 3,040 | Fig 2-41 N: cogeneration 400 + thermal RES / small hydro 2,640 |
| E2 | South-west embedded | SCE [inf: centroid of the solar-thermal fleet] | ≈ 2,070 | Fig 2-41 SW: solar thermal 1,420 + cogeneration 280 + thermal RES / hydro 370 |
| E3 | East embedded | VAL | ≈ 1,070 | Fig 2-41 E: cogeneration 520 + thermal RES / hydro 480 + solar thermal 70 |

**Why (O3 resolved):** the report's kinetic energy is Σ H·S over all rotating generators, explicitly including
solar thermal and other synchronous renewables ([FR] p.50). The load contribution is what makes H a range.

### Pumps as synchronous motors — one `PumpUnit` + breaker per large stage (user decision 2026-11-24, RUNLOG §28)

Each large under-frequency stage is its own motor behind its own breaker, so a stage trip is a clean electrical step
and its inertia leaves with it. A torque step on a lumped motor gave a spurious ≈ 2 Hz rotor swing on the bench.
`PumpUnit` (`stage12/make_pumpunit.py`) is benched (lt6): pumping within 0.6 %, inertia within 5 MW, exact stage
timing.

| # | Unit | Bus | MW | Trip (emergent; f below threshold for 0.15 s) | Basis |
|---|---|---|---|---|---|
| M1 | Duero pumps | PS-CYL | 1,049 | 49.5 Hz | [T3-1] 13a (10 units, 12:33:20.13–20.51) |
| M2 | Ebro pumps | PS-ARA | 1,017 | 49.5 Hz | [T3-1] 13b less its 78 MW unit at 20.480 |
| M3 | Portugal step 1 | PS-PT | 381 | 49.8 Hz | Table 3-15 |
| M4 | Portugal step 2 | PS-PT | 450 | 49.7 Hz | Table 3-15 |
| M5 | Portugal step 3 | PS-PT | 438 | 49.6 Hz | Table 3-15 |
| M6 | Portugal step 4 | PS-PT | 470 | 49.5 Hz | Table 3-15 |
| M7 | Portugal step 5 | PS-PT | 359 | 49.3 Hz | Table 3-15 |

[inf] Portugal's motors all sit on PS-PT (north). 227 MW of the Portuguese pumps are actually in the south
(clusters 7c, 39, Fig 3-1), but Table 3-15 gives MW per step, not per cluster; a stated approximation.

**Checks:**
- Spain 49.5 Hz = 1,049 + 1,017 + 102 (cluster 10) = **2,168**, and 49.3 Hz = 78 + 156 + 75 + 211 + 68 = **588**:
  both equal Table 3-9.
- Portugal: 7a + 7b + 7c + 11 + 27 + 34 + 39 = **2,098**, equal to Table 3-15.

**Small Spanish stages** become frequency-switched `varrlc` loads (0 extra nodes) at their zone bus:
- 49.5 Hz: CAT 10 (102 MW);
- 49.3 Hz: Ebro 78 + 156 (234 MW, PS-ARA), VAL 17 (211), WAN 15 (75), NW 23 (68).

Cluster 50 (156 MW at 12:33:23.9, a "pump disconnection") is forced.

Totals: 49.5 Hz = 1,049 + 1,017 + 102 = 2,168 ✓; 49.3 Hz = 234 + 211 + 75 + 68 = 588 ✓ (Table 3-9).

**Inertia targets:** Spain **97,590 MW·s**, Portugal **21,884 MW·s** (Table 2-4, [FR] p.51). Met by H on the
ratings above, including the pumps (Portugal's value is only reachable with its pumps counted).

## 3. Inverter plants (switching `RES_Plant`)

### A. Report-listed trips (Table 3-3) — 12 plants, each with relays set from the report

| # | Plant | Bus | MW | Event | V at trip [kV] |
|---|---|---|---|---|---|
| R1 | Granada | GRA | 355 | 3 | 417.9 (220 kV side 242.9 > 242) |
| R2 | Badajoz TS1-a | BAD | 582 | 4a | 432.6–437.3 |
| R3 | Badajoz TS2 | BAD | 145 | 4b | 438.7 |
| R4 | Badajoz TS1-b | BAD | 118 | 5b1 | 443 |
| R5 | Segovia (two stages) | CYL | 23 + 94 | 5a1, 5a3 | 436.5, 443.4 |
| R6 | Sevilla TS1 | WAN | 550 | 5a2 | 437.7 |
| R7 | Badajoz TS3 | BAD | 72 + 20 + 16 | 5b4, 6a2, 6a3 | NA, NA, 447.7 |
| R8 | Cáceres TS1 + TS2 | CAC | 37.5 + 41 | 5b3, 6a4 | 250.4 (220 kV), 444.3 |
| R9 | Cádiz | WAN | 25.7 + 127.5 | 6a6, 6a7 | 247.5, 248.2 (220 kV) |
| R10 | Málaga | GRA | 154 | 6a8 | 448.6 |
| R11 | Cuenca | VAL | 530 | 6b | 448.6 |
| R12 | Murcia | SE | 63 | 6a5 | NA |

Huelva 33.7 MW and Sevilla TS2 3 MW are folded into the WAN aggregate.

**Relay structure (added 2026-11-25, SOURCES §12.2):**
- The Table 3-3 400 kV-side voltages are the effective thresholds. [CA] p.90–93, p.115–116 explain why they sit
  below the legal 435/440 kV: collector-transformer taps were set for lower voltages.
- Where a plant has no single threshold, use a timed stage (≈ 435 kV, ≈ 1.5 s) plus an instantaneous stage
  (≈ 440 kV) ([CA] p.94–95, Orden TED/749/2020).

### B. Zone aggregates — 8 plants, carrying the rest of the RES at fixed power factor

| # | Aggregate | Bus |
|---|---|---|
| A1–A5 | south-west split | WAN, BAD, CAC, SCE, GRA |
| A6 | North | CYL |
| A7 | East | VAL / SE |
| A8 | Portugal | PT-S |

- Their relay stages (Vt / Tt / Share 1–3) carry the **later Spanish waves** 8a, 8b, 12a, 12b, 19, 21, 32, 38,
  40 and 43 ([T3-1], 12:33:19.1–23.4). Each wave goes to the aggregate of its Fig 3-1 colour area (listed in §1).
  The settings are fitted to the wave times; the cause is not given in the report, so the fit is stated.
- **Portugal's distribution generation:** frequency stages per Table 3-4 ([FR] p.173): 49.8 / 50.2 Hz 321 MW and
  49.5 / 50.5 Hz 575 MW, delay ≈ 150 ms. The event-24 estimate (1,073 MW at 12:33:21.0) is used as a check.

- **Wind (mainly A6 North):** no overvoltage stage. Nordex farms held PF 0.98 inductive to 12:33:20, saw ≤ 1.07 pu,
  and stopped only after the collapse, mainly on underfrequency ([NX] p.4–6). Their P stays flat during the frequency
  fall.

**Count:** 20 inverter plants.

## 4. Loads and distribution-level behaviour (the user's point: realistic, no drift, not over-complicated)

**Law.** An exponential load per zone, P = P0·(V/V0)^α and Q = Q0·(V/V0)^β. The coefficients are the report's own,
from Table 4-23 / load model #2 ([FR] p.292–293):

| Load class | α | β |
|---|---|---|
| residential (summer) | 1.2 | 2.9 |
| commercial (summer) | 0.99 | 3.5 |
| industrial | 0.18 | 6.0 |

The report's mix is 1/3 each, giving **α ≈ 0.8, β ≈ 4.1** at V ≈ 1.

[inf] Regional mixes are possible later. The report fits four cities: Zaragoza, Barcelona, Sevilla and Madrid,
Figs 4-85…4-88.

**Element.** A `varrlc` R‖L (or R‖C) per zone, with R = V²/P(V) and X = V²/Q(V) computed from a filtered terminal
voltage (time constant ≈ 20–50 ms).
- Its law is explicit and benched against pandapower before use.
- It has a built-in branch-current output (0 extra nodes), so every load's P and Q is measured, not assumed.
- It replaces `fixed_load`, whose fallback behaviour was seen on the bench (RUNLOG §26).

**Embedded rooftop PV (< 1 MW).**
- Not in the TSO generation figures (Fig 2-17 excludes it). It is a net-load reduction in each zone.
- Its **overvoltage tripping is emergent**: the tripped fraction rises with transmission voltage. [FR] §4.3.4 and
  Fig 1-13 tie the change in TSO–DSO flows to these trips. Calibrate it to event 1's +317 MW net load increase
  (12:32:00–57) and Fig 1-13.
- Realised as a controlled current source at the zone bus (`src_ccin`, 0 extra nodes).
- This is our candidate for the **slow pre-event drift** the IEEE-39 model could not produce (RUNLOG §21).

**What stays forced:**
- event 2a/2b: −208 MW of wind and PV at 12:32:05–53, cause "unknown" ([FR] p.122). It is scheduled at the
  listed times per zone (2a north, 2b south);
- **RES down-regulation, 12:32:00–57 (added 2026-11-25 from [CA] p.88, SOURCES §12.1):** observable RES fell by
  ≈ 480 MW in that minute: secondary-regulation set-points down plus the 2a/2b trips. That leaves **≈ 270 MW of
  set-point ramp**, forced as a linear ramp on the RES aggregates, pro-rata to zone RES [inf]. Its cause (AGC and
  market) lies outside the model.
- **Check, not forced:** the same minute's ≈ 550 MW rise in net demand ([CA] p.88) must come out of the model by
  itself, from the rooftop-PV trips (≈ 317 MW) plus the exponential load law. Together with the two items above,
  France export should fall by ≈ 1,030 MW over the 57 s (≈ 1,500 → ≈ 450 MW, [CA] p.104);
- tie trips with external causes: Morocco 16a/b;
- line trips with unknown causes: 9, 36a/b, 42.

**LFDD and demand shedding:** Tables 3-8 / 3-10 / 3-16 / 3-17 (as in ib6, plus Portugal's Tables 3-11…3-14).

**Shunt reactors (added 2026-11-25, RUNLOG S27 §35).**
- Every reactor bank, connected and disconnected (Tables 2-7 / 2-8 plus the Fig 4-2 remainder), is lumped per
  zone as a **controlled admittance** (`varrlc`-type, 0 extra nodes).
- Its set-point is the connected Mvar at 12:32. It stays fixed through the replay: no reconnection happened in the
  event minute ([FR] Table 4-2, [CA] p.37).
- The disconnected capacity, ≈ 2,700 Mvar in South Spain alone (Fig 4-2), is then available to the prevention
  studies as manual or automatic switching, with no rebuild.
- **RES power factor:** Q/P = −0.135 (Fig 4-2), not ib6's −0.175.

## 5. Interconnections and targets at 12:32

| Border | Fig 2-22 (12:32, [read]) | Fig 2-41 |
|---|---|---|
| ES → PT | ≈ 2,100 MW (falling from 2,800 at 12:29) | 2,050 |
| ES → FR | ≈ 1,150–1,200 MW | 1,360 |
| ES → MA | ≈ 750 MW | 570 |
| **Total** | ≈ 4,050 MW | 3,980 |

**O6 resolved:**
- **The net per-border values are the targets.**
- Fig 2-4 is used only to split flow between parallel ties. My earlier Fig 2-4 sums double-counted line ends.
- France: AC ties (Hernani, Vic) plus HVDC: installed 2 × 1,000 MW, but at 12:32 in **Pmode 1, constant 1,000 MW
  export (2 × 500)** since 12:11 ([CA] p.33, p.105). It is a constant-P set-point and does not respond to the angle.
- **Which instant the France target is ([CA] p.104, SOURCES §12.1):** France export ran from ≈ 1,500 (12:32:00) down to
  ≈ 450 MW (12:32:57). [FR]'s ≈ 1,175 is therefore an instant inside that ramp. The pandapower snapshot is the
  12:32:00 state (Fig 2-4 voltages), so the 1,175–1,500 MW range is acceptable for it. The ramp itself is reproduced in
  PSCAD by the §4 drivers.
- Portugal: the schedule 2,545 → 2,000 MW was being regulated from 12:27 ([CA] p.88), which agrees with Fig 2-22's
  fall to ≈ 2,100.

Tie trip times are from [T3-1]:
- Morocco 16a/b, 20.229 / 20.473;
- France 31a/b, 21.407–21.535;
- Portugal 55a–f, 25.060–26.165.

## 6. Zone split of renewables and demand (O7 — method fixed, values computed in the pandapower step)

1. Area totals from Fig 2-41 (exact): N / SW / E production, RES by type, and demand.
2. The tripping plants (§3A) are placed first, at their Table 3-3 MW.
3. The rest of each area's RES is split over its zones in proportion to installed capacity by region and province.
   Red Eléctrica's regional press notes [EXT-6] give, e.g., Extremadura PV 7,868 MW (end 2024) and Andalucía
   20,840 MW installed (all technologies). The REData regional API was unavailable on 2026-11-24 (500/502), so it
   is to be retried.
4. Area demand is split by regional demand [EXT-6, to fetch], or by population as a fallback.
5. **Calibration in pandapower** (exponential loads via an outer fixed-point loop; taps explicit; started from a
   good initial guess) against:
   - Fig 2-4 voltages (south 410–418 kV, centre 404–408 kV);
   - Fig 2-4 main-corridor flows (e.g. ≈ 3.2 GW into Madrid);
   - Fig 2-22 border flows;
   - Table 4-26 fault levels.

## 7. Morocco (O4)

- **Synchronous** through the two 400 kV cables. It leaves at 12:33:20.2–20.5, about 1 s before France.
- Model: one machine plus load at MA. The size and inertia of Morocco's system come from an external source
  **[EXT-7, to fetch]**. Before 20.2 s only Morocco's share of the frequency response matters, so a ±50 % size
  error changes little; stated as a sensitivity.

## 8. Budget (Educational: 200 nodes, 64 module pages)

- **Pages:** 20 machines + 20 `RES_Plant` + HVDC + ≈ 4 logic pages ≈ **45 of 64**.
- **Nodes:** 22 buses × 3 = 66 (incl. the two TS buses); each pump motor behind its breaker adds a terminal node (7 × 3 = 21); generator
  step-up nodes; `RES_Plant` internals (≈ 4–5 each). Loads, small pumps, embedded PV and shedding use 0-node
  shunts / current sources, and there are no series multimeters. The estimate is ≈ 190–200, **at the limit: a
  skeleton build right after the pandapower model decides**.
- **Levers if over:** 2 SW aggregates instead of 5; merge R7 / R8 / R9 into aggregates; merge Portugal steps 1–3 (49.8–49.6 Hz) into one motor.

## 9. Verification steps
1. **Bench in network context:** exponential `varrlc` load, tapped transformer, staged pump motor, OV-tripping
   rooftop-PV source.
2. **pandapower v2 model,** calibrated as in §6, cross-checked with the own solver.
3. **PSCAD build** and one cold settle. It must match pandapower to ≈ 0.01 pu, as ib6 now does (RUNLOG §25).
4. **Parked-relay events:** the drift after event 3, the dV per GW, tie dynamics (Figs 3-7a, 4-91). Then relays on,
   with these added replay-gate checks from [CA] (SOURCES §12.1, §12.5):
   - 12:32 minute: France export −1,030 MW in 57 s; Olmedilla +15 kV, San Serván +13 kV;
   - France peak import 3,807 MW net (AC 4,609) at loss of synchronism, then a swing to 5,587 MW export;
   - Morocco supplying 314 MW at separation (49.314 Hz);
   - 2,037 MW of pumps shed after two steps; 1,402.5 MW of TSO-connected demand by the third.

   Optional, not gating: a small pulse should show a south-against-Porto mode near 0.6–0.67 Hz ([CVH], [CA]
   p.75). Then the replay gate,
   then the replay gate, then the prevention measures.
