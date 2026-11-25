# data/sync_example_record.md — `sync_exciter_governor.pscx` (PLAN F2 / P9)

Source: `C:\Users\Public\Documents\PSCAD\5.1.0\Examples\sync_machines\sync_exciter_governor.pscx`
(80 objects on Main). This record is the specification for `SyncUnit` (PLAN B4). Nothing is to be
"improved" — it is copied.

## Components and ports (measured with `pscad_get_ports`)

### `master:sync_machine` (iid 641688473) — 11 ports

| port | dim | x,y | what it is |
| --- | --- | --- | --- |
| `mvit` | **3** | 18,22 | machine terminal voltage, 3-phase — the electrical connection |
| `NS` | 3 | 18,26 | neutral / stator star point |
| `N` | 1 | 15,26 | neutral (single) |
| `telect` | 1 | 12,26 | **electrical torque (output)** — not a voltage |
| `tmeco` | 1 | 12,28 | mechanical torque (output) |
| `speed` | 1 | 14,30 | rotor speed (output) |
| `tmech` | 1 | 16,30 | mechanical torque (input, from governor/turbine) |
| `efo` | 1 | 12,22 | field voltage (output) |
| `efldn` | 1 | 14,22 | field voltage (input, from exciter) |
| `cfldn` | 1 | 16,22 | field current (input) |
| `Tmstd` | 1 | 18,30 | mechanical torque set-point |

**This settles PLAN A5 item 3:** `telect` is a torque signal, and `mvit` (dim 3) is the terminal
voltage. A previous attempt wired the exciter input to `telect`; that was wrong.

### `master:excac_2016_2` — AC exciter, IEEE type AC (iid 1663074140) — 6 ports

| port | dim | x,y |
| --- | --- | --- |
| `VIT` | **3** | 18,17 (terminal voltage input) |
| `VREF` | 1 | 16,13 |
| `VREFO` | 1 | 14,13 |
| `EFD` | 1 | 14,19 (field voltage to the machine) |
| `EFD0` | 1 | 12,17 |
| `IFD` | 1 | 16,17 (field current, from the machine) |

### `master:hy_gov` — hydro governor (iid 513315416) — 4 ports

| port | dim | x,y |
| --- | --- | --- |
| `W` | 1 | 8,33 (speed input) |
| `WREF` | 1 | 8,39 (speed reference) |
| `ZG` | 1 | 12,35 (gate position) |
| `Z0` | 1 | 12,37 |

### `master:hy_tur` — hydro turbine (iid 221788769) — 5 ports

| port | dim | x,y |
| --- | --- | --- |
| `Win` | 1 | 14,33 |
| `Wref` | 1 | 14,39 |
| `Tm` | 1 | 16,33 (mechanical torque to the machine) |
| `Z` | 1 | 12,35 |
| `ZI` | 1 | 12,37 |

Supporting objects: `master:breaker3`, `master:inductor`, `master:resistor`, `master:ground`,
`master:sandhdefn` (sample-and-hold), two `master:timerdefn`, `master:const`, `master:multimeter`,
six `master:datalabel` + `master:pgb` pairs, `master:tbreakn`.

## Machine parameters (verbatim, `pscad_get_component_parameters`)

Initialisation and start-up — the part the previous attempt got wrong:

| param | value | meaning |
| --- | --- | --- |
| `machsw` | `S2M` | source-to-machine start-up |
| `Enab` | `LRR` | locked-rotor release |
| `Iexc` | `YES` | initialise from the exciter |
| `Igov` | `YES` | initialise from the governor |
| `icTyp` | `POWERS` | initial conditions given as P/Q |
| `P0` / `Q0` | 60 / 0 | initial power |
| `POut` / `QOut` | `POUT` / `QOUT` | output signal names |
| `InExc` / `InGov` | `InitEx` / `InitGv` | exciter/governor initialisation signals |
| `Theta` | `Rang` | rotor angle signal (linked, hence the name) |

Electrical data (this is a **hydro** machine, which is why `Xd` is ~1.0):

