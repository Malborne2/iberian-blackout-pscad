# Iberian equivalent — data dossier with sources

Every number used to design the reduced Iberian equivalent is recorded here, with where it came from. Add to this
file before using a value in the model.

**Source codes**
- **[FR]**: ENTSO-E Expert Panel, *Final Report on the Grid Incident in Spain and Portugal on 28 April 2025*.
  Local copy: `Resources/Final Report on the Grid Incident in Spain and Portugal on 28 April 2025.pdf`. Text dump:
  `notes/Final_Report_on_the_Grid_Incident_in_Spain_and_Portugal_on_2.txt`.
  Page numbers are the report's printed page numbers, which equal PDF page numbers.
  This is the trusted source.
- **[FR-dig]**: curves digitised from [FR] figures in Stage 0 (`stage0/digitise_targets.py`), stored in
  `data/targets_fig*.csv`.
- **[MODEL]**: our own PSCAD results (RUNLOG section given). Used only as design evidence, never as data about Spain.
- **[EXT-n]**: external public sources (listed in §9). **None used yet.**

Confidence tags: **exact** (printed number), **read** (read off a figure; uncertainty stated), **inferred** (our
interpretation; reason stated).

---

## 1. Regional balance at 12:32 — three areas (Fig 2-41, [FR] p.61; same data as Fig 1-4, p.11)

Image: `figs/report_p061_fig2-40_2-41_regions.png`. All values are **exact** (printed in the figure).

| | North / North-West | South-West | East |
|---|---|---|---|
| Combined cycle P/Pmax [MW] | 340 / 1,100 | 320 / 760 | 330 / 820 |
| Coal P/Pmax | 230 / 350 | — | — |
| Nuclear P/Pmax | — | 660 / 1,000 | 2,740 / 3,030 |
| Hydro P/Pmax | 290 / 1,100 | (in "thermal RES + hydro") | (in "thermal RES + hydro") |
| Pump storage P/Pmax | 860 / 910 (generating) | — | **−1,180** / 1,290 (pumping) |
| Solar PV | 2,420 | **12,860** | 1,260 |
| Wind | 710 | 2,810 | 110 |
| Solar thermal | — | 1,420 | 70 |
| Cogeneration | 400 | 280 | 520 |
| Thermal RES + (small) hydro | 2,640 | 370 | 480 |
| **Total production** | **6,170** | **18,720** | **4,330** |
| **Demand** | **9,030** | **8,260** | **7,950** |

**External flows (arrows):**
- North → Portugal 200 MW; North → France 310 MW.
- South-West → Portugal 1,850 MW; South-West → Morocco 570 MW.
- East → France 1,050 MW.

**Check (inferred):**
- Production 29,220 − demand 25,240 = 3,980 MW.
- Exports 200 + 310 + 1,850 + 570 + 1,050 = 3,980 MW. Consistent.
- France total = 1,360 MW, Portugal 2,050 MW, Morocco 570 MW.

**Map lines (Fig 2-41):** the three areas meet at a point in the centre (Madrid region). Text (p.61) says the
south-west "is pushing active power in the direction of the centre-north and east".
- RES are "mainly located in the southwest".
- Nuclear is "in the east and southwest".
- CCGT is "spread across the three regions".

Inter-area transfers are not printed in the figure. They follow from the balance:
- the South-West exports about 10.46 GW minus 2.42 GW abroad, so about 8.0 GW goes internally;
- the North imports about 3.37 GW;
- the East imports about 4.67 GW.

**Status: inferred**, from the balance only.

## 2. Short-circuit power, 11:53 (Table 4-26, [FR] p.313) — **exact**

| Substation | 400 kV [MVA] | 220 kV [MVA] |
|---|---|---|
| SS Reyes (Madrid) | 10,555.3 | 9,657.4 |
| Eliana (Valencia) | 11,167.3 | 8,001.9 |
| Hernani (Basque, France tie) | 10,158.4 | 6,372.2 |
| Vic (Catalonia) | 8,830.1 | 4,963.6 |
| Rubí (Barcelona) | 11,104.3 | 10,107.1 |
| Mesón V. (Galicia) | 9,664.5 | 7,330.5 |
| Guillena (Seville) | 12,271.2 | — |
| Bienvenida (Badajoz) | 8,385.7 | — |

Percentiles against 2024 are in the same table (e.g. Vic 0.1 %, Bienvenida 13.4 %).
The pilot-node time evolution is in Figs 2-90/2-91 (p.~95) and Figs 4-119/4-120 (p.314).

**Design use:**
- target three-phase fault level at the corresponding equivalent buses;
- check ΔV ≈ ΔQ / S_sc (validated in [MODEL] RUNLOG S27 §21: 127 Mvar / 8,386 MVA ≈ +0.015 pu vs report +0.012).

## 3. Shunt reactors and status at 12:32 (Table 2-7 p.86 Spain; Table 2-8 p.87 Portugal) — **exact**

**Spain (RE), 400 kV unless noted, Mvar, C = connected, D = disconnected:**

| Region | Reactors |
|---|---|
| SOUTH | Almaraz 150 D; Arañuelo 150 D; Bienvenida 150 D; Brovales 150 D; Cabra 150 D; D.Rodrigo 150 D; E.Almaraz 220 kV 100 D; Guadame 220 kV 100 **C**; Guadame 150 **C**; Guillena 150 D; JM Oriol 220 kV 100 D; JM Oriol 150 D; Palos 220 kV 100 D; Valdecaballeros 150 D (×2) |
| CENTRE | Anchuelo 150 D; Moraleja 220 kV 100 **C** + 100 D; Moraleja 150 D; Morata 150 **C**; SS Reyes 150 D; Villaviciosa 220 kV 100 D; Villaviciosa 150 D |
| EAST | Belinchón 150 D; Eliana 220 kV 100 **C**; Litoral 150 D; Minglanilla 150 **C**; Olmedilla 150 D; Pinilla 150 D; Requena 150 D; Rocamora 150 D |
| NORTH | Aragón 150 D; Escatrón 220 kV 100 **C**; La Serna 150 **C**; Magallón 150 D (×2); Peñaflor 150 **C**; Rueda 150 D; Vitoria 150 **C** |
| NORTH-EAST | Begues 150 D; Juià 220 kV capacitor 150 D; Maials 150 **C**; Rubí 150 **C**; Sentmenat 150 **C** |

