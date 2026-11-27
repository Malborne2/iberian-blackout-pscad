# Fidelity of `rp_cascade` against the Final Report

model samples to t = 120.00 s (report time 90.00 s); t0 = 30.0 s = 12:32:00

RES instance matching by rating: 21 plants, scale 0.005154; uncertain matches (>15 % off): 17
  RES_Plant(0) -> A1_WAN: estimated S 422 vs 1902 MVA
  RES_Plant(1) -> R9_Cadiz: estimated S 997 vs 170 MVA
  RES_Plant(4) -> R3_Badajoz4b: estimated S 442 vs 161 MVA
  RES_Plant(5) -> A7_VAL: estimated S 233 vs 2016 MVA
  RES_Plant(6) -> R8_Caceres: estimated S 1135 vs 87 MVA
  RES_Plant(7) -> R11_Cuenca: estimated S 717 vs 589 MVA
  RES_Plant(8) -> R10_Malaga: estimated S 419 vs 171 MVA
  RES_Plant(9) -> R2_Badajoz4a: estimated S 103 vs 647 MVA
  RES_Plant(11) -> R1_Granada: estimated S 2209 vs 394 MVA
  RES_Plant(12) -> R6_Sevilla: estimated S 839 vs 611 MVA
  RES_Plant(13) -> A2_BAD: estimated S 792 vs 1537 MVA
  RES_Plant(14) -> A5_GRA: estimated S 1013 vs 1421 MVA
  RES_Plant(15) -> R4_Badajoz5b1: estimated S 888 vs 131 MVA
  RES_Plant(16) -> A9_ARA: estimated S 583 vs 1784 MVA
  RES_Plant(17) -> A3_CAC: estimated S 674 vs 1542 MVA
  RES_Plant(18) -> A4_SCE: estimated S 1598 vs 3989 MVA
  RES_Plant(19) -> A8_PTS: estimated S 483 vs 2979 MVA

## Model events (19)

| t report [s] | 12:3x clock | kind | element | MW |
|---|---|---|---|---|
| 62.555 | 12:33:02.555 | LFDD PT | PT load factor 1.000->1.055 |  |
| 63.524 | 12:33:03.524 | breaker | pump M3 PT (49.8 Hz) |  |
| 65.489 | 12:33:05.489 | LFDD ES | ES load factor 1.000->0.977 |  |
| 66.599 | 12:33:06.599 | breaker | pump M1 Duero (49.5 Hz) |  |
| 66.605 | 12:33:06.605 | LFDD PT | PT load factor 1.055->1.153 |  |
| 66.725 | 12:33:06.725 | LFDD ES | ES load factor 0.977->0.937 |  |
| 66.733 | 12:33:06.733 | breaker | Morocco tie open |  |
| 67.133 | 12:33:07.133 | LFDD ES | ES load factor 0.937->0.881 |  |
| 67.160 | 12:33:07.160 | LFDD PT | PT load factor 1.153->1.116 |  |
| 67.407 | 12:33:07.407 | LFDD PT | PT load factor 1.116->1.062 |  |
| 67.411 | 12:33:07.411 | LFDD ES | ES load factor 0.881->0.828 |  |
| 67.449 | 12:33:07.449 | LFDD PT | PT load factor 1.062->1.012 |  |
| 67.467 | 12:33:07.467 | LFDD ES | ES load factor 0.828->0.777 |  |
| 67.499 | 12:33:07.499 | LFDD ES | ES load factor 0.777->0.733 |  |
| 67.504 | 12:33:07.504 | LFDD PT | PT load factor 1.012->0.958 |  |
| 67.526 | 12:33:07.526 | LFDD PT | PT load factor 0.958->0.903 |  |
| 67.795 | 12:33:07.795 | LFDD PT | PT load factor 0.903->0.855 |  |
| 67.973 | 12:33:07.973 | LFDD ES | ES load factor 0.733->0.690 |  |
| 67.975 | 12:33:07.975 | LFDD PT | PT load factor 0.855->0.782 |  |

## Signal metrics (model - report), by tier