| param | value | param | value |
| --- | --- | --- | --- |
| `MVA` | 300 | `H` | 3.117 |
| `VbaseLL` | 18 kV | `D` | 0 |
| `Xd` | 1.014 | `Xq` | 0.77 |
| `Xd_` | 0.314 | `Xq_` | 0.228 |
| `Xd__` | 0.28 | `Xq__` | 0.375 |
| `Tdo_` | 6.55 s | `Tqo_` | 0.85 s |
| `Tdo__` | 0.039 s | `Tqo__` | 0.071 s |
| `Ra` | 0.0051716 | `Xp` | 0.163 |
| `Rs1` | 0.002 | `XS1` | 0.14 |
| `XMD0` | 1.66 | `XMQ` | 1.58 |
| `RNeut` | 10000 | `XNeut` | 0 |
| `MSat` | `DISABLED` | `CfRa` | `RESISTANCE` |
| `Term` | `VT_IT` | `OMO` | 376.992 |

## Consequences for `SyncUnit`

1. **CORRECTED 2026-11-16 (Session 5), from the definition XML in `master.pslx`:** `mvit` is a
   *Transfer / Output* port (`mode="Output"`, condition `Term==3`): it is the **terminal-voltage
   measurement sent to the exciter**, not the electrical connection. The machine's **3-phase electrical
   terminal is `NS`** (`<port name="NS" dim="3" mode="Electrical" cond=(View==1)>`), and `N`
   (`mode="Electrical"`, `cond=(Neut==1)`) is the external neutral; with `Neut=DISABLE` the neutral is
   an internal ground port. So `SyncUnit` exposes **`NS`** as its `T` port and leaves `mvit` wired to
   the exciter's `VIT`. The example's 3.17 Ω resistor + 8.42 mH inductor on `NS` is its **load**.
2. The exciter takes **`VIT`** (3-phase terminal voltage) and **`IFD`** (field current); it returns
   **`EFD`** to the machine's `efldn`. Wiring the exciter to `telect` is the error to avoid.
3. The governor takes `W` (speed) and returns `ZG`/`Z0`; the turbine takes `Z`/`ZI` and returns `Tm`
   to the machine's `tmech`.
4. Start-up is `machsw=S2M` with `Enab=LRR`, `Iexc=YES`, `Igov=YES`, initial P/Q from the load-flow
   solution — exactly the sequence PLAN B4 requires, and it must be reproduced, not reinvented.
5. The example machine is a 300 MVA hydro unit with `Xd = 1.014`. PLAN B4 wants realistic
   reactances and warns explicitly against cutting `Xd` to make the machine look stiff.
6. **Per-unit base traps (measured 2026-11-16, Session 6/7).** Two fields do not follow the rating
   and will corrupt every `SyncUnit` instance if they are left alone:
   - **`Vbase` is the rated voltage in the machine's own pu system and the relation is
     `V_rated(L-N) = Vbase·√3/2`, i.e. `Vbase = 2·V_LL/3`** (measured: with `Vbase = V_LL/√3` the
     AVR regulated the machine to 0.866 pu and it absorbed ≈200 Mvar; with `Vbase = 2·V_LL/3` the AVR
     saw 1.0 pu at the correct 400 kV). PSCAD's own example carries `VbaseLL = 18 kV` with
     `Vbase = 7.967 kV`, consistent with `2·13.8/3 = 9.2` for its true 13.8 kV rating only
     approximately — verify per unit. Rule: 400 kV → `Vbase = 266.67 kV`; 18 kV → `Vbase = 12.00 kV`.
   - `Ibase = MVA/(√3·V_LL)` (300 MVA at 400 kV → 433.0 A; at 18 kV → 9.62 kA).
   - `source3` impedance fields need **units**: `R1p = "9.3 [ohm]"`, `L1p = "0.34 [H]"`,
     `Vm = "400 [kV]"`. A bare float is stored dimensionless (the read-back loses the unit) and the
     source no longer behaves as that impedance — measured as flows scaling exactly 10× when the
     impedance was changed 10×.
8. **`mvit` carries the dq0 components**, not three phase RMS values (measured at no load:
   `(0.995, 0.079, −0.009)` = `Vq ≈ 1`, `Vd ≈ 0`). A `voltmetergnd` on the terminal reports
   **instantaneous phase-to-neutral kV** (1.0 pu on a 400 kV bus = ±326.6 kV peak), while a
   `source3`'s `V` output reports p.u.
9. Measured on the example itself: its machine runs at **1.0 pu of its true 13.8 kV rating**
   (13.78 kV) and its `InitEx` is **1 from 0.3 s onwards** — a steady `InitEx = 1` does *not* freeze
   the exciter (the field voltage still moves 1.11 → 1.95 at 2 s). Its field current is **positive**
   (1.578 pu); a bench whose `IF` goes negative is under-excited and will not regulate.