Sum connected (inferred, by adding):
- SOUTH 250 Mvar (Guadame only);
- CENTRE 250;
- EAST 250;
- NORTH 550;
- NORTH-EAST 450.

**Almost all southern reactors were out of service.**

**Portugal (REN):**
- Armamar 400 kV 150 D; Castelo Branco 220 kV 70 D; Fanhões 400 kV 150 D; Feira 150 D; Pedralva 150 D; Paraimo 150 D;
  Palmela 150 D; Portimão 150 D.
- Rio Maior 400 kV 150 **C**; Tábua 220 kV 70 **C**; Tavira 150 kV 75 **C**.

**Fig 4-2 / 4-3 ([FR] p.216, `figs/report_p216_fig4-2_4-3_reactive_assets.png`) — exact.** Status of reactive power
assets in "South Spain" (Mvar absorbed / remaining):

| | 12:32:00 | 12:33:00 |
|---|---|---|
| PO 7.4 generators | 74 / 146 | 185 / 332 |
| RES, fixed PF | 2,297 / 1,107 | 2,315 / 1,002 |
| Shunt reactors (connected / not connected) | 1,300 / 2,700 | 1,300 / 2,700 |

- RES reference = 20 % of the instantaneous P of > 5 MW RES, so that P = 3,404 / 0.2 = **17,020 MW**.
  **Realised Q/P = 2,297 / 17,020 = 0.135** [inf, arithmetic]. This replaces the ib6 `Kpf` 0.175 in pp_v2
  (RUNLOG S27 §35).
- "South Spain" = Table 2-7 regions SOUTH + CENTRE + EAST [inf]:
  - their installed reactors add up to 4,250 ≈ 4,000;
  - the model's RES in the matching zones is 16,807 ≈ 17,020 MW.
- **Table 2-7 lists only the "main" reactors.** Its connected S + C + E units sum to 750 Mvar, against 1,300 here.
  The missing 550 Mvar is placed at WAN 400 + SE 150 [inf].

Related: open lines for voltage control (Table 2-12, p.~102; Fig 2-2 p.32, `figs/report_p032_fig2-2_open_lines.png`).
Voltage-control actions: Table 2-2 (RE) and Table 2-3 (REN, p.~35). **Not yet extracted.**

## 4. Trips and their voltages (Table 3-3, [FR] p.144–145) — **exact**

Substations are anonymised by province ("TS1-Badajoz" etc.).

| Event | Time (CEST) | Substation | kV | Tech | MW | V at trip [kV] | Alignment |
|---|---|---|---|---|---|---|---|
| 3 | 12:32:57.220 | TS1-Granada | 400 | PV, wind, thermo-solar | 355 | 417.9 | Diverges |
| 4a | 12:33:16.443 | TS1-Badajoz | 400 | PV, thermo-solar | 582 | 432.6–437.3 | Diverges |
| 4b | 12:33:16.820 | TS2-Badajoz | 400 | PV | 145 | 438.7 | Diverges |
| 5a1 | 12:33:17.368 | TS1-Segovia | 400 | wind | 22.87 | 436.5 | Aligns |
| 5b1 | 12:33:17.520 | TS1-Badajoz | 400 | PV | 118 | 443 | Possibly |
| 5b2 | 12:33:17.547 | TS1-Huelva | 220 | wind, PV | 33.73 | NA | Unknown |
| 5a2 | 12:33:17.780 | TS1-Sevilla | 400 | PV | 550 | 437.7 | Diverges |
| 5a3 | 12:33:17.940 | TS1-Segovia | 400 | wind | 94 | 443.4 | Aligns |
| 5b3 | 12:33:17.975 | TS1-Cáceres | 220 | PV | 37.5 | 250.4 | Diverges |
| 5b4 | 12:33:18.020 | TS3-Badajoz | 220 | PV | 71.9 | NA | Unknown |
| 6a1 | 12:33:18.102 | TS2-Sevilla | 220 | PV | 3 | 246.5 | Diverges |
| 6a2 | 12:33:18.220 | TS3-Badajoz | 220 | PV | 20 | NA | Unknown |
| 6a3 | 12:33:18.360 | TS3-Badajoz | 400 | PV | 16 | 447.7 | Aligns |
| 6a4 | 12:33:18.410 | TS2-Cáceres | 400 | PV | 41 | 444.3 | Diverges |
| 6a5 | 12:33:18.540 | TS1-Murcia | 400 | PV | 63 | NA | No requirement |
| 6a6 | 12:33:18.630 | TS1-Cádiz | 220 | PV | 25.7 | 247.5 | Diverges |
| 6a7 | 12:33:18.680 | TS1-Cádiz | 220 | PV | 127.5 | 248.2 | Diverges |
| 6a8 | 12:33:18.846 | TS1-Málaga | 400 | PV | 154 | 448.6 | Possibly |
| 6b | 12:33:18.951 | TS1-Cuenca | 400 | PV | 530 | 448.6 | Possibly |

The full event list including DSO-level and lumped losses is Table 3-1 (p.~120) and Table 3-4 (DSO units before
12:33:23). The cumulative-loss curve is Fig 3-7a [FR-dig] `data/targets_fig3-7a.csv`.

## 5. Voltages before and during the event — **exact** unless tagged

**[FR] p.122 (`figs/report_p122_event_sequence.png`):**
- Granada 400/220 kV transformer trip: 220 kV side 242.9 kV phase B (setting 110 % Un = 242 kV, t = 0 s); 400 kV side
  417.9 kV; SCADA 12:32:56: 233.4 kV (1.061 pu) on the 220 kV side.