| tier | signal | phase | n | bias | RMSE | max abs err | r |
|---|---|---|---|---|---|---|---|
| PRIMARY | Iberian frequency [Hz] (Fig 1-10) | P0 pre-event | 29 | +0.0242 | 0.0248 | 0.0311 | -0.10 |
| PRIMARY | Iberian frequency [Hz] (Fig 1-10) | P1 slow rise | 77 | +1.02 | 1.34 | 2.85 | -0.58 |
| PRIMARY | Iberian frequency [Hz] (Fig 1-10) | P2 cascade | 12 | -0.656 | 0.902 | 1.67 | 0.96 |
| PRIMARY | Iberian frequency [Hz] (Fig 1-10) | P3 collapse | 15 | -2.48 | 2.58 | 3.73 | 0.94 |
| PRIMARY | Iberian frequency [Hz] (Fig 1-10) | all | 133 | +0.257 | 1.37 | 3.73 | 0.84 |
| PRIMARY | RoCoF [Hz/s] (Fig 1-10 derivative) | P0 pre-event | 29 | +0.00222 | 0.0109 | 0.0444 | -0.13 |
| PRIMARY | RoCoF [Hz/s] (Fig 1-10 derivative) | P1 slow rise | 77 | +0.0148 | 0.698 | 2.67 | 0.02 |
| PRIMARY | RoCoF [Hz/s] (Fig 1-10 derivative) | P2 cascade | 12 | -0.703 | 0.777 | 1.17 | 0.21 |
| PRIMARY | RoCoF [Hz/s] (Fig 1-10 derivative) | P3 collapse | 14 | -0.53 | 1.03 | 2.02 | -0.34 |
| PRIMARY | RoCoF [Hz/s] (Fig 1-10 derivative) | all | 132 | -0.111 | 0.672 | 2.67 | 0.34 |
| PRIMARY | Frequency at La Cereal vs PMU [Hz] (Fig 4-89; model MAD) | P0 pre-event | 0 | | | | | |
| PRIMARY | Frequency at La Cereal vs PMU [Hz] (Fig 4-89; model MAD) | P1 slow rise | 0 | | | | | |
| PRIMARY | Frequency at La Cereal vs PMU [Hz] (Fig 4-89; model MAD) | P2 cascade | 11 | -5.53 | 5.87 | 8.63 | 0.57 |
| PRIMARY | Frequency at La Cereal vs PMU [Hz] (Fig 4-89; model MAD) | P3 collapse | 12 | -5.79 | 7.55 | 11.9 | -0.60 |
| PRIMARY | Frequency at La Cereal vs PMU [Hz] (Fig 4-89; model MAD) | all | 23 | -5.66 | 6.8 | 11.9 | -0.11 |
| PRIMARY | Accumulated loss + net load increase [MW] (Fig 3-7a) | P0 pre-event | 226 | -227 | 234 | 331 | 0.97 |
| PRIMARY | Accumulated loss + net load increase [MW] (Fig 3-7a) | P1 slow rise | 77 | -483 | 484 | 778 | -0.00 |
| PRIMARY | Accumulated loss + net load increase [MW] (Fig 3-7a) | P2 cascade | 13 | -2.35e+03 | 2.59e+03 | 4.31e+03 | nan |
| PRIMARY | Accumulated loss + net load increase [MW] (Fig 3-7a) | P3 collapse | 0 | | | | | |
| PRIMARY | Accumulated loss + net load increase [MW] (Fig 3-7a) | all | 316 | -376 | 610 | 4.31e+03 | 0.51 |
| PRIMARY | Spain-France P vs PMU [MW] (Fig 4-91, + = ES->FR) | P0 pre-event | 0 | | | | | |
| PRIMARY | Spain-France P vs PMU [MW] (Fig 4-91, + = ES->FR) | P1 slow rise | 0 | | | | | |
| PRIMARY | Spain-France P vs PMU [MW] (Fig 4-91, + = ES->FR) | P2 cascade | 13 | +2.49e+03 | 2.71e+03 | 4.56e+03 | 0.52 |
| PRIMARY | Spain-France P vs PMU [MW] (Fig 4-91, + = ES->FR) | P3 collapse | 13 | +283 | 1.85e+03 | 5.67e+03 | 0.52 |
| PRIMARY | Spain-France P vs PMU [MW] (Fig 4-91, + = ES->FR) | all | 27 | +1.4e+03 | 2.3e+03 | 5.67e+03 | 0.45 |
| SECONDARY | 400 kV maximum voltage RISE from 12:32:00 [kV] | P0 pre-event | 226 | -2.85 | 4.39 | 9.31 | 0.84 |
| SECONDARY | 400 kV maximum voltage RISE from 12:32:00 [kV] | P1 slow rise | 77 | -11.6 | 47.6 | 129 | -0.13 |
| SECONDARY | 400 kV maximum voltage RISE from 12:32:00 [kV] | P2 cascade | 13 | -107 | 124 | 197 | -0.42 |
| SECONDARY | 400 kV maximum voltage RISE from 12:32:00 [kV] | P3 collapse | 0 | | | | | |
| SECONDARY | 400 kV maximum voltage RISE from 12:32:00 [kV] | all | 316 | -9.27 | 34.6 | 197 | -0.29 |
| SECONDARY | Voltage at La Cereal vs PMU [pu] (Fig 4-90; model MAD) | P0 pre-event | 0 | | | | | |
| SECONDARY | Voltage at La Cereal vs PMU [pu] (Fig 4-90; model MAD) | P1 slow rise | 0 | | | | | |
| SECONDARY | Voltage at La Cereal vs PMU [pu] (Fig 4-90; model MAD) | P2 cascade | 13 | -0.466 | 0.503 | 0.824 | -0.00 |
| SECONDARY | Voltage at La Cereal vs PMU [pu] (Fig 4-90; model MAD) | P3 collapse | 13 | -0.736 | 0.771 | 1.02 | -0.85 |
| SECONDARY | Voltage at La Cereal vs PMU [pu] (Fig 4-90; model MAD) | all | 28 | -0.571 | 0.629 | 1.02 | -0.68 |
| TERTIARY | 400 kV maximum voltage [kV] (Fig 3-7a) | P0 pre-event | 226 | +7.92 | 8.6 | 13 | 0.84 |
| TERTIARY | 400 kV maximum voltage [kV] (Fig 3-7a) | P1 slow rise | 77 | -0.806 | 46.2 | 138 | -0.13 |
| TERTIARY | 400 kV maximum voltage [kV] (Fig 3-7a) | P2 cascade | 13 | -96.5 | 114 | 186 | -0.42 |
| TERTIARY | 400 kV maximum voltage [kV] (Fig 3-7a) | P3 collapse | 0 | | | | | |
| TERTIARY | 400 kV maximum voltage [kV] (Fig 3-7a) | all | 316 | +1.5 | 33.3 | 186 | -0.29 |
| TERTIARY | Carmona 400 kV voltage [kV] (Fig 1-10 + 3-5) | P0 pre-event | 258 | +3.72 | 6.11 | 10.4 | 0.80 |
| TERTIARY | Carmona 400 kV voltage [kV] (Fig 1-10 + 3-5) | P1 slow rise | 104 | -43.3 | 97.6 | 349 | -0.31 |
| TERTIARY | Carmona 400 kV voltage [kV] (Fig 1-10 + 3-5) | P2 cascade | 12 | -167 | 185 | 287 | -0.72 |
| TERTIARY | Carmona 400 kV voltage [kV] (Fig 1-10 + 3-5) | P3 collapse | 17 | -314 | 319 | 408 | -0.01 |
| TERTIARY | Carmona 400 kV voltage [kV] (Fig 1-10 + 3-5) | all | 398 | -27.2 | 88.9 | 408 | -0.64 |