### Bench started — first finding

`C:\PSCAD_work\sync_bus.pscx` created (canvas 100×100) with `sync_machine`, `excac_2016_2`,
`hy_gov`, `hy_tur` placed. Ports as delivered by the **default** machine configuration:

```
machine : telect, speed, tmeco, cfldn, efldn, tmech, NS, conspd, N      (9 ports)
example : telect, speed, tmeco, cfldn, efldn, tmech, NS, Tmstd, N, mvit, efo  (11 ports)
```

**`mvit` and `efo` are missing and `conspd` appears instead.** So a freshly placed `sync_machine`
does *not* expose the three-phase terminal port — the example's configuration (`Term = VT_IT`,
`View`, `icTyp = POWERS`, `machsw = S2M`, `Enab = LRR`, `Iexc/Igov = YES`) is what makes `mvit`
appear. The example's parameters must be applied **before** any wiring, otherwise the exciter has no
terminal-voltage input to connect to — which is precisely how the earlier attempt ended up feeding the
exciter from `telect`.

Resolved: `conspd` is the default speed-constant port in place of `mvit`/`Tmstd`.

### Bench machine configured — `mvit` is back

Applying the example's configuration to the bench machine (`Term=VT_IT`, `icTyp=POWERS`,
`machsw=S2M`, `Enab=LRR`, `Iexc=YES`, `Igov=YES`, `MVA=300`, `VbaseLL=18`) was accepted **by label**
(no index needed here) and read back identical. Ports then became:

```
telect, speed, tmeco, efo, mvit, cfldn, efldn, tmech, Tmstd, NS, conspd, N     (12)
```

`mvit` (3-phase terminal voltage), `efo` (field voltage output) and `Tmstd` (mechanical torque
set-point) all appeared. The one port the example does not show is `conspd` — a mechanical
speed-constant port, present because the governor configuration on the bench is still default; it is
expected to disappear (or stay unused) once `hy_gov`'s parameters are applied.

**Order of work for the bench, now established:** configure every component from the record *before*
wiring, because the port list itself depends on the configuration.

## Exciter, governor, turbine parameters (from the example)

`excac_2016_2` (IEEE type AC): `TYPE`, `INIT`, `OVR`, `RC`, `XC`, `TR`, `STAB=NO`, `VFMX`, `VEMN`,
`TE=0.8`, `KE=1`, `KC`, `KD`, `SE1/VE1/SE2/VE2`, `UEL`, `OEL`, `SCL`, `UELTo`, and per-stage gains
`KA_1=400, TA_1=0.02, KF_1=0.03, TF_1=1` with a second stage `KA_2=400, TA_2=0.01, KF_2=0.03`.

`hy_gov` (hydro governor): `INIT=InitGv`, permanent droop `RP=0.04`, gate limits
`MGOR=MGCR=0.16`, `DB`, and the two-stage time constants `TP_1=0.05`, `TG_1=0.2`, `RT_1=0.4`,
`TR_1=5`, `KP_2=3`, `TA_2=0.05`.

`hy_tur` (hydro turbine): `INIT`, `WC`, `ST`, `JD`, `RV`, `HR`, `PR`, `ZR`, `QG`, `QNL`, `ZNL`,
`PM0`, `HI`, `TW_1`.

These are the numbers `SyncUnit` must carry. `RP=0.04` (4 % droop) and `KA=400` with `TA=0.02` are the
two that decide whether the unit looks like a stiff voltage source or a realistic one — PLAN B4's
`Vctl` switch changes the *outer* behaviour, not these inner loops.

### Parameters applied to the bench — verified by read-back

Exciter: `TE=0.8, KE=1, KA_1=400, TA_1=0.02, STAB=NO` — read back identical.
Governor: `RP=0.04, TP_1=0.05, TG_1=0.2, TR_1=5, KP_2=3` — read back identical.
Machine ports still 12 (`mvit` present). `conspd` persists because `hy_tur` is still at defaults; it is
a mechanical port and does not block the electrical wiring.

### Wiring pass 1 — what the first build demanded

Three wires placed: `mvit`→`VIT`, `EFD`→`efldn`, `cfldn`→`IFD`. The build then reported:

```
Input port 'Win'   floating
Input port 'Wref'  floating
Input port 'Z'     floating
Input parameter 'S2M' floating. The expected signal source 'machsw' is undefined.
Input parameter 'LRR' floating. The expected signal source 'Enab'  is undefined.
```

Two distinct requirements, both of which the example satisfies with extra objects:

1. **`machsw=S2M` and `Enab=LRR` are signal *sources*, not just settings.** They expect named signals
   `S2M` and `LRR` to exist on the canvas — the example supplies them with `master:const` blocks. So
   the start-up sequence is driven by signals, which is why the example carries `const`, `timerdefn`,
   `sandhdefn` and `tbreakn`.
2. **The turbine needs its inputs wired**: `Win`/`Wref`/`Z` from the governor's `ZG`/`Z0` and the
   speed reference.

Nothing here is a parameter error — it is the bench being incomplete, exactly as expected at this
stage.

### Wiring pass 2 — how the start-up signals actually attach

Three `const` blocks were added and named `S2M`, `LRR`, `WREF`. The build still reports

```
Input parameter 'S2M' floating. The expected signal source 'machsw' is undefined.
Input parameter 'LRR' floating. The expected signal source 'Enab'  is undefined.
```

So **naming a `const` is not enough**: `machsw`/`Enab` are data *parameters* that link to a signal
**by name**, and the name has to be published by a `datalabel` (the same convention used for every
measurement channel — meter `Name` → `datalabel` with that `Name` → consumer). The example's extra
objects are exactly that: `const` → `datalabel` → the machine's parameter, plus `timerdefn`/`sandhdefn`
for the timing of the source-to-machine transfer and rotor release.

Governor `Z0` also appeared as floating once the turbine link was examined, confirming that
`ZG`/`Z0` → `Z`/`ZI` are wired pairs, not independent inputs.

**Bench wiring still to do:** `const`→`datalabel` for `S2M`, `LRR`, `WREF`; governor `ZG`→turbine `Z`,
`Z0`→`ZI`, speed `W`→`Win`, `WREF`→`Wref`; machine `tmech`→turbine `Tm`; then the source and infinite
bus.

### Mechanism confirmed — `const` → `datalabel` → parameter

Wiring the `S2M` const to a `datalabel` named `S2M` **cleared the error**:
`Input parameter 'S2M' floating` disappeared from the build, leaving only `LRR` and the four turbine
inputs. So the binding rule is proven:

> A data parameter such as `machsw` binds to a signal **by name**, and that name must be published by
> a `datalabel` fed from the producing component. A `const` named `S2M` alone does nothing; the
> `datalabel` is what makes the name visible.

This is the same convention as the measurement channels (`meter Name` → `datalabel` → `pgb`) and it is
now the established way to drive `machsw`, `Enab`, `Iexc`, `Igov` and the `Vctl`/`Qmode` switches of
PLAN B3/B4.

### Wiring pass 3 — five errors left

Publishing `LRR` and `WREF`, and wiring `ZG`→`Z`, `Z0`→`ZI`, `speed`→`W`, `speed`→`Win`,
`tmech`→`Tm`, cleared every turbine and governor port error and both start-up parameters. What remains:

```
conspd  floating     machine mechanical speed-constant input
EFD0    floating     exciter initial field voltage
VREF    floating     exciter voltage reference
WREF    floating     governor speed reference (published, not yet wired to the port)
Wref    floating     turbine speed reference (same)
```

So the bench is five connections from complete: `WREF` datalabel → governor `WREF` and turbine `Wref`,
plus `const`→`datalabel` pairs for `VREF` and `EFD0` (the exciter's reference and initial field), and a
value on `conspd`.

### Wiring pass 4 — final error list at handover

`VREF`/`EFD0` consts were removed (their auto-routed wires had clipped a 3-phase node, producing the
`dimension mismatch -> 3 != 1`). The build now reports:

```
Signal 'RT_2' source contention at component [sync_machine] 'SyncMachine'
Signal 'RT_2' source contention at component [hy_tur] ''
Input port 'conspd' floating
Input port 'VREF'   floating
```

`RT_2` contention means the machine `speed` output is driving two consumers that both claim the same
link — I wired `speed`→governor `W` **and** `speed`→turbine `Win`; in the example `Win` is fed from the
governor side, not directly from speed. Fix: break `speed`→`Win` and feed `Win` from the governor's
output, then re-add `VREF`/`EFD0` consts with explicit wire vertices, and give `conspd` a value.