- Badajoz TS1 SCADA 12:33:10: 434.0 kV (evacuation bay), 430.5 / 429.9 kV (busbars 1/2).
- Cáceres TS3 PMU 12:33:16.420: 431.72 kV positive sequence (phases 428.1 / 436.8 / 430.2 kV).

**[FR] p.123:**
- 12:32:58: positive-sequence voltages over 1.05 pu.
- 12:33:17: maximum 442.5 kV (1.106 pu).
- 12:33:18: 451.4 kV (1.128 pu), "higher values in the southern part of Spain" (Fig 3-2 heatmaps).

**Fig 3-7a [FR-dig]:** 400 kV maximum 421.8 → 427.8 kV between events 3 and 4a (no trips); 432.7 / 435.6 / 441.6 kV
at 76.9 / 77.6 / 78.4 s.

**[FR] p.11, p.~62–63:** before 12:30, voltages during the oscillation "barely exceed 410 kV", lower threshold
375 kV.

**Fig 2-4 ([FR] p.37) SCADA busbar voltages at 12:32:00 — read**, ±2 kV. The embedded image is 1,371 × 520 px, so
some labels are illegible and are left out.
- SOUTH: Almaraz 406; Bienvenida 412; Brovales 413; Balboa 412; S.Serván 410; Carmonita 411; Arcos Frt. 413;
  Pinar Rey 414; Cabra 418; Guadame 417; Cártama 415; Tajo Enc. 414; Jordana 416; Manzanares 416; Rodaandal 416;
  Brazatort 412; Valdecaballeros 406; Caparacena (Granada) 409; Tabernas 404.
- CENTRE: Morata 404; SS Reyes 404; Galapagar 408; Mudarra 405.
- NORTH: Grijota 404.
- EAST: Litoral 406.
- NORTH-EAST: Vic 395.

**Pattern (inferred from the reading):** the south (Andalusia / Extremadura) sits at 410–418 kV, the centre and north
at 404–408 kV, and the north-east lower (Vic 395 kV).

## 6. Network topology (Fig 2-4, [FR] p.37; Fig 2-3 at 12:00, p.36)

Images:
- `figs/report_p037_fig2-4_topology.png`;
- zooms `..._west_zoom.png` (Portugal, Galicia, Castilla y León, Extremadura, Andalusia, Madrid) and
  `..._east_zoom.png` (Basque Country, Aragón, Catalonia, Valencia, Murcia, eastern Andalusia).

It is a SCADA schematic, not geographic: the layout is roughly geographic, but distances are not to scale. It shows:
- 400 kV substations by name;
- line connections and double circuits;
- line flows in MW;
- the Portuguese network (grey area, left);
- the France ties at the top: Argia–Hernani / Arkale (west), Pragnères–Biescas (centre), Baixas–Vic and Baixas–S.Llogaia
  HVDC (east);
- the Morocco tie at the bottom: Tarifa → BEHA / MLL.

**Use:** corridor structure (which regions connect to which, how many circuits), and line flows at 12:32 to check the
equivalent's load flow. **Status: to be transcribed** into a corridor list (§8). Lengths are not in [FR] (§9).

## 7. Mechanisms and timing relevant to the design — **exact** quotes and paraphrases

- **[FR] p.11, p.61:** generation in the south-west "very high relative to consumption"; "high electricity transit
  flows from the southwest of Spain to the surrounding areas"; maximum angle spread in the south-west (Fig 2-40
  heatmap, 12:00).
- **[FR] p.122, events 1–2 (12:32:00–12:32:57):** net load increase of ≈ 317 MW on the distribution grids (event 1);
  ≈ 208 MW change or disconnection of wind/solar > 1 MW, in northern (2a) and southern (2b) Spain.
  **Candidate driver of the slow +6 kV drift** between events 3 and 4a (to be examined: [MODEL] RUNLOG S27 §21 shows
  that the Granada trip alone does not produce it).
- **[FR] p.~78–80 (Figs 1-11, 2-84…2-86):** reactive power of conventional units > 100 MW against their reference,
  per area (north/north-west, centre/south-west, east/north-east). **To extract**, for the unit Q targets.
- **[FR] p.~96–97:** "Thermal 4–Centre/South-West" CCGT scheduled for voltage control in western Andalusia was
  unavailable from 19:52 on 27 April.
- Oscillations: 0.63 Hz local mode (12:03–12:08) and 0.2 Hz East–Centre–West inter-area mode (12:19–12:22) (p.11).
- Frequency, tie flow and Carmona voltage curves: Figs 3-5, 4-89, 4-90, 4-91 [FR-dig] `data/targets_*.csv`.

## 8. Corridors between zones — from OSM line geometry ([EXT-1]); cross-check against Fig 2-4 pending

Built by `build_corridors.py` → **`corridors.csv`** (every inter-zone line: substations, route km, circuits, OSM line
names) and **`zone_km.csv`** (circuit-km inside each zone, plus half of each tie, which sets line charging).
Zones and substation positions: `substations.csv` (`build_substations.py`, [EXT-2]).

Summary (route km = length along the OSM geometry; circuits from the OSM `circuits` tag, else cables/3, else 1):