## Sequence: Table 3-3 plant trips

| event | plant | report t [s] | model t [s] | error [s] |
|---|---|---|---|---|
| 3 | R1_Granada | 57.220 | not tripped | |
| 4a | R2_Badajoz4a | 76.443 | not tripped | |
| 4b | R3_Badajoz4b | 76.820 | not tripped | |
| 5a1 | R5_Segovia | 77.368 | not tripped | |
| 5b1 | R4_Badajoz5b1 | 77.520 | not tripped | |
| 5a2 | R6_Sevilla | 77.780 | not tripped | |
| 6a3 | R7_BadajozTS3 | 78.360 | not tripped | |
| 6a4 | R8_Caceres | 78.410 | not tripped | |
| 6a7 | R9_Cadiz | 78.680 | not tripped | |
| 6a8 | R10_Malaga | 78.846 | not tripped | |
| 6b | R11_Cuenca | 78.951 | not tripped | |

## Sequence: defence plan, ties

| milestone | report t [s] | model t [s] | error [s] |
|---|---|---|---|
| 49.5 Hz crossed (pump step 1) | 80.180 | 77.593 | -2.587 |
| 49.0 Hz crossed (LFDD step 1) | 80.600 | 78.315 | -2.285 |
| 48.8 Hz crossed | 80.760 | 78.514 | -2.246 |
| 48.6 Hz crossed | 81.000 | 78.825 | -2.175 |
| 48.4 Hz crossed | 81.380 | 79.173 | -2.207 |
| 48.2 Hz crossed | 81.820 | 79.236 | -2.584 |
| 48.0 Hz crossed | 82.040 | 79.585 | -2.455 |
| Morocco tie 16a | 80.229 | 66.733 | -13.496 |
| France AC separation 31b | 81.535 | not reached / not modelled | |

Table 3-3 trips reproduced: 0 of 11

## Milestones

| quantity | report | model |
|---|---|---|
| minimum frequency [Hz] | 47.408 | 37.137 |
| maximum 400 kV voltage [kV] | 446.779 | 619.231 |
| Carmona voltage at 12:32:56 [kV] | 426.915 | 419.621 |

**Primary score** (mean RMSE/tolerance of the system-level metrics, lower is better, <= 0.5 good, > 1 poor): P0 0.36  P1 2.54  P2 3.00  P3 3.00

figures: iberia_eq/pscad/figs/fid_rp_cascade_overview.png, _sequence.png, _collapse.png, _score.png