| Corridor | Lines | Circuits | Main paths (route km × circuits) |
|---|---|---|---|
| CAC–MAD | 3 | 6 | Almaraz–Villaviciosa 168×2; Almaraz–Morata 217×2; Arañuelo–Morata 193×2 |
| BAD–CAC | 2 | 3 | S.Serván–Almaraz 143×2; Bienvenida–Almaraz 181×1 |
| BAD–WAN | 2 | 3 | Brovales–Guillena 119×2; Bienvenida–Guillena 77×1 |
| SCE–WAN | 2 | 4 | Arcos–La Roda de Andalucía 143×2; Guillena–Valdecaballeros 207×2 |
| CAC–SCE | 2 | 3 | Arañuelo–Valdecaballeros 101×2; Almaraz–Guadalquivir Medio 249×1 |
| GRA–SCE | 1 | 1 | Tajo de la Encantada–Cabra 67 |
| GRA–WAN | 1 | 2 | Tajo de la Encantada–Jordana 80×2 |
| GRA–SE | 1 | 1 | Huéneja–Tabernas 59 |
| CYL–MAD | 4 | 4 | Segovia–Galapagar 60 and three of 200+ km |
| MAD–VAL | 3 | 4 | Trillo–Villanueva de los Escuderos 84×2; Morata–Olmedilla 149; Minglanilla–Belinchón 146 |
| SE–VAL | 3 | 4 | Olmedilla–(Romica area) 75×2; Rocamora–Beneixama 67; Ayora–Campanario 34 |
| ARA–MAD | 2 | 3 | Magallón–Trillo 207×2; Almazán–Fuendetodos 137 |
| ARA–CAT | 2 | 3 | Aragón–(Mequinenza/Ascó area) 73×2; Rubí–… 131 |
| ARA–N | 2 | 3 | …–Muruarte 60×2; Santa Engracia–La Serna 58 |
| ARA–VAL | 1 | 1 | …–Morella 77 |
| CYL–NW | 3 | 5 | Velilla–La Robla 127×2; Tordesillas–… 147×2; La Mudarra–Montearenas 169 |
| CYL–N | 3 | 3 | 61–206 km |
| N–NW | 4 | 4 | 50–231 km |
| CAC–CYL | 1 | 1 | Almaraz–Hinojosa 178 |
| **Portugal ties** | | | Cartelle–Lindoso 47×2 (NW); Aldeadávila–Lagoaça 5 (CYL); Cedillo–Falagueira 25 (CAC); Brovales–Alqueva 81 (BAD); Puebla de Guzmán–Tavira 58 (WAN); Fontefría–Ponte de Lima 90 (NW) |
| **France ties** | | | Hernani/Itxaso–Argia (N; 2×2 km to the border + 34 km); Vic–Baixas 92 (CAT) |

Circuit-km per zone (incl. half of ties):
- Spain: ARA 1,398; BAD 672; CAC 1,319; CAT 1,396; CYL 1,738; GRA 623; MAD 1,947; N 1,311; NW 2,690; SCE 1,536;
  SE 1,023; VAL 1,117; WAN 1,607.
- **Spain total ≈ 18,400** circuit-km; PT 3,198.

**Known gaps and limits (must be handled before use):**
- 89 line chains end at an unmapped junction (OSM gaps). Some corridors are therefore under-counted.
  Fig 2-4 shows e.g. more Madrid–Castilla links and the Granada–Litoral chain.
- **Morocco ties missing:** the submarine cables end outside OSM's Iberian substations. Fig 2-4 shows Puerto de la
  Cruz → BEHA/MLL with 471 and 277 MW.
- **Not in this list:** the HVDC Baixas–Santa Llogaia (DC, not 400 kV AC) and Biescas–Pragnères (220 kV).
- Missing `circuits` tags default to 1, so double-circuit lines may be under-counted.
- Substations without a name show as "…" or "?".
- The Spain total should be checked against Red Eléctrica's published 400 kV circuit length (to be looked up and
  cited before calibration).

**Next (done in §8b):** cross-check every corridor against Fig 2-4 (`figs/report_p037_*`: connections and 12:32 flows) and correct
the circuit counts. Then compute the initial R/X/B per corridor from per-km parameters ([EXT-3]).

### 8b. Cross-check of §8 against Fig 2-4 ([FR] p.37) — read 2026-11-23

Read from the native embedded image (1,371 × 520 px, extracted with PyMuPDF and zoomed ×3; tiles in the session
scratchpad, reproducible from the PDF).
- Flows are MW at 12:32 as printed next to each line end.
- The arrow direction is not always unambiguous at this resolution, so **direction is tagged "?" where unsure**.
- Circuit counts are the number of parallel red lines between the two boxes.

| Corridor / tie | Fig 2-4 reading | OSM (§8) | Verdict |
|---|---|---|---|
| Almaraz → Morata | 2 circuits, 513 / 513 MW towards Madrid | 2 × 217 km | **agrees** |
| Almaraz (J.M. Oriol side) → Villaviciosa | 2 circuits, 716 / 699 MW towards Madrid | 2 × 168 km | **agrees** |
| Arañuelo / Valdecaballeros → Morata | 2 circuits, 393 / 393 MW towards Madrid | Arañuelo–Morata 2 × 193 km | **agrees** |
| → Sum CAC/SCE → Madrid | ≈ 3,230 MW over 6 circuits | — | read |
| Bienvenida / S.Serván / Carmonita → Almaraz | 880, 967, 230 MW (towards Almaraz) | S.Serván–Almaraz 2 × 143; Bienvenida–Almaraz 181 | agrees on the paths; **OSM may miss the Carmonita–J.M. Oriol link** |
| Bienvenida – Guillena | vertical line, 49 / 500 MW labels nearby, direction ? | 77 km × 1 | agrees on the path |
| Caparacena → Huéneja → Tabernas → Litoral | 300 → 428 → 791 → 917 MW eastwards | Huéneja–Tabernas 59 km only | **OSM chain incomplete** (Caparacena–Huéneja, Tabernas–Litoral are within zones or in gaps) |
| Tajo Enc. – Jordana / Cártama – Cabra | 93, 80, 29 MW | Tajo–Jordana 2 × 80; Tajo–Cabra 67 | agrees on the paths |
| Cartelle → Lindoso (PT) | 2 circuits, 102 / 101 MW towards Portugal | 2 × 47 km | **agrees** |
| Aldeadávila → Lagoaça (PT) | 1 circuit, 652 / 653 MW towards Portugal (+ 220 kV Saucelle/Pocinho 70, 23, 23) | 1 × 5 km | **agrees** |
| Cedillo → Falagueira (PT) | 1,124 / 1,130 MW towards Portugal | 1 × 25 km | **agrees** |
| P.Guzmán → Tavira (PT) | 772 / 780 MW towards Portugal | 58 km (labelled Puebla de Guzmán–Tavira) | **agrees** |
| Brovales – Alqueva (PT) | link visible, flow label unclear (≈ 131?) | 81 km | path agrees, flow unread |
| Hernani → Argia (FR) | 664 / 668 MW, direction ? | Hernani/Itxaso–Argia 2 + 1 | path agrees |
| Arkale (220 kV) → Argia | 19 MW | not in 400 kV list | — |
| Biescas → Pragnères (220 kV) | 0 MW | not in 400 kV list | — |
| Vic → Baixas (FR) + S.Llogaia HVDC | 506 / 506 at Baixas; S.Llogaia 500 / 500 | Vic–Baixas 92 km; HVDC excluded | path agrees |
| Puerto de la Cruz → Morocco (BEHA, MLL) | cables drawn, flows near Tarifa 471 / 277 MW | **missing in OSM** | add from Fig 2-4 |

**Conflict to resolve:** the Fig 2-4 tie readings do not add up to Fig 2-41's net exports at 12:32.
- Portugal: ≈ 2,900 MW read vs 2,050.
- France: ≈ 690 + 1,000 + 500 MW read vs 1,360.

Likely causes:
- arrows read in the wrong direction on some lines;
- both line-end values counted where they are one line;
- Fig 2-4's own time stamp vs the figure.

**Fig 2-41's net values are used as the targets.** The Fig 2-4 values serve only as the split between parallel
paths. To be re-checked against Fig 2-55 (Spain–France exchange, p.~64) and Fig 5-46 (Spain–Portugal, p.~334).

## 9. External sources (only where [FR] has no data)

- **[EXT-1]** OpenStreetMap contributors, 400 kV power lines and cables, Overpass API query
  `way["power"~"^(line|cable)$"]["voltage"~"400000"]`, bbox 35.9,-9.6,43.9,3.4, `out tags geom`.
  Fetched 2026-11-23 20:05 CET from https://overpass-api.de (OSM base timestamp in the file).
  Raw file: `ext/osm_lines_400kV.json` (3,159 ways). Licence ODbL (© OpenStreetMap contributors).
- **[EXT-2]** OpenStreetMap contributors, substations, fetched 2026-11-23 19:59–20:03 CET:
  - `ext/osm_substations_400kV.json`: power=substation, voltage~400000, ES and PT areas;
  - `ext/osm_substations_ree.json`: operator~"Red El", ES;
  - Nominatim place search for towns (San Sebastián de los Reyes, Cofrentes, Ascó, Escatrón, Vitoria-Gasteiz):
    `ext/osm_nominatim_places.jsonl`.

  Each row of `substations.csv` names its OSM element id or Nominatim query.
  **Guadame → "Subestación de Guadalquivir Medio" (OSM way/145461765) is an inference:** SCADA code GUADAME =
  GUADAlquivir MEdio. Its position fits the Fig 2-4 links.
- **[EXT-3]** standard 400 kV overhead-line parameters per km: to be chosen and cited (initial estimate only; final
  impedances calibrated to §2).
- **[EXT-4]** Red Eléctrica published 400 kV network length (for the check above): to be looked up.

## 10. Tool note — does PSCAD 5.1 (Educational) have a load flow? (checked 2026-11-23)

**No standalone load-flow solver was found.** Evidence:
1. **The PSCAD 5.1 help** (`C:\PSCAD_work\help\x`, decompiled `ol-help.chm`; 24 pages mention "load flow") treats
   load flow only as an *external* input. Synchronous machines and sources start from terminal V, P, Q "which might
   correspond to the values obtained from a load flow program" (Synchronous Machine › Start-up and Initialization;
   3-phase source › "At the Terminal").
2. **The line-constants program's "LOAD FLOW RXB DATA"** is R/X/B output formatted for a load-flow program, not a
   solver.
3. **The `Bus` component** (`mhi.pscad` 3.1.3, `component.py`) stores Name, BaseKV, VM, VA and type
   (0 Auto, 1 Load, 2 Generator, 3 Swing). These hold load-flow data, e.g. a case imported from PSS/E through
   Manitoba's E-TRAN, which is not installed here. Nothing in PSCAD solves for them.
4. **`emtdc/*/inc/pflow.h`** only contains `USE PF_DISPLAY`, a display module. No load-flow executable or library
   is in `C:\Program Files (x86)\PSCAD\5.1.0\Utilities` or `bin`.

**Consequences for the design:**
- **Decision (user, 2026-11-23): pandapower is the main and only load-flow tool** for the equivalent.
  `stage12/qdesign.py` (own solver) is retired for this work.
- An independent cross-check can come from either of two sources:
  - **pandapower 3.5.6** (installed 2026-11-23 with the user's approval; checked on its IEEE-39 case: converged,
    V 0.982–1.064 pu);
  - PSCAD itself: a short EMT run with the machines held as ideal sources at the load-flow V and angle. That reaches
    steady state in under a second of simulated time, a few minutes of wall time.

## 11. Sources added 2026-11-24 (Draft 2 of the v2 list)

**[FR] items newly used:**
- **Fig 4-84 ([FR] p.292, `figs/report_p292_fig4-84_tso_dso.png`), read 2026-11-25 (RUNLOG S29 §4):**
  - **Sign:** negative means the DSO injects into the TSO grid.
  - **Scope:** the 400 kV TSO–DSO interface only, 12:00–12:33.
  - P: 7.8–9.0 GW, rising with voltage.
  - Q: −1.8 Gvar at 395 kV → −1.0 Gvar at 418 kV; ≈ −1.3 Gvar at 412 kV [read ±0.1 Gvar].
- **Table 2-12 ([FR] p.114–115):** 400 kV lines still open at 12:32 are Pierola–Sentmenat 2, Cofrentes–La Muela 1,
  Fuendetodos–Mezquita and Mezquita–Morella 1. Lengths in pp_v2 are [inf] (straight distance × 1.15).
- **Table 3-1** (p.117–~120): full event sequence, parsed into **`table3-1_events.csv`** (173 rows: event, country,
  time, description, MW).
  - Checks: Spanish pump trips 13a + 13b + 14 + 10 + 15 + 17 + 23 = 2,756 MW = Table 3-9; Portuguese pump trips =
    2,098 MW = Table 3-15.
  - Parser slip: 7b is −124 MW (the footnote marker "21" was read as the value).
- **Table 3-9** (p.199) and **Table 3-15** (p.203): pump steps. **Table 3-4** (p.173): Portuguese DSO generation
  tripped on frequency.
- **Fig 3-1** (p.121): event locations and cluster areas.
- **Table 2-4** (p.51): KE Spain 97,590 MW·s (H 2.17–2.67 s), Portugal 21,884 MW·s (2.45–2.95 s), Iberia
  119,474 MW·s. **p.50:** KE = Σ H·S over rotating generators, including solar thermal and synchronous renewables;
  loads add to H.
- **Figs 2-17 / 2-19** (p.44–45): Spanish and Portuguese generation mix at 12:30 [read].
  **Fig 2-16:** Portuguese load ≈ 5.6 GW. **Figs 2-21 / 2-22** (p.46–47): border flows at 12:32 [read].
- **Table 4-23 / load models #1–#2** (p.292–293): exponential-load coefficients. **§4.3.4 / Fig 1-13:** rooftop-PV
  overvoltage trips correlated with TSO–DSO flow changes.

**External:**
- **[EXT-5]** Consejo de Seguridad Nuclear (CSN), report on the April 2025 blackout (public use), April 2026:
  https://www.csn.es/documents/d/portal-csn/2026-04-22-blackout-report-public-use-april-2025
  - Local copy `ext/csn/CSN_blackout_report_2026-04.pdf`, text `.txt` (19 pages).
  - **Confirmed, p.6 table:**

    | Unit | Status | Output [MWe] |
    |---|---|---|
    | Almaraz I | cold shutdown | — |
    | Almaraz II | 70 % | 680 |
    | Ascó I | 70 % | 719 |
    | Ascó II | 100 % | 1,034 |
    | Cofrentes | cold stop | — |
    | Trillo | refuelling | — |
    | Vandellós II | 100 % | 1,089 |

  - Sum **3,522 MWe**; the search summary's "3,387" was wrong.
  - The four in-service units tripped automatically on the frequency drop (p.6–7).
  - [FR] gives P = 3,400 MW (Fig 2-41) / 3,390 MW (trips): **[FR] values are used for P**, CSN for which units ran.
- **[EXT-6]** Red Eléctrica regional press notes, installed capacity by region (2024 data):
  - Extremadura: https://www.ree.es/sites/default/files/07_SALA_PRENSA/Documentos/2024/NP_Extremadura_EN.pdf
    (PV 7,868 MW end 2024).
  - Andalucía: https://ree.es/sites/default/files/07_SALA_PRENSA/Documentos/2024/NP_Andalucia_EN.pdf
    (20,840 MW installed, all technologies).
  - Values from the search summary; **to confirm from the PDFs**. Other regions: same series.
  - The REData API (apidatos.ree.es, regional endpoints) returned 500/502 errors on 2026-11-24.
- **[EXT-7]** Morocco system size (news sources, approximate):
  - installed ≈ 12.0 GW at end 2024, of which ≈ 5.4 GW renewable:
    https://www.moroccoworldnews.com/2026/01/273871/wind-power-emerges-as-key-driver-of-moroccos-energy-transition/
  - record peak ≈ 8.4 GW: https://en.le360.ma/economy/heatwave-fuels-record-electricity-demand-in-morocco_DOQ4COMJPVEHXNGOIQ5Z7YXJAU/ and
    https://northafricapost.com/99212-morocco-sets-new-record-for-electricity-consumption.html

  **[FR] facts that calibrate the Morocco equivalent instead:**
  - an inter-area **Morocco–Iberia mode ≈ 0.5 Hz** ([FR] §4 modal analysis, p.~240, text line ~17030);
  - the ties were tripped by an **under-frequency protection on the Moroccan side** (16a at 12:33:20.229 with
    direct transfer trip, 16b at 20.473; [FR] p.180–181), so the trip is emergent;
  - the ES–MA flow is correlated with southern voltage (p.~305, Analysis 1);
  - reactive flows: Fig 2-94 (p.100).
- **[EXT-8]** Red Eléctrica REData API, April 2025 monthly, by autonomous community (peninsular), fetched 2026-11-24:
  - generation by technology (`generacion/estructura-generacion`) and demand (`demanda/evolucion`);
  - daily resolution returned HTTP 500, so monthly is used as the regional-share proxy;
  - raw files: `ext/ree/ree_generation_by_ccaa.json`, `ext/ree/ree_demand_by_ccaa.json`; table:
    **`regional_april2025_MWh.csv`**;
  - totals April 2025: demand 17,627 GWh, PV 3,995, wind 4,254, solar thermal 311, nuclear 2,952;
  - PV shares: Andalucía 24.7 %, Extremadura 23.3 %, Castilla-La Mancha 23.2 %, Aragón 9.2 %,
    Castilla y León 9.1 %, Murcia 5.8 %;
  - demand shares: Cataluña 18.6 %, Andalucía 16.0 %, Madrid 11.6 %, C. Valenciana 11.1 %.
- **[EXT-3]** 400 kV line per-km starting values: pandapower 3.5.6 standard types "490-AL1/64-ST1A 380.0"
  (r 0.059, x 0.253 Ω/km, c 11.0 nF/km) and "679-AL1/86-ST1A 380.0" (r 0.042, x 0.250, c 14.6).
  - **x and c only** (r is taken as 0.03 Ω/km per circuit [inf], a bundled-conductor value; r barely affects voltage).
  - Final impedances are calibrated to Table 4-26.

## 12. Supplementary sources added 2026-11-25 (committee report + two WISO 2025 papers)

[FR] stays the authority. Items below are used only where [FR] has no value, or as a cross-check. Each is tagged
**new** (not found in [FR]), **adds** (adds detail to an [FR] item) or **agrees** (repeats [FR]; listed only as a check).

**Source codes**
- **[CA]**: Comité de Análisis 28-A (MITECO), *Informe no confidencial*, approved 16 June 2025. Spanish, 182 pages,
  many names redacted. Local: `Resources/Informe-no-confidencial-Comite-de-analisis-28A.pdf`; text
  `notes/Informe-no-confidencial-Comite-de-analisis-28A.txt`. Page numbers = printed page numbers.
- **[NX]**: D. Ortiz, E. Arrechea (Nordex), "Iberian Peninsula blackout: analysis and performance of Nordex wind
  power plants", WISO 2025, doi:10.1049/icp.2025.4529. Text `notes/Iberian_Peninsula_blackout_analysis_and_performance_of_Norde.txt`.
- **[CVH]**: L. Cai, T. Veith, Y. Hou, "Analysis of the power system oscillations before the blackout in Spain and
  Portugal on April 28, 2025", WISO 2025, doi:10.1049/icp.2025.4524. Prony analysis of Gridradar data. Text
  `notes/Analysis_of_the_power_system_oscillations_before_the_blackou.txt`.
- `Resources/Spain Portogal 28-April Blackout.pdf` (Aug 2025): image-only slides, not one of the new files, not read.

### 12.1 The 12:32:00–12:32:57 minute — **new**, design-relevant
- [CA] p.87–88: export through the interconnections fell by **1,030 MW in 57 s** (France). The operator splits it:
  - **≈ 480 MW: reduction of observable renewable generation**, partly secondary-regulation set-points down, partly
    isolated trips. The 208 MW of trips listed in [FR] p.122 (events 2a/2b) are inside this figure.
  - Synchronous generation: almost unchanged.
  - **≈ 550 MW (rest): rise in observed demand**, compatible with loss of unobservable distributed generation
    ([FR]'s 317 MW, event 1) plus the voltage dependence of load.
- [CA] p.88: the **Portugal schedule change** agreed at 12:20 (2,545.2 → 2,000 MW) started regulating at 12:27. The
  adjustment window is ±5 min, and the schedule change can cause transient imbalances. [FR] Fig 2-22 shows ES→PT
  falling from ≈ 2,800 (12:29) to ≈ 2,100 MW (12:32) **(agrees)**.
- [CA] p.39: ramp examples Olmedilla 413 → 428 kV, Arroyo de San Serván 411 → 424 kV in 57 s. p.89, Gráfico 39:
  south–centre angle difference shrinks in the same minute (less south→north flow).
- [CA] p.88 (operator's view): distribution OLTCs set for the earlier low voltages may lag, giving overvoltage on
  distribution secondaries while transmission is still within limits.
- [CA] p.104: France export ≈ 1,500 MW at 12:32:00 (AC ≈ 500 + HVDC 1,000), ≈ 450 MW just before event 3 (Granada),
  ≈ 0 after it. So **[FR] Fig 2-22's ≈ 1,175 MW is a point inside a 1,000 MW ramp**, and the "ES→FR at 12:32" target
  depends on the instant chosen.

### 12.2 Trip mechanism at the collector substations — **adds**
- [CA] p.90–93, Granada (event 3): instantaneous overvoltage protection on the 220 kV side of the 400/220 kV
  autotransformer of the common evacuation infrastructure (ICE). Setting 70 V × 2,000 × √3 = 242.5 kV (110 %).
  Phase readings 70.14 V (242.97 kV), then the other phases 55 ms later at 70.53 V (244.32 kV).
  - REE's 400 kV side: 418 kV before, 423.9 kV after. 242.5 kV at the nominal ratio would mean 440 kV.
  - The committee reads this as **a transformer tap set for lower voltages** (or an "early" trip). Inside the ICE,
    no 30/220 kV reading exceeded 1.08 pu.
- [CA] p.115–116: general point. Transmission voltages inside limits can be overvoltages behind ICE or DSO
  transformers whose taps were not adjusted fast enough. The **rate** of voltage rise matters, not only its value.
  The operating procedures have no rate-of-change limit.
- **Design consequence [inf]:** using the 400 kV-side "V at trip" from Table 3-3 as each plant's effective threshold
  (V2 list §3A) is physically justified: it lumps the frozen collector tap and the relay setting together.
- [CA] p.94–95, Badajoz (events 4a/4b): SCADA 430–435 kV before 12:33:15; 443 kV at the second trip. One plant's
  report says it tripped on **> 435 kV for > 1.5 s, exceeding 440 kV before the trip** (Orden TED/749/2020
  withstand curve, [CA] Gráfico 40). → a timed stage (≈ 435 kV, ≈ 1.5 s) plus an instantaneous stage (≈ 440 kV) is a
  supported relay structure.
- [CA] p.96, Sevilla (event 5a2): 437.91 kV before the trip **(agrees** with Table 3-3, 437.7 kV).
- [CA] p.48, p.52: 132/220 kV plant relays at **+14 % / +15 %** (12:33:19.131). A 400 kV line overvoltage trip set at
  **1.2 Un = 480 kV** operated at 485 kV (12:33:23.076). **new**

### 12.3 Voltage control at 12:30 — **adds**
- [CA] p.21: 10 thermal units scheduled for dynamic voltage control (3 nuclear, 7 CCGT). By zone: centre 1, south-west 2,
  south-east 1, north-west 1, north 1, east 2, Levante north 1, Levante south 1. One south-west CCGT failed at 19:47 on
  27 April **(agrees** with [FR] p.~96).
- [CA] p.38–39, p.110: at 12:30, **11 thermal units** with set-point voltage control were online: 4 nuclear, 1 coal,
  6 CCGT, plus hydro. That was the lowest count in 2025; 12 units on 13 days, more on all others. In the south-west only
  a nuclear unit and one CCGT at technical minimum were online.
- [CA] p.111–112: the operator reports **insufficient Q absorption by almost all synchronous units** at some time
  that morning. Above 410–420 kV several units absorbed less than expected, some **generated** Q. **One southern unit's
  Q showed no relation to voltage** (flat). On 22 April, one plant absorbed more than 3× its 12:32 maximum, so the
  capability existed. No numbers are given.
- [CA] p.112: RES and cogeneration must hold PF between 0.98 capacitive and 0.98 inductive (RD 413/2014, hourly).
  Of the 850 largest plants, ≈ 22 % were outside it, mostly at low output (median 11 % of capacity), which the
  committee puts down to evacuation-network capacitance. 20 of 141 transmission-connected consumers and 9.4–21.4 % of
  283 TSO–DSO points were non-compliant.
- [NX] p.4–5: two Nordex wind farms (30 kV and 132 kV PCC) held a **0.98 inductive** PF set-point (Q/P = −0.203) from
  11:00 to 12:33:20. PCC voltage never exceeded **1.07 pu**. No Nordex turbine tripped on overvoltage; they stopped
  after the collapse, mainly on underfrequency. Active power stayed flat through the frequency fall.
  → our ib6 `Kpf` −0.175 lies inside the RD 413/2014 band. It matches an aggregate a little below the nominal 0.98
  (part non-compliance, part capacitive evacuation).
- [CA] p.37 reactor switching, 12:26–12:28: Vitoria 400 REA2, Peñaflor 400 REA1, Guadame 220 REA3, Guadame 400 REA2,
  Morata 400 REA4 connected **(agrees** with Table 2-7's C status). Disconnected after the oscillations:
  Villaviciosa 400 REA1, Guadame 220 REA3, Rueda 400 REA2, Aragón 400 REA1 (12:04–05); Cabra 400, Peñaflor 400,
  Palos 220, Morata 400 (12:17–12:24).
- [CA] p.30, p.33, p.35: lines closed to add damping: Pinar–Tajo, Arcos–Cabra, Pierola–Vandellós (11:08–11:20).
  Five more at 12:07–12:08 and two at 12:21/12:25, names redacted: 10 circuits in total.
- [CA] p.64–65: REE–DSO agreement ranges: normal 380–420 kV, coordination 420–435 kV, exceptional > 435 kV.

### 12.4 System state at 12:30 — **adds / agrees**
- [CA] p.38: demand 25,184 MW, **pumping 2,978 MW**; mix 82 % renewable, 10 % nuclear (4 reactors, 2 at full load:
  agrees with [EXT-5]), 3 % gas (6 plants), 1 % coal, 4 % cogeneration and waste.
- [NX] p.1–2 (from REE real-time data): Spanish generation 32,185 MW; demand 25,184 + pumping 3,030 MW; exports PT 2,652,
  FR 868, MA 782, Andorra 9, **Balearic link 102 MW** (time not stated).
- [CVH] p.4 (REE data, 12:25): FR 778, PT 2,818, MA 745, Andorra 8 MW.
- [CA] p.56: the Balearic HVDC (Morvedre, ≈ VAL bus) carried 96.5 MW and blocked at 12:33:23.520. **new**, small. It is
  not in our demand split; a 100 MW load at VAL would cover it if Fig 2-41's East demand excludes it [inf].
- [CA] p.107: inertia **2.3 s**, excluding interconnections **(agrees** with [FR] Table 2-4, 2.17–2.67 s). RoCoF stayed
  below 1 Hz/s until at least 12:33:19. Tertiary reserve: > 7,000 MW up, > 5,000 MW down.

### 12.5 Interconnection dynamics in the collapse — **new** validation targets (replay gate)
- [CA] p.54, p.105, France:
  - 12:33:19.620: maximum import, net **3,807 MW** (AC **4,609**, HVDC returning **802** to France). Loss of
    synchronism starts here.
  - 20.260: zero crossing.
  - 20.520: maximum export **5,587 MW**.
  - 21.407: Vic–Baixas opened by out-of-step protection after the second slip.
  - 21.535: Hernani–Argia opened (48.458 Hz); AC separation complete.
  - 23.960: HVDC blocked on Santa Llogaia voltage collapse.
  - HVDC in Pmode 1 at 1,000 MW (**2 × 500**) since 12:11. The committee estimates up to 3,000 MW more import if it had
    been in Pmode 3, but judges the outcome unchanged.
- [CA] p.55–56, Morocco: 20.229 Beni Harchane end opens (probably the Moroccan underfrequency relay, as on
  24 July 2021); 20.473 Mellousa 2 opens at **49.314 Hz with Morocco supplying 314 MW to Iberia** (the flow had
  reversed from ≈ 750 MW export).
- [CA] p.57, p.49–51, defence plan:
  - pump shedding: 49.50 Hz crossed at 20.180; 588 MW at the 49.30 Hz step (20.500); **2,037 MW** shed by 20.800 after
    two steps;
  - demand steps crossed: 49.0 Hz at 20.600, 48.8 at 20.760, 48.6 at 21.000, 48.4 at 21.380, 48.2 at 21.820,
    48.0 at 22.040;
  - **1,402.5 MW** of transmission-connected demand shed by the third step.

### 12.6 Oscillations — **adds** (optional small-signal check, not part of the event replay)
- [CVH] p.3: local mode ≈ **0.67 Hz**, marginal damping at Málaga, **negative at Porto**; eigenvectors show Málaga
  against Porto. Inter-area ≈ 0.2 Hz (12:16–12:22) with poor damping.
- [CA] p.75–76: 0.6 Hz mode largest in the south-west: Arroyo de San Serván 32.7 kV, Almaraz 31.2 kV p-p, Carmona.
  Tavel (FR) roughly in antiphase with Carmona. One operator says Porto oscillates more and earlier than Málaga.
- [CA] p.76–80: one Badajoz PV plant oscillated in P and Q (≈ 70 % p-p of its output) from 12:03, and again before
  12:19. A similar 0.8 Hz event occurred in March 2024. Possible forced-oscillation source; unresolved.
- [CA] p.84–86: after each oscillation, embedded inverters dropped out and reconnected after **3–5 min**
  (Majadahonda 220/132 kV load bumps 12:07–12:15 and 12:25–12:29). At 11:00 there was a ≈ 1,200 MW "anomalous"
  demand rise. → supports **latching** the rooftop-PV trip in an 80 s replay (no reconnection).
