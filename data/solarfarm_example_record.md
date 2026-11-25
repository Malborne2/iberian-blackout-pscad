# Example record: `SimpleSolarFarm.pscx`

Source of every line below: the shipped `.pscx` itself (read-only, parsed offline).
Coordinates are PSCAD grid units. This is the specification to copy, not to improve
(PLAN F2 Stage 3, skill P9).

## Canvas `PIwithFreeze_1`

Module ports: In(dim 1, Input), Out(dim 1, Output), Rst(dim 1, Input)

| component | type | at | parameters |
| --- | --- | --- | --- |
| master:import `In` | | (16,15) |  |
| master:import `Rst` | | (29,27) |  |
| master:export `Out` | | (46,15) |  |
| master:hardlimit  | | (39,15) | `UL`=MaxOut, `LL`=MinOut, `COM`=Hard_Limit, `Dim`=1 |
| master:sumjct  | | (35,15) | `DPath`=1, `B`=1, `D`=1, `Dim`=1 |
| master:gain  | | (31,15) | `G`=Kp, `COM`=Gain, `Dim`=1, `DPath`=1 |
| master:integral  | | (31,23) | `Reset`=1, `T`=Ti, `Yo`=0.0, `YRst`=0.0, `YHi`=MaxOut, `YLo`=MinOut, `Dim`=1 |
| master:select  | | (26,23) | `A`=1, `DPath`=1, `COM`=Selector, `Dim`=1 |
| master:const  | | (22,21) | `Dim`=1 |
| master:import `Kp` | | (11,3) |  |
| master:import `Ti` | | (11,4) |  |
| master:import `MaxOut` | | (11,7) |  |
| master:import `MinOut` | | (11,8) |  |
| master:logic_mult  | | (24,27) | `Type`=1, `Num_in`=2, `disnum`=1 |
| master:datalabel `MaxOut` | | (11,30) | `datatype`=2, `index`=1 |
| master:datalabel `MinOut` | | (11,32) | `datatype`=2, `index`=1 |
| master:mult  | | (25,15) | `DPath`=1, `Dim`=1 |
| master:datalabel `Rst` | | (18,12) | `datatype`=2, `index`=1 |
| master:inv  | | (19,12) | `const`=false |
| master:compar  | | (14,28) | `OPos`=1, `ONeg`=1, `OHi`=1, `conv`=1 |
| master:compar  | | (14,32) | `OPos`=1, `ONeg`=1, `OHi`=1, `conv`=1 |

Wiring (absolute endpoints, intermediate vertices included):

- (41,15) -> (44,15)
- (26,27) -> (26,25)
- (31,27) -> (31,25)
- (28,23) -> (29,23)
- (18,15) -> (23,15)
- (24,23) -> (19,23) -> (19,15)
- (33,23) -> (35,23) -> (35,17)
- (11,30) -> (14,30)
- (18,28) -> (18,26) -> (22,26)
- (7,34) -> (14,34)
- (11,32) -> (14,32)
- (27,15) -> (29,15)
- (21,12) -> (25,12) -> (25,13)
- (37,15) -> (37,36) -> (7,36) -> (7,28) -> (14,28)
- (18,12) -> (19,12)
- (22,28) -> (20,28) -> (20,32) -> (18,32)

## Canvas `DC_DC_Converter`

Module ports: HDCP(dim 1, Electrical), DCN(dim 1, Electrical), LDCP(dim 1, Electrical), DCN(dim 1, Electrical)

| component | type | at | parameters |
| --- | --- | --- | --- |
| master:xnode `HDCP` | | (28,6) |  |
| master:xnode `DCN` | | (24,14) |  |
| master:xnode `LDCP` | | (3,6) |  |
| master:datalabel `GBoost` | | (17,10) | `datatype`=2, `index`=1 |
| master:inductor  | | (16,6) | `L`=100 [uH] |
| master:ammeter `IH` | | (23,6) |  |
| master:capacitor  | | (10,8) | `C`=1000 [uF] |
| master:voltmeter `VH` | | (26,8) |  |
| master:datalabel `VH` | | (52,8) | `datatype`=2, `index`=1 |
| master:datalabel `VL` | | (52,10) | `datatype`=2, `index`=1 |
| master:datalabel `IH` | | (44,9) | `datatype`=2, `index`=1 |
| master:datalabel `IL` | | (51,14) | `datatype`=2, `index`=1 |
| master:pgb `VH` | | (53,8) | `Display`=1, `Scale`=1.0, `Units`=kV, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:pgb `VL` | | (53,10) | `Display`=1, `Scale`=1.0, `Units`=kV, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:pgb `I dc link` | | (47,9) | `Display`=1, `Scale`=1.0, `Units`=kA, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:pgb `IL` | | (53,14) | `Display`=1, `Scale`=1.0, `Units`=kA, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:sig_gen  | | (12,42) | `Max`=1.01 |
| master:const  | | (8,42) | `Value`=5000, `Dim`=1 |
| master:datalabel `carr` | | (15,42) | `datatype`=2, `index`=1 |
| master:fp_int  | | (26,46) | `Type`=1, `Blck`=1, `max`=360.0, `min`=0.0, `PTime`=0.005 [s] |
| master:datalabel `carr` | | (18,42) | `datatype`=2, `index`=1 |
| master:datalabel `Ref_Boost` | | (18,44) | `datatype`=2, `index`=1 |
| master:datalabel `GBoost` | | (26,50) | `datatype`=2, `index`=1 |
| master:datalabel `Pref` | | (17,21) | `datatype`=2, `index`=1 |
| master:sumjct  | | (23,21) | `DPath`=1, `D`=1, `Dim`=1 |
| master:datalabel `Ref_Boost` | | (34,21) | `datatype`=2, `index`=1 |
| master:datalabel `KpBoost` | | (61,12) | `datatype`=2, `index`=1 |
| master:datalabel `TiBoost` | | (61,15) | `datatype`=2, `index`=1 |
| master:var `KpBoost` | | (57,12) | `Display`=1, `Max`=10, `Min`=0.0, `Value`=1.0, `Collect`=1 |
| master:var `TiBoost` | | (57,15) | `Display`=1, `Max`=10, `Min`=0.0, `Value`=0.1, `Collect`=1 |
| master:pgb `Dboost` | | (53,16) | `Scale`=1.0, `Units`=%, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datalabel `DlimBst` | | (61,18) | `datatype`=2, `index`=1 |
| master:peswitch  | | (20,6) | `L`=DH, `INTR`=1, `RON`=1e-4 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.2e-3 [kV], `EBO`=12 [kV], `Erw`=12 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:voltmeter `VL` | | (13,8) |  |
| master:ammeter `IL` | | (4,6) |  |
| master:pgb `Dlim Bst` | | (53,18) | `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:pin  | | (17,21) |  |
| master:resistor  | | (19,13) | `R`=1.0 [Mohm] |
| master:ground  | | (19,15) |  |
| master:import `OnOff` | | (21,32) |  |
| master:peswitch  | | (19,8) | `L`=Q, `Type`=3, `INTR`=1, `RON`=1e-4 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=17 [kV], `Erw`=17 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:var `DmaxBoost` | | (57,18) | `Display`=1, `Max`=0.7, `Min`=0.0, `Value`=0.7, `Collect`=1 |
| master:datalabel `VL` | | (13,25) | `datatype`=2, `index`=1 |
| master:datalabel `IL` | | (13,27) | `datatype`=2, `index`=1 |
| master:mult  | | (15,25) | `DPath`=1, `Dim`=1 |
| master:datalabel `P_PV` | | (23,25) | `datatype`=2, `index`=1 |
| master:annotation  | | (24,27) | `AL2`=Enable Boost |
| master:logic_mult  | | (26,31) | `Num_in`=2, `disnum`=1 |
| master:datalabel `EnableBoost` | | (30,31) | `datatype`=2, `index`=1 |
| master:annotation  | | (15,33) | `AL1`=Pref < PLim  =>, `AL2`=Enable Boost |
| master:inv  | | (29,26) | `const`=false |
| master:inductor  | | (9,6) | `L`=100 [uH] |
| master:datalabel `Pref` | | (52,12) | `datatype`=2, `index`=1 |
| master:import `Plim` | | (11,32) |  |
| master:pgb `Pref` | | (53,12) | `Display`=1, `Scale`=1, `Units`=MW, `Max`=2.0, `Min`=-2.0, `enab`=1 |
| master:import `Pref` | | (11,30) |  |
| master:datalabel `Ref_Boost` | | (51,16) | `datatype`=2, `index`=1 |
| master:realpole  | | (20,25) | `COM`=Real_Pole, `YO`=0.0, `Dim`=1, `G`=1.0, `T`=0.005 [s], `Max`=10.0, `Min`=-10.0 |
| master:datalabel `DlimBst` | | (51,18) | `datatype`=2, `index`=1 |
| master:annotation  | | (10,27) | `AL2`=maximum power in kW |
| master:datalabel `PLim` | | (51,20) | `datatype`=2, `index`=1 |
| master:pgb `P_Lim` | | (53,20) | `Scale`=1.0, `Units`=MW, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datalabel `EnableBoost` | | (26,40) | `datatype`=2, `index`=1 |
| SimpleSolarFarm:PIwithFreeze_1  | | (29,21) | `Kp`=KpBoost, `Ti`=TiBoost, `MaxOut`=DLimBst |
| master:pgb `P_PV` | | (53,22) | `Scale`=1.0, `Units`=MW, `Min`=-2.0, `Max`=2.0, `UseSignalName`=1, `enab`=1 |
| master:datalabel `P_PV` | | (51,22) | `datatype`=2, `index`=1 |
| master:voltmeter `Vswitch` | | (21,8) |  |
| master:datalabel `Vswitch` | | (57,22) | `datatype`=2, `index`=1 |
| master:pgb `Vswitch` | | (59,22) | `Scale`=1.0, `Units`=kV, `Min`=-2.0, `Max`=2.0, `UseSignalName`=1, `enab`=1 |
| master:compar  | | (14,30) | `OPos`=1, `ONeg`=1, `OLo`=1 |

Wiring (absolute endpoints, intermediate vertices included):

- (21,10) -> (19,10)
- (21,8) -> (19,8)
- (22,6) -> (23,6)
- (20,6) -> (16,6)
- (19,8) -> (19,6)
- (26,12) -> (12,12)
- (14,6) -> (9,6)
- (13,10) -> (13,12)
- (19,10) -> (19,12)
- (10,8) -> (10,6)
- (28,6) -> (25,6)
- (26,8) -> (26,6)
- (26,10) -> (26,12)
- (14,42) -> (15,42)
- (18,44) -> (24,44)
- (18,42) -> (24,42)
- (24,44) -> (24,46)
- (24,48) -> (23,48) -> (23,42)
- (17,21) -> (21,21)
- (31,21) -> (34,21)
- (59,12) -> (61,12)
- (59,15) -> (61,15)
- (4,6) -> (3,6)
- (13,8) -> (13,6)
- (12,12) -> (10,12) -> (10,10)
- (59,18) -> (61,18)
- (24,14) -> (24,12)
- (25,21) -> (27,21)
- (29,24) -> (29,23)
- (13,27) -> (15,27)
- (17,25) -> (18,25)
- (13,30) -> (14,30)
- (18,30) -> (24,30)
- (23,32) -> (24,32)
- (28,31) -> (30,31)
- (6,6) -> (7,6)
- (52,12) -> (53,12)
- (53,14) -> (51,14)
- (53,8) -> (52,8)
- (53,10) -> (52,10)
- (53,16) -> (51,16)
- (53,18) -> (51,18)
- (22,25) -> (23,25) -> (23,23)
- (53,20) -> (51,20)
- (30,31) -> (29,31) -> (29,26)
- (19,13) -> (19,12)
- (53,22) -> (51,22)
- (59,22) -> (57,22)
- (47,9) -> (44,9)
- (14,32) -> (13,32)

## Canvas `Simple_PPC`

Module ports: PFref(dim 1, Input), Qref(dim 1, Input), Pref(dim 1, Input), Vref(dim 1, Input), Qpu(dim 1, Output), Ppu(dim 1, Output), Qmeas(dim 1, Input), Pmeas(dim 1, Input), Vmeas(dim 1, Input), DBLK(dim 1, Input)

| component | type | at | parameters |
| --- | --- | --- | --- |
| master:import `Vmeas` | | (17,21) |  |
| master:import `Pmeas` | | (17,23) |  |
| master:import `Vref` | | (4,21) |  |
| master:import `Pref` | | (4,23) |  |
| master:import `Qref` | | (4,25) |  |
| master:import `PFref` | | (3,30) |  |
| master:import `DBLK` | | (5,13) |  |
| master:import `Qmeas` | | (17,25) |  |
| master:export `Ppu` | | (48,8) |  |
| master:export `Qpu` | | (52,23) |  |
| master:import `Scale` | | (13,8) |  |
| master:import `Sbase` | | (11,6) |  |
| master:import `Ti_V` | | (5,4) |  |
| master:import `Kp_V` | | (5,5) |  |
| master:import `Kp_PF` | | (5,7) |  |
| master:import `Ti_PF` | | (5,6) |  |
| master:import `Kp_Q` | | (5,9) |  |
| master:import `Ti_Q` | | (5,8) |  |
| master:import `Kp_P` | | (5,11) |  |
| master:import `Ti_P` | | (5,10) |  |
| master:mult  | | (15,6) | `DPath`=1, `Dim`=1 |
| master:datalabel `Srate` | | (18,6) | `datatype`=2, `index`=1 |
| SimpleSolarFarm:PI_AntiWindUp  | | (44,8) | `Kp`=Kp_P, `Ti`=Ti_P, `Kaw`=1, `MaxOut`=Pmax, `MinOut`=Pmin |
| master:sumjct  | | (40,8) | `DPath`=1, `D`=1, `Dim`=1 |
| master:dynamic_datatap  | | (49,23) | `Type`=2, `Dim`=1 |
| master:div  | | (19,4) | `Dim`=1, `DPath`=1 |
| master:const  | | (15,4) | `Value`=1.0, `Dim`=1 |
| master:datalabel `inv_Srate` | | (22,4) | `datatype`=2, `index`=1 |
| master:gain  | | (21,23) | `G`=inv_Srate, `COM`=Per-Unitize Active Power, `Dim`=1, `DPath`=1 |
| master:gain  | | (21,25) | `G`=inv_Srate, `COM`=Per-Unitize Reactive Power, `Dim`=1, `DPath`=1 |
| master:datalabel `Ppu_meas` | | (25,23) | `datatype`=2, `index`=1 |
| master:datalabel `Qpu_meas` | | (25,25) | `datatype`=2, `index`=1 |
| master:datalabel `Vpu_meas` | | (25,21) | `datatype`=2, `index`=1 |
| master:datalabel `Vpu_ref` | | (12,21) | `datatype`=2, `index`=1 |
| master:datalabel `Qpu_ref` | | (12,25) | `datatype`=2, `index`=1 |
| master:datalabel `Ppu_ref` | | (12,23) | `datatype`=2, `index`=1 |
| master:gain  | | (8,25) | `G`=inv_Srate, `COM`=Per-Unitize Reactive Power, `Dim`=1, `DPath`=1 |
| master:gain  | | (8,23) | `G`=inv_Srate, `COM`=Per-Unitize Active Power, `Dim`=1, `DPath`=1 |
| master:abs  | | (8,30) | `Dim`=1, `DPath`=1 |
| master:mult  | | (18,28) | `DPath`=1, `Dim`=1 |
| master:sign  | | (8,28) | `COM`=Sign Function, `Dim`=1, `const`=false |
| master:trig  | | (16,30) | `Type`=3, `COM`=Trig-Func, `Dim`=1, `const`=false |
| master:trig  | | (12,30) | `Type`=-2, `COM`=Trig-Func, `Dim`=1, `const`=false |
| master:datalabel `Q_over_P` | | (22,28) | `datatype`=2, `index`=1 |
| master:datalabel `Vpu_ref` | | (36,14) | `datatype`=2, `index`=1 |
| master:datalabel `Vpu_meas` | | (36,12) | `datatype`=2, `index`=1 |
| master:sumjct  | | (40,14) | `DPath`=1, `D`=1, `Dim`=1 |
| SimpleSolarFarm:PI_AntiWindUp  | | (44,14) | `Kp`=Kp_V, `Ti`=Ti_V, `Kaw`=1, `MaxOut`=Qmax, `MinOut`=Qmin |
| master:datalabel `VRT` | | (44,10) | `datatype`=2, `index`=1 |
| SimpleSolarFarm:PI_AntiWindUp  | | (44,20) | `Kp`=Kp_PF, `Ti`=Ti_PF, `Kaw`=1, `MaxOut`=Qmax, `MinOut`=Qmin |
| master:sumjct  | | (40,20) | `DPath`=1, `D`=1, `Dim`=1 |
| SimpleSolarFarm:PI_AntiWindUp  | | (44,26) | `Kp`=Kp_Q, `Ti`=Ti_Q, `Kaw`=1, `MaxOut`=Qmax, `MinOut`=Qmin |
| master:sumjct  | | (40,26) | `DPath`=1, `D`=1, `Dim`=1 |
| master:datalabel `Qpu_ref` | | (36,26) | `datatype`=2, `index`=1 |
| master:datalabel `Ppu_ref` | | (36,8) | `datatype`=2, `index`=1 |
| master:datalabel `Qpu_meas` | | (36,24) | `datatype`=2, `index`=1 |
| master:datalabel `Ppu_meas` | | (36,6) | `datatype`=2, `index`=1 |
| master:gain  | | (36,20) | `G`=Q_over_P, `Dim`=1, `DPath`=1 |
| master:datalabel `Ppu_meas` | | (32,20) | `datatype`=2, `index`=1 |
| master:datalabel `Qpu_meas` | | (36,18) | `datatype`=2, `index`=1 |
| master:datamerge  | | (48,23) | `N`=3, `Type`=2, `Disp`=1, `Dim1`=1, `Dim2`=1, `Dim3`=1, `Dim4`=1, `Dim5`=1, `Dim6`=1, `Dim7`=1, `Dim8`=1, `Dim9`=1, `Dim10`=1, `Dim11`=1, `Dim12`=1 |
| master:import `con_mode` | | (49,26) |  |
| master:import `HVRT` | | (5,15) |  |
| master:import `LVRT` | | (5,16) |  |
| master:datalabel `VRT` | | (44,16) | `datatype`=2, `index`=1 |
| master:datalabel `VRT` | | (44,22) | `datatype`=2, `index`=1 |
| master:datalabel `VRT` | | (44,28) | `datatype`=2, `index`=1 |
| master:datalabel `Vpu_meas` | | (66,9) | `datatype`=2, `index`=1 |
| master:compare  | | (70,7) | `X`=HVRT, `OH`=1, `Dim`=1, `conv`=1 |
| master:compare  | | (70,11) | `X`=LVRT, `OL`=1, `Dim`=1, `conv`=1 |
| master:logic_mult  | | (74,9) | `Type`=1, `Num_in`=2 |
| master:datalabel `VRT` | | (76,9) | `datatype`=2, `index`=1 |
| master:unity  | | (8,21) | `IType`=2, `OType`=2, `Dim`=1, `const`=false |
| master:import `Pmax` | | (14,13) |  |
| master:import `Pmin` | | (14,14) |  |
| master:import `Qmax` | | (14,15) |  |
| master:import `Qmin` | | (14,16) |  |
| master:unity  | | (21,21) | `IType`=2, `OType`=2, `Dim`=1, `const`=false |
| master:inv  | | (7,13) | `const`=false |
| master:datalabel `RST` | | (9,13) | `datatype`=2, `index`=1 |
| master:datalabel `RST` | | (44,6) | `datatype`=2, `index`=1 |
| master:datalabel `RST` | | (44,12) | `datatype`=2, `index`=1 |
| master:datalabel `RST` | | (44,18) | `datatype`=2, `index`=1 |
| master:datalabel `RST` | | (44,24) | `datatype`=2, `index`=1 |

Wiring (absolute endpoints, intermediate vertices included):

- (17,6) -> (19,6)
- (21,4) -> (22,4)
- (23,23) -> (25,23)
- (23,25) -> (25,25)
- (21,21) -> (25,21)
- (8,21) -> (12,21)
- (10,25) -> (12,25)
- (10,23) -> (12,23)
- (6,28) -> (6,30)
- (10,28) -> (16,28)
- (22,28) -> (20,28)
- (5,30) -> (6,30)
- (38,8) -> (36,8)
- (40,6) -> (36,6)
- (40,12) -> (36,12)
- (38,14) -> (36,14)
- (40,18) -> (36,18)
- (38,26) -> (36,26)
- (40,24) -> (36,24)
- (32,20) -> (34,20)
- (46,14) -> (47,14) -> (47,19)
- (46,20) -> (47,20)
- (46,26) -> (47,26) -> (47,21)
- (68,7) -> (68,11)
- (68,9) -> (66,9)
- (72,7) -> (72,8)
- (72,10) -> (72,11)

## Canvas `PI_AntiWindUp`

Module ports: In(dim 1, Input), Out(dim 1, Output), frz(dim 1, Input), Rst(dim 1, Input)

| component | type | at | parameters |
| --- | --- | --- | --- |
| master:import `In` | | (16,15) |  |
| master:import `Rst` | | (42,29) |  |
| master:export `Out` | | (61,15) |  |
| master:hardlimit  | | (50,15) | `UL`=MaxOut, `LL`=MinOut, `COM`=Hard_Limit, `Dim`=1 |
| master:sumjct  | | (46,15) | `DPath`=1, `B`=1, `D`=1, `Dim`=1 |
| master:gain  | | (42,15) | `G`=Kp, `COM`=Gain, `Dim`=1, `DPath`=1 |
| master:integral  | | (44,25) | `Reset`=1, `T`=Ti, `Yo`=0.0, `YRst`=0.0, `YHi`=MaxOut, `YLo`=MinOut, `Dim`=1 |
| master:import `Kp` | | (11,3) |  |
| master:import `Ti` | | (11,4) |  |
| master:import `MaxOut` | | (11,7) |  |
| master:import `MinOut` | | (11,8) |  |
| master:mult  | | (25,15) | `DPath`=1, `Dim`=1 |
| master:datalabel `Rst` | | (18,12) | `datatype`=2, `index`=1 |
| master:inv  | | (19,12) | `const`=false |
| master:sumjct  | | (48,33) | `DPath`=1, `D`=1, `Dim`=1 |
| master:zminusone `Feedback Loop XYZ` | | (44,33) | `Type`=2, `Dim`=1, `InitR`=0.0, `InitC`=(0.0, 0.0) |
| master:sumjct  | | (27,25) | `DPath`=1, `B`=1, `D`=1, `Dim`=1 |
| master:import `frz` | | (11,10) |  |
| master:select  | | (38,25) | `A`=1, `DPath`=1, `COM`=Selector, `Dim`=1 |
| master:datalabel `frz` | | (38,29) | `datatype`=2, `index`=1 |
| master:const  | | (34,23) | `Value`=0.0, `Dim`=1 |
| master:import `Kaw` | | (11,5) |  |
| master:gain  | | (40,33) | `G`=Kaw, `COM`=Gain, `Dim`=1, `DPath`=1 |

Wiring (absolute endpoints, intermediate vertices included):

- (52,15) -> (59,15)
- (44,29) -> (44,27)
- (29,25) -> (36,25)
- (18,15) -> (23,15)
- (25,25) -> (19,25) -> (19,15)
- (46,25) -> (46,17)
- (27,15) -> (40,15)
- (21,12) -> (25,12) -> (25,13)
- (18,12) -> (19,12)
- (38,33) -> (27,33) -> (27,27)
- (58,33) -> (58,15)
- (50,33) -> (58,33)
- (48,31) -> (48,15)
- (40,25) -> (42,25)
- (38,27) -> (38,29)

## Canvas `Load`

Module ports: abc(dim 3, Electrical)

| component | type | at | parameters |
| --- | --- | --- | --- |
| master:xnode `abc` | | (39,11) |  |
| master:import `VLoad` | | (4,2) |  |
| master:import `Freq` | | (4,3) |  |
| master:import `PLoad` | | (4,5) |  |
| master:import `QLoad` | | (4,6) |  |
| master:varrlc  | | (28,15) | `R`=Rload, `L`=1.0 [H], `C`=1.0 [uF], `E`=0.0 [kV] |
| master:datalabel `VLoad` | | (5,16) | `datatype`=2, `index`=1 |
| master:square  | | (8,16) | `Dim`=1, `DPath`=1 |
| master:div  | | (12,16) | `Dim`=1, `DPath`=1 |
| master:datalabel `PLoad` | | (5,19) | `datatype`=2, `index`=1 |
| master:hardlimit  | | (8,19) | `UL`=1000, `LL`=1e-8, `COM`=Hard_Limit, `Dim`=1 |
| master:hardlimit  | | (16,16) | `UL`=1e6, `LL`=1e-8, `COM`=Hard_Limit, `Dim`=1 |
| master:datalabel `RLoad` | | (21,16) | `datatype`=2, `index`=1 |
| master:varrlc  | | (32,15) | `RLC`=1, `R`=Lload, `L`=LLoad, `C`=1.0 [uF], `E`=0.0 [kV] |
| master:datalabel `QLoad` | | (10,29) | `datatype`=2, `index`=1 |
| master:datalabel `V_2` | | (10,13) | `datatype`=2, `index`=1 |
| master:compare  | | (14,33) | `OH`=1, `Dim`=1 |
| master:select  | | (17,31) | `A`=1, `DPath`=1, `COM`=Selector, `Dim`=1 |
| master:const  | | (13,31) | `Value`=1.0e-50, `Dim`=1 |
| master:div  | | (21,28) | `Dim`=1, `DPath`=1 |
| master:datalabel `V_2` | | (18,28) | `datatype`=2, `index`=1 |
| master:div  | | (25,28) | `Dim`=1, `DPath`=1 |
| master:emtconst `Constant` | | (31,31) | `Value`=1, `Dim`=1 |
| master:mult  | | (27,31) | `DPath`=1, `Dim`=1 |
| master:datalabel `Freq` | | (27,33) | `datatype`=2, `index`=1 |
| master:hardlimit  | | (29,28) | `UL`=1e6, `LL`=1e-18, `COM`=Hard_Limit, `Dim`=1 |
| master:datalabel `LLoad` | | (32,28) | `datatype`=2, `index`=1 |
| master:datalabel `QLoad` | | (10,39) | `datatype`=2, `index`=1 |
| master:compare  | | (14,43) | `OL`=1, `Dim`=1 |
| master:select  | | (17,41) | `A`=1, `DPath`=1, `COM`=Selector, `Dim`=1 |
| master:const  | | (13,41) | `Value`=1.0e-50, `Dim`=1 |
| master:div  | | (23,41) | `Dim`=1, `DPath`=1 |
| master:datalabel `V_2` | | (22,43) | `datatype`=2, `index`=1 |
| master:mult  | | (29,44) | `DPath`=1, `Dim`=1 |
| master:datalabel `Freq` | | (29,46) | `datatype`=2, `index`=1 |
| master:div  | | (27,41) | `Dim`=1, `DPath`=1 |
| master:emtconst `Constant` | | (33,44) | `Value`=1, `Dim`=1 |
| master:gain  | | (31,41) | `G`=1e6, `COM`=Gain, `Dim`=1, `DPath`=1 |
| master:hardlimit  | | (35,41) | `UL`=1e6, `LL`=1e-18, `COM`=Hard_Limit, `Dim`=1 |
| master:datalabel `CLoad` | | (39,41) | `datatype`=2, `index`=1 |
| master:abs  | | (13,39) | `Dim`=1, `DPath`=1 |
| master:varrlc  | | (36,15) | `RLC`=2, `R`=Lload, `L`=1.0 [H], `C`=CLoad, `E`=0.0 [kV] |
| master:ground  | | (32,17) |  |

Wiring (absolute endpoints, intermediate vertices included):

- (5,16) -> (6,16)
- (5,19) -> (6,19)
- (10,19) -> (12,19) -> (12,18)
- (18,16) -> (19,16)
- (19,16) -> (21,16)
- (10,16) -> (10,13)
- (11,33) -> (11,29)
- (10,29) -> (15,29)
- (16,33) -> (17,33)
- (12,33) -> (11,33)
- (18,28) -> (19,28)
- (19,31) -> (21,31) -> (21,30)
- (25,31) -> (25,30)
- (31,28) -> (32,28)
- (11,43) -> (11,39)
- (10,39) -> (11,39)
- (16,43) -> (17,43)
- (12,43) -> (11,43)
- (22,43) -> (23,43)
- (19,41) -> (21,41)
- (27,43) -> (27,44)
- (37,41) -> (39,41)
- (28,17) -> (36,17)
- (28,15) -> (28,13) -> (36,13) -> (36,15)
- (32,15) -> (32,13)
- (32,13) -> (32,11) -> (39,11)

## Canvas `GridEqSrc`

Module ports: uvw(dim 3, Electrical)

| component | type | at | parameters |
| --- | --- | --- | --- |
| master:xnode `uvw` | | (27,25) |  |
| master:ground  | | (14,21) |  |
| master:source3 `Source1` | | (14,19) | `Type`=4, `MVA`=1 [MVA], `Vm`=0.48 [kV], `F`=60.0 [Hz], `Tc`=0.05 [s], `Imp`=1, `View`=1, `R1s`=1.0 [ohm], `R1p`=1.0 [ohm], `L1p`=0.1 [H], `Z1`=0.18 [ohm], `Phi1`=80.0 [deg], `RN`=2.0, `R0p`=1.0 [ohm], `L0p`=0.1 [H], `Z0`=1.0 [ohm], `Phi0`=80.0 [deg], `Es`=0.48 [kV], `F0`=60.0 [Hz], `Ph`=0.0 [deg], `Pinit`=0.0 [pu], `Qinit`=0.0 [pu], `Vdes`=1.0 [pu], `Vbase`=230.0 [kV], `Tvm`=0.02 [s], `Tvc`=0.05 [s], `Pdes`=1.0 [pu], `Tpm`=0.02 [s], `Tpc`=0.05 [s], `R0s`=1.0 [ohm], `L0s`=0.0001 [H], `qset`=1, `PF_QMIN`=-1.0, `PF_QMAX`=1.0 |
| master:annotation  | | (9,18) | `AL1`=Isc = 1.5kA, `AL2`=(for 100kVA converter) |
| master:ground  | | (14,29) |  |
| master:source3 `Source1` | | (14,27) | `Type`=4, `MVA`=1 [MVA], `Vm`=0.48 [kV], `F`=60.0 [Hz], `Tc`=0.05 [s], `Imp`=1, `View`=1, `R1s`=1.0 [ohm], `R1p`=1.0 [ohm], `L1p`=0.1 [H], `Z1`=0.0924 [ohm], `Phi1`=80.0 [deg], `RN`=2.0, `R0p`=1.0 [ohm], `L0p`=0.1 [H], `Z0`=1.0 [ohm], `Phi0`=80.0 [deg], `Es`=0.48 [kV], `F0`=60.0 [Hz], `Ph`=0.0 [deg], `Pinit`=0.0 [pu], `Qinit`=0.0 [pu], `Vdes`=1.0 [pu], `Vbase`=230.0 [kV], `Tvm`=0.02 [s], `Tvc`=0.05 [s], `Pdes`=1.0 [pu], `Tpm`=0.02 [s], `Tpc`=0.05 [s], `R0s`=1.0 [ohm], `L0s`=0.0001 [H], `qset`=1, `PF_QMIN`=-1.0, `PF_QMAX`=1.0 |
| master:annotation  | | (9,26) | `AL1`=Isc =3kA, `AL2`=(for 250kVA converter) |
| master:ground  | | (14,37) |  |
| master:source3 `Source1` | | (14,35) | `Type`=4, `MVA`=1 [MVA], `Vm`=0.48 [kV], `F`=60.0 [Hz], `Tc`=0.05 [s], `Imp`=1, `View`=1, `R1s`=1.0 [ohm], `R1p`=1.0 [ohm], `L1p`=0.1 [H], `Z1`=0.046 [ohm], `Phi1`=80.0 [deg], `RN`=2.0, `R0p`=1.0 [ohm], `L0p`=0.1 [H], `Z0`=1.0 [ohm], `Phi0`=80.0 [deg], `Es`=0.48 [kV], `F0`=60.0 [Hz], `Ph`=0.0 [deg], `Pinit`=0.0 [pu], `Qinit`=0.0 [pu], `Vdes`=1.0 [pu], `Vbase`=230.0 [kV], `Tvm`=0.02 [s], `Tvc`=0.05 [s], `Pdes`=1.0 [pu], `Tpm`=0.02 [s], `Tpc`=0.05 [s], `R0s`=1.0 [ohm], `L0s`=0.0001 [H], `qset`=1, `PF_QMIN`=-1.0, `PF_QMAX`=1.0 |
| master:annotation  | | (9,34) | `AL1`=Isc = 6kA, `AL2`=(for 500kVA converter) |
| master:import `SCLevel` | | (7,6) |  |
| master:mux  | | (18,6) | `A`=1, `B`=2, `C`=3, `D`=4, `E`=5, `F`=6 |
| master:consti  | | (13,8) | `Value`=1, `Dim`=1 |
| master:breaker3  | | (18,17) | `CLVL`=0.0 [kA], `View`=1, `ViewB`=1, `NAME`=CB1, `NAMEA`=BRKA, `NAMEB`=BRKB, `NAMEC`=BRKC, `ROFF`=1.0e6 [ohm], `RON`=0.0005 [ohm], `PRER`=0.5 [ohm], `TDA`=0.0 [s], `TDB`=0.0 [s], `TDC`=0.0 [s], `TDRA`=0.05 [s], `TDRB`=0.05 [s], `TDRC`=0.05 [s], `TDBOA`=0.005 [s] |
| master:breaker3  | | (18,25) | `CLVL`=0.0 [kA], `View`=1, `ViewB`=1, `NAME`=CB2, `NAMEA`=BRKA, `NAMEB`=BRKB, `NAMEC`=BRKC, `ROFF`=1.0e6 [ohm], `RON`=0.0005 [ohm], `PRER`=0.5 [ohm], `TDA`=0.0 [s], `TDB`=0.0 [s], `TDC`=0.0 [s], `TDRA`=0.05 [s], `TDRB`=0.05 [s], `TDRC`=0.05 [s], `TDBOA`=0.005 [s] |
| master:breaker3  | | (18,33) | `CLVL`=0.0 [kA], `View`=1, `ViewB`=1, `NAME`=CB3, `NAMEA`=BRKA, `NAMEB`=BRKB, `NAMEC`=BRKC, `ROFF`=1.0e6 [ohm], `RON`=0.0005 [ohm], `PRER`=0.5 [ohm], `TDA`=0.0 [s], `TDB`=0.0 [s], `TDC`=0.0 [s], `TDRA`=0.05 [s], `TDRB`=0.05 [s], `TDRC`=0.05 [s], `TDBOA`=0.005 [s] |
| master:xy_transfer_function  | | (11,6) | `Xoff`=0.0, `Yoff`=0.0, `Kx`=1.0, `Ky`=1.0, `Mode`=1, `Method`=1, `N`=3, `X1`=1.5, `Y1`=1.0, `X2`=3, `Y2`=2.0, `X3`=6, `Y3`=3.0, `X4`=4.0, `Y4`=1.0, `X5`=5.0, `Y5`=5.0, `X6`=6.0, `Y6`=6.0, `X7`=7.0, `Y7`=7.0, `X8`=8.0, `Y8`=8.0, `X9`=9.0, `Y9`=9.0, `X10`=9.0, `Y10`=9.0, `File`=datafile, `npairs`=1000, `X11`=11, `X12`=12, `Y11`=11, `Y12`=12 |
| master:inv  | | (20,2) | `const`=false |
| master:datalabel `CB1` | | (24,2) | `datatype`=2, `index`=1 |
| master:inv  | | (20,4) | `const`=false |
| master:datalabel `CB2` | | (24,4) | `datatype`=2, `index`=1 |
| master:inv  | | (20,6) | `const`=false |
| master:datalabel `CB3` | | (24,6) | `datatype`=2, `index`=1 |

Wiring (absolute endpoints, intermediate vertices included):

- (16,17) -> (14,17)
- (16,25) -> (14,25)
- (16,33) -> (14,33)
- (15,8) -> (16,8)
- (13,6) -> (16,6)
- (20,17) -> (20,33)
- (20,25) -> (27,25)
- (22,2) -> (24,2)
- (22,4) -> (24,4)
- (22,6) -> (24,6)

## Canvas `IEEE1547Relay`

Module ports: Vabc(dim 3, Input), Iabc(dim 3, Input), Trip(dim 1, Output)

| component | type | at | parameters |
| --- | --- | --- | --- |
| master:import `Vabc` | | (4,2) |  |
| master:import `Iabc` | | (4,4) |  |
| master:export `Trip` | | (16,2) |  |
| master:datalabel `Vabc` | | (2,14) | `datatype`=2, `index`=1 |
| master:datatap  | | (10,15) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (10,18) | `Index`=2, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (10,21) | `Index`=3, `Dim`=1, `Type`=2, `Disp`=1 |
| master:tvekta  | | (24,17) | `Gp`=1950, `Gi`=1900.0, `Vbas`=1.0 [V], `Fbas`=60[Hz], `THOFF`=1.5707963267948966192313216916398, `dlead`=1, `HiLimit`=1.2, `LoLimit`=0.8 |
| master:datalabel `Theta` | | (29,17) | `datatype`=2, `index`=1 |
| master:datalabel `Vabc` | | (3,26) | `datatype`=2, `index`=1 |
| master:datatap  | | (6,27) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (6,29) | `Index`=2, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (6,31) | `Index`=3, `Dim`=1, `Type`=2, `Disp`=1 |
| master:fft  | | (10,29) | `Type`=3, `F`=60 [Hz], `Filt`=1, `Track`=1, `Enab`=1, `Fout`=fgrid |
| master:import `Freq` | | (4,8) |  |
| master:import `Vnom` | | (4,9) |  |
| master:datalabel `fgrid` | | (15,32) | `datatype`=2, `index`=1 |
| master:datalabel `PLLErr` | | (13,40) | `datatype`=2, `index`=1 |
| master:compar  | | (16,40) | `OPos`=1, `ONeg`=1, `OHi`=1 |
| master:gain  | | (5,14) | `G`=1.2247, `COM`=Gain, `Dim`=3, `DPath`=1 |
| master:annotation  | | (5,12) | `AL1`=sqrt(3/2) |
| master:div  | | (12,15) | `Dim`=1, `DPath`=1 |
| master:div  | | (12,18) | `Dim`=1, `DPath`=1 |
| master:div  | | (12,21) | `Dim`=1, `DPath`=1 |
| master:datalabel `Vnom` | | (3,16) | `datatype`=2, `index`=1 |
| master:datalabel `Vapu` | | (15,15) | `datatype`=2, `index`=1 |
| master:datalabel `Vbpu` | | (15,18) | `datatype`=2, `index`=1 |
| master:datalabel `Vcpu` | | (15,21) | `datatype`=2, `index`=1 |
| master:datalabel `Vapu` | | (21,15) | `datatype`=2, `index`=1 |
| master:datalabel `Vbpu` | | (21,17) | `datatype`=2, `index`=1 |
| master:datalabel `Vcpu` | | (21,19) | `datatype`=2, `index`=1 |
| master:var `Islanding error` | | (12,42) | `Display`=1, `Max`=1.0, `Min`=0.0, `Value`=0.01, `Units`=pu, `Collect`=1 |
| master:annotation  | | (12,37) | `AL1`=Islanding detection |
| master:logic_mult  | | (28,39) | `Type`=1, `Num_in`=2, `disnum`=1 |
| master:zminusone `Feedback Loop XYZ` | | (30,37) | `Type`=2, `Dim`=1, `InitR`=0.0, `InitC`=(0.0, 0.0) |
| master:datalabel `Island` | | (36,39) | `datatype`=2, `index`=1 |
| master:logic_mult  | | (51,26) | `Type`=1, `Num_in`=9, `disnum`=1 |
| master:datalabel `Island` | | (46,22) | `datatype`=2, `index`=1 |
| master:consti `Other trip conditions` | | (42,30) | `Dim`=1 |
| master:datalabel `Trip` | | (54,26) | `datatype`=2, `index`=1 |
| master:datalabel `PLLErr` | | (43,17) | `datatype`=2, `index`=1 |
| master:abcdq0  | | (35,17) | `IDir`=1, `Theta`=Theta, `dqorder`=1 |
| master:datalabel `Vapu` | | (32,16) | `datatype`=2, `index`=1 |
| master:datalabel `Vbpu` | | (32,17) | `datatype`=2, `index`=1 |
| master:datalabel `Vcpu` | | (32,18) | `datatype`=2, `index`=1 |
| master:abs  | | (39,17) | `Dim`=1, `DPath`=1 |
| master:pgb `PLLErr` | | (45,17) | `Display`=1, `Scale`=1.0, `Max`=2.0, `Min`=-2.0, `enab`=1 |
| master:delay  | | (33,39) | `T`=0.05 [s] |

Wiring (absolute endpoints, intermediate vertices included):

- (7,14) -> (9,14) -> (9,20)
- (3,26) -> (5,26) -> (5,31)
- (13,40) -> (16,40)
- (2,14) -> (3,14)
- (12,17) -> (11,17) -> (11,16) -> (3,16)
- (12,20) -> (11,20) -> (11,19) -> (5,19) -> (5,16)
- (12,23) -> (5,23) -> (5,19)
- (14,15) -> (15,15)
- (14,18) -> (15,18)
- (14,21) -> (15,21)
- (22,15) -> (21,15)
- (22,17) -> (21,17)
- (22,19) -> (21,19)
- (14,42) -> (16,42)
- (21,40) -> (26,40)
- (26,38) -> (26,35) -> (30,35)
- (35,39) -> (36,39)
- (46,22) -> (49,22)
- (44,30) -> (49,30) -> (49,23)
- (53,26) -> (54,26)
- (33,16) -> (32,16)
- (33,17) -> (32,17)
- (33,18) -> (32,18)
- (41,17) -> (45,17)
- (28,17) -> (29,17)
- (20,40) -> (21,40)
- (30,39) -> (31,39)

## Canvas `PIwithFreeze`

Module ports: In(dim 1, Input), Out(dim 1, Output), Rst(dim 1, Input)

| component | type | at | parameters |
| --- | --- | --- | --- |
| master:import `In` | | (16,15) |  |
| master:import `Rst` | | (29,27) |  |
| master:export `Out` | | (46,15) |  |
| master:hardlimit  | | (39,15) | `UL`=MaxOut, `LL`=MinOut, `COM`=Hard_Limit, `Dim`=1 |
| master:sumjct  | | (35,15) | `DPath`=1, `B`=1, `D`=1, `Dim`=1 |
| master:gain  | | (31,15) | `G`=Kp, `COM`=Gain, `Dim`=1, `DPath`=1 |
| master:integral  | | (31,23) | `Reset`=1, `T`=Ti, `Yo`=0.0, `YRst`=0.0, `YHi`=MaxOut, `YLo`=MinOut, `Dim`=1 |
| master:import `Kp` | | (11,3) |  |
| master:import `Ti` | | (11,4) |  |
| master:import `MaxOut` | | (11,7) |  |
| master:import `MinOut` | | (11,8) |  |
| master:mult  | | (25,15) | `DPath`=1, `Dim`=1 |
| master:datalabel `Rst` | | (18,12) | `datatype`=2, `index`=1 |
| master:inv  | | (19,12) | `const`=false |

Wiring (absolute endpoints, intermediate vertices included):

- (41,15) -> (44,15)
- (31,27) -> (31,25)
- (28,23) -> (29,23)
- (18,15) -> (23,15)
- (33,23) -> (35,23) -> (35,17)
- (27,15) -> (29,15)
- (21,12) -> (25,12) -> (25,13)
- (18,12) -> (19,12)
- (28,23) -> (27,23) -> (27,15)

## Canvas `VSC`

Module ports: uvw(dim 3, Electrical), Ppu(dim 1, Input), Qpu(dim 1, Input), DBLK1(dim 1, Input)

| component | type | at | parameters |
| --- | --- | --- | --- |
| master:xnode `uvw` | | (29,14) |  |
| master:voltmeter `V_dc` | | (105,13) |  |
| master:voltmetergnd `E1` | | (68,14) |  |
| master:ammeter `I_C` | | (66,14) |  |
| master:datalabel `GG1` | | (75,11) | `datatype`=2, `index`=1 |
| master:datalabel `GG3` | | (82,11) | `datatype`=2, `index`=1 |
| master:datalabel `GG5` | | (89,11) | `datatype`=2, `index`=1 |
| master:datalabel `GG4` | | (75,19) | `datatype`=2, `index`=1 |
| master:datalabel `GG6` | | (82,19) | `datatype`=2, `index`=1 |
| master:datalabel `GG2` | | (89,19) | `datatype`=2, `index`=1 |
| master:datalabel `GG1` | | (90,67) | `datatype`=2, `index`=1 |
| master:datalabel `GG2` | | (112,67) | `datatype`=2, `index`=1 |
| master:datalabel `GG3` | | (101,67) | `datatype`=2, `index`=1 |
| master:datalabel `GG4` | | (93,67) | `datatype`=2, `index`=1 |
| master:datalabel `GG5` | | (115,67) | `datatype`=2, `index`=1 |
| master:datalabel `GG6` | | (104,67) | `datatype`=2, `index`=1 |
| master:peswitch  | | (78,11) | `L`=D, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=17 [kV], `Erw`=17 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (77,9) | `L`=Q, `Type`=3, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=17 [kV], `Erw`=17 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:breakout  | | (68,14) |  |
| master:capacitor  | | (97,13) | `C`=10000 [uF] |
| master:datalabel `Ic_C` | | (66,48) | `datatype`=2, `index`=1 |
| master:datalabel `Ib_C` | | (66,47) | `datatype`=2, `index`=1 |
| master:datalabel `Ia_C` | | (66,46) | `datatype`=2, `index`=1 |
| master:datalabel `Ec` | | (66,44) | `datatype`=2, `index`=1 |
| master:datalabel `Eb` | | (66,43) | `datatype`=2, `index`=1 |
| master:datalabel `Ea` | | (66,42) | `datatype`=2, `index`=1 |
| master:datatap  | | (64,42) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datalabel `Vgrid` | | (59,42) | `datatype`=2, `index`=1 |
| master:peswitch  | | (85,11) | `L`=D, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=17 [kV], `Erw`=17 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (92,11) | `L`=D, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=17 [kV], `Erw`=17 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (92,19) | `L`=D, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=17 [kV], `Erw`=17 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (85,19) | `L`=D, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=17 [kV], `Erw`=17 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (78,19) | `L`=D, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=17 [kV], `Erw`=17 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:ground  | | (94,24) |  |
| master:peswitch  | | (84,9) | `L`=Q, `Type`=3, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=17 [kV], `Erw`=17 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (91,9) | `L`=Q, `Type`=3, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=17 [kV], `Erw`=17 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (91,17) | `L`=Q, `Type`=3, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=17 [kV], `Erw`=17 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (84,17) | `L`=Q, `Type`=3, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=17 [kV], `Erw`=17 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (77,17) | `L`=Q, `Type`=3, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=17 [kV], `Erw`=17 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:import `DBLK1` | | (22,40) |  |
| master:import `Qpu` | | (22,44) |  |
| master:import `Kpd` | | (16,43) |  |
| master:import `Tid` | | (16,44) |  |
| master:import `Kpq` | | (16,45) |  |
| master:import `Tiq` | | (16,46) |  |
| master:import `Kp_Q` | | (16,41) |  |
| master:import `Ti_Q` | | (16,42) |  |
| master:import `System_Freq` | | (22,39) |  |
| master:import `Kp_PLL` | | (16,37) |  |
| master:import `Ti_PLL` | | (16,38) |  |
| master:import `Sbase` | | (22,38) |  |
| master:import `MV_Vbase` | | (22,37) |  |
| master:datalabel `Lpu` | | (31,45) | `datatype`=2, `index`=1 |
| master:div  | | (61,42) | `Dim`=3, `DPath`=1 |
| master:datatap  | | (64,43) | `Index`=2, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (64,44) | `Index`=3, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datalabel `INV_Ibase_pk` | | (60,48) | `datatype`=2, `index`=1 |
| master:datalabel `Igrid` | | (59,46) | `datatype`=2, `index`=1 |
| master:datalabel `INV_Sbase` | | (22,53) | `datatype`=2, `index`=1 |
| master:datalabel `INV_Vbase` | | (22,55) | `datatype`=2, `index`=1 |
| master:mult  | | (25,55) | `DPath`=1, `Dim`=1 |
| master:emtconst  | | (23,57) | `Value`=10, `Dim`=1 |
| master:div  | | (28,53) | `Dim`=1, `DPath`=1 |
| master:datalabel `INV_Ibase` | | (32,53) | `datatype`=2, `index`=1 |
| master:emtconst  | | (27,61) | `Value`=9, `Dim`=1 |
| master:annotation  | | (19,62) | `AL1`=LL,rms |
| master:mult  | | (29,59) | `DPath`=1, `Dim`=1 |
| master:mult  | | (33,59) | `DPath`=1, `Dim`=1 |
| master:emtconst  | | (31,61) | `Value`=12, `Dim`=1 |
| master:datalabel `INV_Vbase_LNpk` | | (38,59) | `datatype`=2, `index`=1 |
| master:datalabel `INV_Vbase_LNpk` | | (58,44) | `datatype`=2, `index`=1 |
| master:datalabel `INV_Ibase_pk` | | (42,53) | `datatype`=2, `index`=1 |
| master:mult  | | (37,53) | `DPath`=1, `Dim`=1 |
| master:annotation  | | (42,54) | `AL1`=L,rms |
| master:emtconst  | | (35,55) | `Value`=9, `Dim`=1 |
| master:datalabel `INV_Vbase` | | (21,63) | `datatype`=2, `index`=1 |
| master:square  | | (25,63) | `Dim`=1, `DPath`=1 |
| master:div  | | (29,63) | `Dim`=1, `DPath`=1 |
| master:datalabel `INV_Sbase` | | (22,65) | `datatype`=2, `index`=1 |
| master:datalabel `INV_Zbase` | | (32,63) | `datatype`=2, `index`=1 |
| master:datatap  | | (64,48) | `Index`=3, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (64,47) | `Index`=2, `Dim`=1, `Type`=2, `Disp`=1 |
| master:div  | | (61,46) | `Dim`=3, `DPath`=1 |
| master:datatap  | | (64,46) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:varrlc  | | (62,14) | `RLC`=1, `R`=1.0 [ohm], `L`=Lfilter, `C`=1.0 [uF], `E`=0.0 [kV] |
| master:varrlc  | | (52,18) | `R`=Rdamp, `L`=Ldamp, `C`=Cdamp, `E`=0.0 [kV] |
| master:varrlc  | | (54,16) | `RLC`=1, `R`=1.0 [ohm], `L`=Ldamp, `C`=Cdamp, `E`=0.0 [kV] |
| master:varrlc  | | (54,20) | `RLC`=2, `R`=1.0 [ohm], `L`=Cdamp, `C`=Cdamp, `E`=0.0 [kV] |
| master:varrlc  | | (61,16) | `RLC`=2, `R`=1.0 [ohm], `L`=Filter_L, `C`=Cfilter, `E`=0.0 [kV] |
| master:varrlc  | | (58,14) | `RLC`=1, `R`=1.0 [ohm], `L`=Lfilter, `C`=1.0 [uF], `E`=0.0 [kV] |
| master:short  | | (54,22) |  |
| master:short  | | (61,18) |  |
| master:gain  | | (41,73) | `G`=1e-6, `COM`=Gain, `Dim`=1, `DPath`=1 |
| master:datalabel `Rdamp` | | (50,77) | `datatype`=2, `index`=1 |
| master:sqrt  | | (47,77) | `Dim`=1, `DPath`=1 |
| master:div  | | (43,77) | `Dim`=1, `DPath`=1 |
| master:datalabel `Cdamp` | | (38,73) | `datatype`=2, `index`=1 |
| master:gain  | | (35,73) | `G`=0.5, `COM`=Gain, `Dim`=1, `DPath`=1 |
| master:datalabel `Ldamp` | | (38,77) | `datatype`=2, `index`=1 |
| master:gain  | | (35,77) | `G`=5.0, `COM`=Gain, `Dim`=1, `DPath`=1 |
| master:mult  | | (28,75) | `DPath`=1, `Dim`=1 |
| master:square  | | (24,75) | `Dim`=1, `DPath`=1 |
| master:emtconst  | | (16,75) | `Value`=1, `Dim`=1 |
| master:mult  | | (20,75) | `DPath`=1, `Dim`=1 |
| master:const  | | (26,73) | `Value`=1e5, `Dim`=1 |
| master:div  | | (30,73) | `Dim`=1, `DPath`=1 |
| master:datalabel `Lfilter` | | (28,77) | `datatype`=2, `index`=1 |
| master:datalabel `Cfilter` | | (32,73) | `datatype`=2, `index`=1 |
| master:mult  | | (16,80) | `DPath`=1, `Dim`=1 |
| master:const `L pu total` | | (27,45) | `Value`=0.144, `Dim`=1 |
| master:datalabel `Lpu` | | (14,80) | `datatype`=2, `index`=1 |
| master:gain  | | (20,80) | `G`=0.5, `COM`=Gain, `Dim`=1, `DPath`=1 |
| master:div  | | (24,80) | `Dim`=1, `DPath`=1 |
| master:emtconst  | | (20,84) | `Value`=1, `Dim`=1 |
| master:mult  | | (24,84) | `DPath`=1, `Dim`=1 |
| master:datalabel `System_Freq` | | (24,86) | `datatype`=2, `index`=1 |
| master:multimeter  | | (47,14) | `MeasV`=1, `MeasI`=1, `MeasP`=1, `MeasQ`=1, `RMS`=2, `S`=Sbase, `BaseV`=0.6 [kV], `BaseA`=1.0, `TS`=0.02, `Freq`=System_Freq, `Dis`=1, `CurI`=Igrid, `VolI`=Vgrid, `P`=P, `Q`=Q, `Vrms`=Vrms, `Pd`=0.0, `Qd`=0.0, `Vd`=0.0 |
| master:import `Kp_P` | | (16,39) |  |
| master:import `Ti_P` | | (16,40) |  |
| master:import `Ppu` | | (22,43) |  |
| master:datalabel `Qmin` | | (29,48) | `datatype`=2, `index`=1 |
| master:gain  | | (26,48) | `COM`=neg, `Dim`=1, `DPath`=1 |
| master:import `Pmin` | | (22,47) |  |
| master:import `Pmax` | | (22,46) |  |
| master:import `Qmax` | | (22,48) |  |
| master:import `Pramp` | | (16,48) |  |
| master:import `Qramp` | | (16,49) |  |
| master:datalabel `INV_Zbase` | | (16,82) | `datatype`=2, `index`=1 |
| master:multimeter  | | (31,14) | `MeasP`=1, `MeasQ`=1, `S`=1.0 [MVA], `BaseV`=1.0 [kV], `BaseA`=1.0 [kA], `TS`=0.02 [s], `Freq`=60.0 [Hz], `Dis`=1, `Pd`=0.0, `Qd`=0.0, `Vd`=0.0 |
| master:xfmr-3p2w  | | (43,14) | `Tmva`=Sbase, `f`=System_Freq, `YD1`=1, `Lead`=1, `Xl`=0.025 [pu], `Ideal`=1, `NLL`=0.0 [pu], `CuL`=0.0001 [pu], `View`=1, `V1`=MV_VBase, `V2`=0.6 [kV], `Xair`=0.2 [pu], `Tdc`=0.0 [s], `Xknee`=1.17 [pu], `Txk`=0.0 [s], `Im1`=2.0 [%], `Fremn1`=0.0, `Fremn2`=0.0, `Fremn3`=0.0, `LW2`=10, `Bnom`=1.7, `material`=1, `C`=0.1, `K`=5.0e-5, `BETA`=0.96, `alpha`=1.325e-5, `Msat`=1.72e6, `F1`=2730, `F2`=3209, `F3`=20294, `Fb`=2 |
| master:ground  | | (43,16) |  |
| master:resistor  | | (94,22) | `R`=1.0 [Mohm] |
| master:import `Scale` | | (32,9) |  |
| master:const `[kV]` | | (27,43) | `Value`=1.3, `Dim`=1 |
| master:unity  | | (20,53) | `IType`=2, `OType`=2, `Dim`=1, `const`=false |
| master:datalabel `Sbase` | | (16,53) | `datatype`=2, `index`=1 |
| master:const  | | (17,55) | `Value`=0.6, `Dim`=1 |
| master:datalabel `INV_Vbase_LNpk` | | (71,89) | `datatype`=2, `index`=1 |
| master:div  | | (71,91) | `Dim`=1, `DPath`=1 |
| master:inv  | | (67,87) | `const`=false |
| SimpleSolarFarm:PIwithFreeze  | | (67,91) | `Kp`=Kpq, `Ti`=Tiq, `MaxOut`=0.392, `MinOut`=-0.392 |
| master:datalabel `DBlk` | | (68,87) | `datatype`=2, `index`=1 |
| SimpleSolarFarm:PIwithFreeze  | | (67,103) | `Kp`=Kpd, `Ti`=Tid, `MaxOut`=0.392, `MinOut`=-0.392 |
| master:abcdq0  | | (69,47) | `IDir`=1, `Theta`=Theta, `dqorder`=1 |
| master:abcdq0  | | (69,43) | `IDir`=1, `Theta`=Theta, `dqorder`=1 |
| master:tvekta  | | (68,38) | `Gp`=Kp_PLL, `Gi`=Ti_PLL, `Vbas`=1.0 [V], `Fbas`=System_Freq, `THOFF`=1.5707963267948966192313216916398, `dlead`=1, `FName`=PLL_f, `HiLimit`=1.2, `LoLimit`=0.8 |
| master:pgb `d PI out` | | (73,103) | `Display`=1, `Scale`=1.0, `Units`=V, `Min`=-20, `Max`=20, `enab`=1 |
| master:datalabel `vq` | | (70,97) | `datatype`=2, `index`=1 |
| master:pgb `PLL Theta` | | (73,38) | `Display`=1, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datalabel `Ec` | | (66,40) | `datatype`=2, `index`=1 |
| master:datalabel `Eb` | | (66,38) | `datatype`=2, `index`=1 |
| master:datalabel `Ea` | | (66,36) | `datatype`=2, `index`=1 |
| master:datalabel `vd` | | (70,109) | `datatype`=2, `index`=1 |
| master:pgb `q PI out` | | (73,91) | `Display`=1, `Scale`=1.0, `Units`=V, `Min`=-8, `Max`=8, `enab`=1 |
| master:pgb `Vq Reference` | | (73,95) | `Display`=1, `Scale`=1.0, `Min`=-0.3, `Max`=0.4, `enab`=1 |
| master:gain  | | (66,95) | `G`=Lpu, `COM`=L, `Dim`=1, `DPath`=1 |
| master:pgb `Vd Reference` | | (73,107) | `Display`=1, `Scale`=1.0, `Min`=-0.3, `Max`=0.4, `enab`=1 |
| master:pgb `Iq Reference` | | (61,93) | `Display`=1, `Scale`=1.0, `Units`=pu, `Min`=-0.12, `Max`=0.02, `enab`=1 |
| master:pgb `Id Reference` | | (61,105) | `Display`=1, `Scale`=1.0, `Units`=pu, `Min`=-0.1, `Max`=0.2, `enab`=1 |
| master:datalabel `iq` | | (63,89) | `datatype`=2, `index`=1 |
| master:sumjct  | | (63,91) | `DPath`=1, `D`=1, `Dim`=1 |
| master:datalabel `iqref1` | | (60,91) | `datatype`=2, `index`=1 |
| master:datalabel `id` | | (63,101) | `datatype`=2, `index`=1 |
| master:sumjct  | | (63,103) | `DPath`=1, `D`=1, `Dim`=1 |
| master:datalabel `idref` | | (60,103) | `datatype`=2, `index`=1 |
| master:datalabel `vq1` | | (72,95) | `datatype`=2, `index`=1 |
| master:datalabel `id` | | (60,95) | `datatype`=2, `index`=1 |
| master:sumjct  | | (70,95) | `DPath`=1, `D`=1, `F`=1, `Dim`=1 |
| master:datalabel `vd1` | | (72,107) | `datatype`=2, `index`=1 |
| master:datalabel `iq` | | (60,107) | `datatype`=2, `index`=1 |
| master:sumjct  | | (70,107) | `DPath`=1, `F`=1, `Dim`=1 |
| master:pgb `Iq  Measured` | | (73,48) | `Display`=1, `Scale`=1, `Units`=pu, `Min`=-0.12, `Max`=0.12, `enab`=1 |
| master:pgb `Id  Measured` | | (73,46) | `Display`=1, `Scale`=1, `Units`=pu, `Min`=-0.2, `Max`=0.2, `enab`=1 |
| master:datalabel `iq` | | (72,48) | `datatype`=2, `index`=1 |
| master:datalabel `id` | | (72,46) | `datatype`=2, `index`=1 |
| master:pgb `Vq Measured` | | (73,44) | `Display`=1, `Scale`=1, `Units`=V, `Min`=-300, `Max`=300, `enab`=1 |
| master:pgb `Vd Measured` | | (73,42) | `Display`=1, `Scale`=1, `Units`=V, `Min`=-300, `Max`=300, `enab`=1 |
| master:datalabel `vq` | | (72,44) | `datatype`=2, `index`=1 |
| master:datalabel `vd` | | (72,42) | `datatype`=2, `index`=1 |
| master:datalabel `theta` | | (72,38) | `datatype`=2, `index`=1 |
| master:datalabel `Qpu` | | (55,56) | `datatype`=2, `index`=1 |
| master:hardlimit  | | (58,56) | `UL`=Qmax, `LL`=Qmin, `COM`=Hard_Limit, `Dim`=1, `Limit`=1 |
| master:ratelimit  | | (66,56) | `IR`=Qramp, `DR`=Qramp, `COM`=Rate_Limiter, `Dim`=1 |
| master:div  | | (79,56) | `Dim`=1, `DPath`=1 |
| master:datalabel `INV_Ibase_pk` | | (79,58) | `datatype`=2, `index`=1 |
| master:inv  | | (76,54) | `const`=false |
| master:datalabel `DBlk` | | (77,54) | `datatype`=2, `index`=1 |
| master:pgb `Q ref` | | (68,58) | `Display`=1, `Scale`=1.0, `Units`=MVAr, `Min`=0.0, `Max`=0.4, `enab`=1 |
| master:datalabel `Q` | | (70,54) | `datatype`=2, `index`=1 |
| master:sumjct  | | (70,56) | `DPath`=1, `D`=1, `Dim`=1 |
| master:datalabel `Qmax` | | (60,54) | `datatype`=2, `index`=1 |
| master:datalabel `Qmin` | | (56,58) | `datatype`=2, `index`=1 |
| master:datalabel `iqref` | | (82,56) | `datatype`=2, `index`=1 |
| master:datalabel `idref` | | (82,63) | `datatype`=2, `index`=1 |
| master:datalabel `Pmin` | | (56,65) | `datatype`=2, `index`=1 |
| master:datalabel `Pmax` | | (60,61) | `datatype`=2, `index`=1 |
| master:sumjct  | | (70,63) | `DPath`=1, `D`=1, `Dim`=1 |
| master:datalabel `P` | | (70,61) | `datatype`=2, `index`=1 |
| master:pgb `P ref` | | (68,65) | `Display`=1, `Scale`=1.0, `Units`=MW, `Min`=0.0, `Max`=0.4, `enab`=1 |
| master:datalabel `DBlk` | | (77,61) | `datatype`=2, `index`=1 |
| master:inv  | | (76,61) | `const`=false |
| master:datalabel `INV_Ibase_pk` | | (79,65) | `datatype`=2, `index`=1 |
| master:div  | | (79,63) | `Dim`=1, `DPath`=1 |
| master:ratelimit  | | (66,63) | `IR`=Pramp, `DR`=Pramp, `COM`=Rate_Limiter, `Dim`=1 |
| master:hardlimit  | | (58,63) | `UL`=Qmax, `LL`=Qmin, `COM`=Hard_Limit, `Dim`=1, `Limit`=1 |
| master:datalabel `Ppu1` | | (55,63) | `datatype`=2, `index`=1 |
| master:div  | | (71,103) | `Dim`=1, `DPath`=1 |
| master:datalabel `DBlk` | | (68,99) | `datatype`=2, `index`=1 |
| master:inv  | | (67,99) | `const`=false |
| master:datalabel `INV_Vbase_LNpk` | | (71,101) | `datatype`=2, `index`=1 |
| master:gain  | | (66,107) | `G`=Lpu, `COM`=L, `Dim`=1, `DPath`=1 |
| master:div  | | (100,40) | `Dim`=1, `DPath`=1 |
| master:fp_int  | | (90,63) | `Type`=1, `Blck`=1, `max`=360.0, `min`=0.0, `PTime`=0.005 [s] |
| master:datalabel `Crr` | | (87,59) | `datatype`=2, `index`=1 |
| master:datalabel `Ref_a` | | (88,62) | `datatype`=2, `index`=1 |
| master:datalabel `Crr` | | (110,62) | `datatype`=2, `index`=1 |
| master:datalabel `Ref_c` | | (109,59) | `datatype`=2, `index`=1 |
| master:datalabel `Crr` | | (98,59) | `datatype`=2, `index`=1 |
| master:datalabel `Ref_b` | | (99,62) | `datatype`=2, `index`=1 |
| master:datalabel `Crr` | | (95,62) | `datatype`=2, `index`=1 |
| master:datalabel `Ref_a` | | (96,59) | `datatype`=2, `index`=1 |
| master:datalabel `Crr` | | (118,59) | `datatype`=2, `index`=1 |
| master:datalabel `Ref_c` | | (117,62) | `datatype`=2, `index`=1 |
| master:datalabel `Crr` | | (106,62) | `datatype`=2, `index`=1 |
| master:datalabel `Ref_b` | | (107,59) | `datatype`=2, `index`=1 |
| master:datalabel `Crr` | | (106,55) | `datatype`=2, `index`=1 |
| master:datalabel `vd1` | | (87,40) | `datatype`=2, `index`=1 |
| master:datalabel `vq1` | | (87,42) | `datatype`=2, `index`=1 |
| master:datalabel `Ref_a` | | (112,40) | `datatype`=2, `index`=1 |
| master:datalabel `Ref_b` | | (112,41) | `datatype`=2, `index`=1 |
| master:datalabel `Ref_c` | | (112,42) | `datatype`=2, `index`=1 |
| master:const `mf` | | (98,53) | `Value`=60, `Dim`=1 |
| master:sig_gen  | | (104,55) | `Max`=1 |
| master:pgb `Phase A Reference` | | (113,40) | `Display`=1, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:pgb `Carrier` | | (106,55) | `Display`=1, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:pgb `m*` | | (102,38) | `Display`=1, `Scale`=1, `Max`=1, `enab`=1 |
| master:pgb `Delta` | | (100,46) | `Display`=1, `Scale`=1.0, `Units`=o, `Min`=-90, `Max`=90, `enab`=1 |
| master:fp_int  | | (104,63) | `Type`=1, `Blck`=1, `max`=360.0, `min`=0.0, `PTime`=0.005 [s] |
| master:fp_int  | | (112,63) | `Type`=1, `Blck`=1, `max`=360.0, `min`=0.0, `PTime`=0.005 [s] |
| master:fp_int  | | (101,63) | `Type`=1, `Blck`=1, `max`=360.0, `min`=0.0, `PTime`=0.005 [s] |
| master:datalabel `DBLK` | | (90,57) | `datatype`=2, `index`=1 |
| master:fp_int  | | (93,63) | `Type`=1, `Blck`=1, `max`=360.0, `min`=0.0, `PTime`=0.005 [s] |
| master:fp_int  | | (115,63) | `Type`=1, `Blck`=1, `max`=360.0, `min`=0.0, `PTime`=0.005 [s] |
| master:datalabel `V_dc` | | (95,38) | `datatype`=2, `index`=1 |
| master:polar_rec  | | (96,41) | `Dir`=1 |
| master:polar_rec  | | (104,41) |  |
| master:abcdq0  | | (109,41) | `Theta`=Theta, `dqorder`=1 |
| master:const  | | (107,44) | `Dim`=1 |
| master:gain  | | (98,38) | `G`=0.5, `Dim`=1, `DPath`=1 |
| master:emtconst  | | (96,44) | `Value`=6, `Dim`=1 |
| master:mult  | | (100,44) | `DPath`=1, `Dim`=1 |
| master:mult  | | (100,55) | `DPath`=1, `Dim`=1 |
| master:datalabel `System_Freq` | | (96,55) | `datatype`=2, `index`=1 |
| master:gain  | | (90,40) | `G`=INV_Vbase_LNpk, `COM`=was INV_Vdcbase, `Dim`=1, `DPath`=1 |
| master:gain  | | (90,42) | `G`=INV_Vbase_LNpk, `COM`=was INV_Vdcbase, `Dim`=1, `DPath`=1 |
| master:datalabel `Fcr` | | (102,55) | `datatype`=2, `index`=1 |
| master:datalabel `Fcr` | | (15,77) | `datatype`=2, `index`=1 |
| master:gain  | | (18,77) | `G`=0.1, `COM`=Gain, `Dim`=1, `DPath`=1 |
| master:datalabel `Vdc_Base` | | (31,43) | `datatype`=2, `index`=1 |
| master:datalabel `IdMax` | | (81,74) | `datatype`=2, `index`=1 |
| master:datalabel `IdMin` | | (81,76) | `datatype`=2, `index`=1 |
| master:gain  | | (62,56) | `COM`=L, `Dim`=1, `DPath`=1 |
| master:gain  | | (62,63) | `COM`=L, `Dim`=1, `DPath`=1 |
| master:pgb `Vgrid` | | (58,42) | `UseSignalName`=1, `enab`=1, `Display`=1, `Scale`=1.0, `Max`=2.0, `Min`=-2.0 |
| master:pgb `Igrid` | | (58,46) | `UseSignalName`=1, `enab`=1, `Display`=1, `Scale`=1.0, `Max`=2.0, `Min`=-2.0 |
| master:multimeter  | | (39,14) | `MeasP`=1, `MeasQ`=1, `S`=1.0 [MVA], `BaseV`=1.0 [kV], `BaseA`=1.0 [kA], `TS`=0.02 [s], `Freq`=60.0 [Hz], `Dis`=1, `Pd`=0.0, `Qd`=0.0, `Vd`=0.0 |
| master:pgb `V_dc` | | (93,38) | `UseSignalName`=1, `enab`=1, `Display`=1, `Scale`=1.0, `Max`=2.0, `Min`=-2.0 |
| master:mult  | | (42,36) | `Dim`=1 |
| master:datalabel `DBLK` | | (44,36) | `datatype`=2, `index`=1 |
| master:sumjct  | | (89,75) | `DPath`=1, `D`=1, `Dim`=1 |
| master:datalabel `Vrms` | | (89,73) | `datatype`=2, `index`=1 |
| master:const  | | (87,73) | `Value`=1.0, `Dim`=1 |
| master:compare  | | (97,79) | `X`=LVRT, `OH`=1, `Dim`=1, `conv`=1 |
| master:compare  | | (97,83) | `X`=HVRT, `OL`=1, `Dim`=1, `conv`=1 |
| master:datalabel `LVRT_ON` | | (100,79) | `datatype`=2, `index`=1 |
| master:datalabel `HVRT_ON` | | (100,83) | `datatype`=2, `index`=1 |
| master:sumjct  | | (101,73) | `DPath`=1, `B`=1, `D`=1, `Dim`=1 |
| SimpleSolarFarm:PI_AntiWindUp  | | (74,63) | `Kp`=Kp_P, `Ti`=Ti_P, `Kaw`=1, `MaxOut`=IdMax, `MinOut`=IdMin |
| SimpleSolarFarm:PI_AntiWindUp  | | (74,56) | `Kp`=Kp_Q, `Ti`=Ti_Q, `Kaw`=1, `MaxOut`=IqMax, `MinOut`=IqMin |
| master:logic_mult  | | (103,81) | `Type`=1, `Num_in`=2 |
| master:datalabel `VRT_ON` | | (109,81) | `datatype`=2, `index`=1 |
| master:datalabel `VRT_ON` | | (74,58) | `datatype`=2, `index`=1 |
| master:datalabel `iqref` | | (97,71) | `datatype`=2, `index`=1 |
| master:datalabel `iqref1` | | (107,73) | `datatype`=2, `index`=1 |
| master:pgb `Vrms` | | (90,73) | `UseSignalName`=1, `enab`=1, `Display`=1, `Scale`=1.0, `Max`=2.0, `Min`=-2.0 |
| master:consti  | | (72,65) | `Dim`=1 |
| master:gain  | | (93,75) | `G`=DBlk, `Dim`=1, `DPath`=1 |
| master:import `VRT_ENAB` | | (37,47) |  |
| master:import `db_VRT` | | (37,48) |  |
| master:import `m_VRT` | | (37,49) |  |
| master:import `m_P_f` | | (43,48) |  |
| master:import `db_P_f` | | (43,47) |  |
| master:import `P_f_ENAB` | | (43,46) |  |
| master:select  | | (105,73) | `A`=1, `DPath`=1, `COM`=Selector, `Dim`=1 |
| master:datalabel `VRT_ENAB` | | (105,75) | `datatype`=2, `index`=1 |
| master:select  | | (107,81) | `A`=1, `COM`=Selector, `Dim`=1 |
| master:consti  | | (103,83) | `Dim`=1 |
| master:nodelabel `f_meas_node` | | (46,18) | `VName`=VNode, `VBase`=1 [kV] |
| master:sumjct  | | (95,97) | `DPath`=1, `D`=1, `Dim`=1 |
| master:datalabel `System_Freq` | | (95,99) | `datatype`=2, `index`=1 |
| master:datalabel `db_VRT` | | (87,79) | `datatype`=2, `index`=1 |
| master:gain  | | (90,79) | `G`=0.5, `COM`=neg, `Dim`=1, `DPath`=1 |
| master:gain  | | (93,81) | `COM`=neg, `Dim`=1, `DPath`=1 |
| master:datalabel `LVRT` | | (93,79) | `datatype`=2, `index`=1 |
| master:datalabel `HVRT` | | (93,83) | `datatype`=2, `index`=1 |
| master:select  | | (113,93) | `A`=1, `DPath`=1, `COM`=Selector, `Dim`=1 |
| master:sumjct  | | (109,93) | `DPath`=1, `B`=1, `D`=1, `Dim`=1 |
| master:datalabel `P_f_ENAB` | | (113,95) | `datatype`=2, `index`=1 |
| master:datalabel `Ppu` | | (105,91) | `datatype`=2, `index`=1 |
| master:datalabel `Ppu1` | | (115,93) | `datatype`=2, `index`=1 |
| master:range  | | (31,38) | `XL`=0.95, `XU`=1.05, `OM`=1, `COM`=Band_Compare, `Dim`=1, `conv`=1 |
| master:delay  | | (35,38) | `T`=0.1 [s] |
| master:maxmin  | | (39,38) | `Type`=1, `D`=1, `E`=1 |
| master:datalabel `Vrms` | | (28,38) | `datatype`=2, `index`=1 |
| master:datalabel `INIT` | | (42,38) | `datatype`=2, `index`=1 |
| master:datalabel `DBLK1` | | (40,36) | `datatype`=2, `index`=1 |
| master:datalabel `INV_Ibase_pk` | | (59,72) | `datatype`=2, `index`=1 |
| master:gain  | | (63,72) | `G`=1.1, `COM`=L, `Dim`=1, `DPath`=1 |
| master:datalabel `Imax` | | (67,72) | `datatype`=2, `index`=1 |
| master:square  | | (60,75) | `Dim`=1, `DPath`=1 |
| master:sqrt  | | (68,77) | `Dim`=1, `DPath`=1 |
| master:sumjct  | | (64,77) | `DPath`=1, `D`=1, `Dim`=1 |
| master:square  | | (60,78) | `Dim`=1, `DPath`=1 |
| master:datalabel `id1` | | (57,81) | `datatype`=2, `index`=1 |
| master:datalabel `iq1` | | (57,75) | `datatype`=2, `index`=1 |
| master:datalabel `Imax` | | (57,78) | `datatype`=2, `index`=1 |
| master:sumjct  | | (64,79) | `DPath`=1, `D`=1, `Dim`=1 |
| master:sqrt  | | (68,79) | `Dim`=1, `DPath`=1 |
| master:square  | | (60,81) | `Dim`=1, `DPath`=1 |
| master:gain  | | (78,76) | `COM`=L, `Dim`=1, `DPath`=1 |
| master:select  | | (73,76) | `DPath`=1, `COM`=Selector, `Dim`=1 |
| master:import `PR` | | (22,41) |  |
| master:datalabel `PR` | | (73,78) | `datatype`=2, `index`=1 |
| master:datalabel `iq_pr` | | (70,80) | `datatype`=2, `index`=1 |
| master:datalabel `id_pr` | | (70,76) | `datatype`=2, `index`=1 |
| master:datalabel `Imax` | | (70,74) | `datatype`=2, `index`=1 |
| master:datalabel `Imax` | | (70,82) | `datatype`=2, `index`=1 |
| master:select  | | (73,80) | `A`=1, `DPath`=1, `COM`=Selector, `Dim`=1 |
| master:gain  | | (78,80) | `COM`=L, `Dim`=1, `DPath`=1 |
| master:datalabel `IqMin` | | (81,80) | `datatype`=2, `index`=1 |
| master:datalabel `IqMax` | | (81,82) | `datatype`=2, `index`=1 |
| master:datalabel `iq1` | | (77,56) | `datatype`=2, `index`=1 |
| master:datalabel `id1` | | (77,63) | `datatype`=2, `index`=1 |
| SimpleSolarFarm:deadband  | | (98,95) | `X`=1, `OH`=1, `Dim`=1, `deadband`=db_P_f, `offset`=0.0, `Gain`=m_P_f |
| master:datalabel `PLL_f` | | (88,97) | `datatype`=2, `index`=1 |
| master:ratelimit  | | (106,95) | `IR`=rate_P_f, `DR`=rate_P_f, `COM`=Rate_Limiter, `Dim`=1 |
| master:import `rate_P_f` | | (43,49) |  |
| master:pgb `RT_59` | | (93,95) | `UseSignalName`=1, `enab`=1, `Display`=1, `Scale`=1.0, `Max`=2.0, `Min`=-2.0 |
| master:trans_filt  | | (91,97) | `Order`=3, `Band`=1, `Type`=1, `FBase`=120.0 [Hz], `Flow`=10.0 [Hz], `Fup`=100.0 [Hz], `Q`=5, `PRip`=0.1 [dB], `Dim`=1 |
| master:gain  | | (102,95) | `G`=DBlk, `COM`=neg, `Dim`=1, `DPath`=1 |
| master:ammeter `Ipv` | | (130,11) |  |
| master:voltmeter `Vpv` | | (131,13) |  |
| master:datalabel `Vpv` | | (154,50) | `datatype`=2, `index`=1 |
| master:pgb `Vpv` | | (157,50) | `Display`=1, `Scale`=1, `Units`=kV, `Min`=-0.3, `Max`=0.4, `UseSignalName`=1, `enab`=1 |
| master:inductor  | | (120,7) | `L`=200 [uH] |
| master:peswitch  | | (118,9) | `L`=Q, `Type`=3, `INTR`=1, `RON`=1e-4 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=17 [kV], `Erw`=17 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:voltmeter `VL` | | (116,9) |  |
| master:peswitch  | | (116,7) | `L`=DH, `INTR`=1, `RON`=1e-4 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.2e-3 [kV], `EBO`=12 [kV], `Erw`=12 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:datalabel `GBoost` | | (120,11) | `datatype`=2, `index`=1 |
| master:datalabel `V_dc` | | (129,42) | `datatype`=2, `index`=1 |
| master:sumjct  | | (133,40) | `DPath`=1, `D`=1, `Dim`=1 |
| master:datalabel `GBoost` | | (158,46) | `datatype`=2, `index`=1 |
| master:datalabel `Ref_Boost` | | (150,40) | `datatype`=2, `index`=1 |
| master:datalabel `carr` | | (150,38) | `datatype`=2, `index`=1 |
| master:fp_int  | | (158,42) | `Type`=1, `Blck`=1, `max`=360.0, `min`=0.0, `PTime`=0.005 [s] |
| master:const  | | (144,36) | `Value`=5000, `Dim`=1 |
| master:sig_gen  | | (148,36) | `Max`=1.01 |
| master:datalabel `Vdc_Base` | | (129,40) | `datatype`=2, `index`=1 |
| master:ammeter `I_dc` | | (105,7) |  |
| master:datalabel `V_dc` | | (129,50) | `datatype`=2, `index`=1 |
| master:datalabel `I_dc` | | (132,52) | `datatype`=2, `index`=1 |
| master:mult  | | (132,50) | `DPath`=1, `Dim`=1 |
| master:realpole  | | (136,50) | `COM`=Real_Pole, `YO`=0.0, `Dim`=1, `G`=1.0, `T`=0.01 [s], `Max`=10.0, `Min`=-10.0 |
| master:datalabel `P_dc` | | (139,50) | `datatype`=2, `index`=1 |
| master:pgb `P_dc` | | (140,50) | `Display`=1, `Scale`=1, `Min`=-0.3, `Max`=0.4, `UseSignalName`=1, `enab`=1 |
| master:datalabel `DBlk` | | (158,36) | `datatype`=2, `index`=1 |
| master:inv  | | (137,37) | `const`=false |
| master:datalabel `DBlk` | | (136,37) | `datatype`=2, `index`=1 |
| SimpleSolarFarm:PI_AntiWindUp  | | (139,40) | `Kp`=0.1, `Ti`=0.1, `Kaw`=1, `MaxOut`=0.4, `MinOut`=0.0 |
| master:pgb `V_dc` | | (151,50) | `Display`=1, `Scale`=1, `Units`=kV, `Min`=-0.3, `Max`=0.4, `UseSignalName`=1, `enab`=1 |
| master:datalabel `V_dc` | | (148,50) | `datatype`=2, `index`=1 |
| master:pgb `Ref_Boost` | | (151,46) | `Display`=1, `Scale`=1, `Units`=kV, `Min`=-0.3, `Max`=0.4, `UseSignalName`=1, `enab`=1 |
| master:datalabel `Ref_Boost` | | (148,46) | `datatype`=2, `index`=1 |
| master:pgb `Ipv` | | (157,48) | `Display`=1, `Scale`=1, `Units`=kA, `Min`=-0.3, `Max`=0.4, `UseSignalName`=1, `enab`=1 |
| master:datalabel `Ipv` | | (154,48) | `datatype`=2, `index`=1 |
| master:datalabel `I_dc` | | (148,48) | `datatype`=2, `index`=1 |
| master:pgb `I_dc` | | (151,48) | `Display`=1, `Scale`=1, `Units`=kA, `Min`=-0.3, `Max`=0.4, `UseSignalName`=1, `enab`=1 |
| master:consti  | | (137,42) | `Dim`=1 |
| master:capacitor  | | (123,9) | `C`=1000 [uF] |
| master:sumjct  | | (145,40) | `DPath`=1, `D`=1, `Dim`=1 |
| master:datalabel `Vpv` | | (129,46) | `datatype`=2, `index`=1 |
| master:compare  | | (133,46) | `X`=0.75, `OL`=1, `Dim`=1, `conv`=1 |
| master:gain  | | (139,46) | `G`=0.2, `COM`=Gain, `Dim`=1, `DPath`=1 |
| master:unity  | | (137,46) | `IType`=1, `OType`=2, `Dim`=1, `const`=false |
| master:xnode `Pos` | | (134,11) |  |
| master:xnode `Neg` | | (134,17) |  |
| master:deadband  | | (97,75) | `Dim`=1, `deadband`=db_VRT, `offset`=0.0, `Gain`=m_VRT |
| master:current_scaler  | | (36,15) | `G_CDCS`=Scale, `Dim`=3 |
| master:resistor  | | (54,23) | `R`=1.0 [Mohm] |
| master:ground  | | (54,25) |  |
| master:ground  | | (61,22) |  |
| master:resistor  | | (61,20) | `R`=1.0 [Mohm] |

Wiring (absolute endpoints, intermediate vertices included):

- (105,13) -> (105,7)
- (105,15) -> (105,21)
- (78,11) -> (77,11)
- (78,9) -> (77,9)
- (78,19) -> (77,19)
- (78,17) -> (77,17)
- (85,11) -> (84,11)
- (85,9) -> (84,9)
- (85,19) -> (84,19)
- (85,17) -> (84,17)
- (92,11) -> (91,11)
- (92,9) -> (91,9)
- (92,19) -> (91,19)
- (92,17) -> (91,17)
- (77,11) -> (77,17)
- (84,11) -> (84,17)
- (91,11) -> (91,17)
- (77,9) -> (77,7) -> (84,7)
- (84,7) -> (84,9)
- (84,7) -> (91,7) -> (91,9)
- (91,19) -> (91,21) -> (84,21) -> (84,19)
- (84,21) -> (77,21) -> (77,19)
- (70,12) -> (77,12)
- (70,14) -> (84,14)
- (70,16) -> (91,16)
- (91,7) -> (103,7)
- (91,21) -> (100,21)
- (97,13) -> (97,7)
- (97,15) -> (97,21)
- (64,42) -> (66,42)
- (64,43) -> (66,43)
- (64,44) -> (66,44)
- (64,46) -> (66,46)
- (64,47) -> (66,47)
- (64,48) -> (66,48)
- (94,22) -> (94,21)
- (23,55) -> (22,55)
- (22,53) -> (27,53)
- (28,55) -> (27,55)
- (30,53) -> (31,53)
- (38,59) -> (35,59)
- (42,53) -> (39,53)
- (23,63) -> (21,63)
- (22,65) -> (29,65)
- (32,63) -> (31,63)
- (63,43) -> (63,41)
- (61,44) -> (58,44)
- (63,47) -> (63,45)
- (61,48) -> (60,48)
- (54,16) -> (54,14)
- (54,19) -> (54,20)
- (54,16) -> (52,16)
- (54,18) -> (52,18)
- (54,18) -> (54,19)
- (61,16) -> (61,14)
- (60,14) -> (62,14)
- (58,14) -> (56,14)
- (33,73) -> (32,73)
- (50,77) -> (49,77)
- (37,77) -> (41,77)
- (26,77) -> (33,77)
- (26,77) -> (26,80)
- (46,14) -> (45,14)
- (31,53) -> (35,53)
- (27,59) -> (22,59) -> (22,63)
- (56,14) -> (50,14)
- (29,48) -> (28,48)
- (105,21) -> (100,21)
- (106,7) -> (105,7)
- (106,21) -> (105,21)
- (29,14) -> (30,14)
- (106,7) -> (114,7)
- (106,21) -> (128,21)
- (20,53) -> (22,53)
- (18,53) -> (16,53)
- (19,55) -> (22,55)
- (61,103) -> (60,103)
- (67,87) -> (68,87)
- (66,48) -> (67,48)
- (66,47) -> (67,47)
- (66,46) -> (67,46)
- (71,46) -> (72,46)
- (72,48) -> (72,47) -> (71,47)
- (61,105) -> (61,103)
- (60,95) -> (64,95)
- (66,42) -> (67,42)
- (66,43) -> (67,43)
- (66,44) -> (67,44)
- (71,42) -> (72,42)
- (71,43) -> (72,43) -> (72,44)
- (72,38) -> (73,38)
- (72,42) -> (73,42)
- (72,44) -> (73,44)
- (72,46) -> (73,46)
- (72,48) -> (73,48)
- (56,56) -> (55,56)
- (76,54) -> (77,54)
- (68,56) -> (68,58)
- (76,56) -> (77,56)
- (81,56) -> (82,56)
- (81,63) -> (82,63)
- (76,63) -> (77,63)
- (68,63) -> (68,65)
- (76,61) -> (77,61)
- (56,63) -> (55,63)
- (61,91) -> (61,93)
- (60,91) -> (61,91)
- (72,95) -> (73,95)
- (73,91) -> (73,93) -> (72,93)
- (67,99) -> (68,99)
- (60,107) -> (64,107)
- (73,103) -> (73,105) -> (72,105)
- (72,107) -> (73,107)
- (87,59) -> (88,59)
- (88,61) -> (88,63)
- (88,65) -> (87,65) -> (87,59)
- (109,59) -> (110,59)
- (110,61) -> (110,63)
- (110,65) -> (109,65) -> (109,59)
- (98,59) -> (99,59)
- (99,61) -> (99,63)
- (99,65) -> (98,65) -> (98,59)
- (107,59) -> (106,59)
- (106,61) -> (106,63)
- (106,65) -> (107,65) -> (107,59)
- (118,59) -> (117,59)
- (117,61) -> (117,63)
- (117,65) -> (118,65) -> (118,59)
- (96,59) -> (95,59)
- (95,61) -> (95,63)
- (95,65) -> (96,65) -> (96,59)
- (92,42) -> (94,42)
- (92,40) -> (94,40)
- (98,42) -> (102,42)
- (102,38) -> (102,40)
- (106,42) -> (106,41) -> (107,41)
- (106,40) -> (107,40)
- (111,40) -> (113,40)
- (111,41) -> (112,41)
- (111,42) -> (112,42)
- (96,38) -> (95,38)
- (88,40) -> (87,40)
- (88,42) -> (87,42)
- (15,77) -> (16,77)
- (29,43) -> (31,43)
- (90,57) -> (115,57)
- (96,55) -> (98,55)
- (29,45) -> (31,45)
- (37,73) -> (39,73)
- (43,73) -> (43,75)
- (48,14) -> (50,14)
- (64,14) -> (66,14)
- (59,42) -> (58,42)
- (59,46) -> (58,46)
- (95,38) -> (93,38)
- (99,79) -> (101,79)
- (99,83) -> (101,83)
- (95,75) -> (95,83)
- (99,75) -> (101,75)
- (101,83) -> (101,82)
- (101,79) -> (101,80)
- (97,71) -> (103,71)
- (99,73) -> (98,73) -> (98,71)
- (105,75) -> (105,79) -> (107,79)
- (46,14) -> (46,18)
- (88,97) -> (89,97)
- (87,79) -> (88,79)
- (92,79) -> (93,79)
- (96,95) -> (95,95)
- (107,93) -> (106,93) -> (106,91)
- (106,91) -> (111,91)
- (106,91) -> (105,91)
- (37,40) -> (41,40) -> (41,38)
- (28,38) -> (29,38)
- (41,38) -> (42,38)
- (89,73) -> (90,73)
- (59,72) -> (61,72)
- (67,72) -> (65,72)
- (64,75) -> (62,75)
- (57,78) -> (58,78)
- (64,81) -> (62,81)
- (62,78) -> (62,79)
- (62,78) -> (62,77)
- (57,75) -> (58,75)
- (57,81) -> (58,81)
- (76,76) -> (76,74) -> (81,74)
- (80,76) -> (81,76)
- (76,76) -> (75,76)
- (71,74) -> (70,74)
- (71,76) -> (70,76)
- (71,80) -> (70,80)
- (71,82) -> (70,82)
- (76,80) -> (75,80)
- (80,80) -> (81,80)
- (76,80) -> (76,82) -> (81,82)
- (70,76) -> (70,77)
- (70,79) -> (70,80)
- (108,95) -> (109,95)
- (93,95) -> (93,97)
- (134,11) -> (130,11)
- (131,15) -> (131,17)
- (131,13) -> (131,11)
- (134,17) -> (128,17)
- (154,50) -> (157,50)
- (118,11) -> (118,21)
- (117,7) -> (120,7)
- (118,9) -> (118,7)
- (116,7) -> (117,7)
- (116,9) -> (118,9)
- (116,11) -> (118,11)
- (129,42) -> (133,42)
- (139,37) -> (139,38)
- (135,40) -> (137,40)
- (141,40) -> (143,40)
- (129,40) -> (131,40)
- (156,44) -> (155,44) -> (155,38)
- (156,40) -> (156,42)
- (150,38) -> (156,38)
- (147,40) -> (156,40)
- (150,36) -> (150,38)
- (129,50) -> (130,50)
- (138,50) -> (140,50)
- (137,37) -> (136,37)
- (148,50) -> (151,50)
- (148,46) -> (151,46)
- (154,48) -> (157,48)
- (148,48) -> (151,48)
- (128,7) -> (122,7)
- (123,9) -> (123,7)
- (123,11) -> (123,21)
- (141,46) -> (145,46) -> (145,42)
- (131,46) -> (129,46)
- (128,17) -> (128,21)
- (128,11) -> (128,7)
- (32,14) -> (34,14)
- (61,20) -> (61,19)

## Canvas `LCL_Filter`

Module ports: e1l(dim 3, Electrical), e1r(dim 3, Electrical)

| component | type | at | parameters |
| --- | --- | --- | --- |
| master:short  | | (18,10) |  |
| master:short  | | (13,14) |  |
| master:resistor  | | (16,16) | `R`=1.0 [Mohm] |
| master:ground  | | (16,18) |  |
| master:const `L` | | (12,28) | `Value`=125e-6, `Dim`=1 |
| master:varrlc  | | (9,6) | `RLC`=1, `R`=1.0 [ohm], `L`=Lfilter, `C`=1.0 [uF], `E`=0.0 [kV] |
| master:datalabel `Cfilter` | | (23,24) | `datatype`=2, `index`=1 |
| master:varrlc  | | (18,8) | `RLC`=2, `R`=1.0 [ohm], `L`=Filter_L, `C`=Cfilter, `E`=0.0 [kV] |
| master:datalabel `Lfilter` | | (16,28) | `datatype`=2, `index`=1 |
| master:div  | | (18,24) | `Dim`=1, `DPath`=1 |
| master:const  | | (14,24) | `Value`=1e5, `Dim`=1 |
| master:mult  | | (8,26) | `DPath`=1, `Dim`=1 |
| master:emtconst  | | (4,26) | `Value`=1, `Dim`=1 |
| master:square  | | (12,26) | `Dim`=1, `DPath`=1 |
| master:mult  | | (16,26) | `DPath`=1, `Dim`=1 |
| master:const `cutoff freq; 0.1 f PWM` | | (6,28) | `Value`=360, `Dim`=1 |
| master:varrlc  | | (13,12) | `RLC`=2, `R`=1.0 [ohm], `L`=Cdamp, `C`=Cdamp, `E`=0.0 [kV] |
| master:varrlc  | | (13,8) | `RLC`=1, `R`=1.0 [ohm], `L`=Ldamp, `C`=Cdamp, `E`=0.0 [kV] |
| master:varrlc  | | (11,10) | `R`=Rdamp, `L`=Ldamp, `C`=Cdamp, `E`=0.0 [kV] |
| master:gain  | | (21,28) | `G`=5.0, `COM`=Gain, `Dim`=1, `DPath`=1 |
| master:datalabel `Ldamp` | | (24,28) | `datatype`=2, `index`=1 |
| master:gain  | | (26,24) | `G`=0.5, `COM`=Gain, `Dim`=1, `DPath`=1 |
| master:datalabel `Cdamp` | | (29,24) | `datatype`=2, `index`=1 |
| master:div  | | (34,28) | `Dim`=1, `DPath`=1 |
| master:sqrt  | | (38,28) | `Dim`=1, `DPath`=1 |
| master:datalabel `Rdamp` | | (41,28) | `datatype`=2, `index`=1 |
| master:varrlc  | | (20,6) | `RLC`=1, `R`=1.0 [ohm], `L`=Lfilter, `C`=1.0 [uF], `E`=0.0 [kV] |
| master:const  | | (21,23) | `Value`=200, `Dim`=1 |
| master:ground  | | (59,15) |  |
| master:resistor  | | (59,13) | `R`=1.0 [Mohm] |
| master:short  | | (56,11) |  |
| master:filter-hp  | | (56,7) | `Q`=100.0, `Fo`=60.0 [Hz], `F`=300.0 [Hz], `MVAR`=100.0 [MVAR], `Volt`=132.79 [kV], `R`=2.5 [ohm], `L`=625 [uH], `C`=100 [uF] |
| master:short  | | (61,9) |  |
| master:capacitor  | | (61,7) | `C`=200 [uF] |
| master:inductor  | | (52,5) | `L`=125e-6 |
| master:inductor  | | (63,5) | `L`=125e-6 |
| master:xnode `e1r` | | (23,6) |  |
| master:xnode `e1l` | | (8,6) |  |
| master:annotation  | | (20,9) | `AL1`=in uF! |
| master:gain  | | (31,24) | `G`=1e-6, `COM`=Gain, `Dim`=1, `DPath`=1 |

Wiring (absolute endpoints, intermediate vertices included):

- (22,6) -> (23,6)
- (8,6) -> (9,6)
- (11,6) -> (20,6)
- (18,8) -> (18,6)
- (16,16) -> (16,15)
- (13,15) -> (18,15) -> (18,11)
- (13,10) -> (13,11)
- (13,10) -> (11,10)
- (13,8) -> (11,8)
- (13,11) -> (13,12)
- (14,28) -> (19,28)
- (24,28) -> (23,28)
- (24,24) -> (23,24)
- (29,24) -> (28,24)
- (24,28) -> (32,28)
- (41,28) -> (40,28)
- (13,8) -> (13,6)
- (56,12) -> (61,12) -> (61,10)
- (59,13) -> (59,12)
- (61,7) -> (61,5)
- (54,5) -> (63,5)
- (51,5) -> (52,5)
- (65,5) -> (66,5)
- (33,24) -> (34,24)
- (34,26) -> (34,24)
- (23,24) -> (20,24)

## Canvas `Rectifier`

Module ports: DC_P(dim 1, Electrical), RST(dim 3, Electrical), Pulses(dim 12, Input), DC_M(dim 1, Electrical)

| component | type | at | parameters |
| --- | --- | --- | --- |
| master:import `Pulses` | | (6,4) |  |
| master:datalabel `GG1` | | (13,18) | `datatype`=2, `index`=1 |
| master:datalabel `GG3` | | (20,18) | `datatype`=2, `index`=1 |
| master:datalabel `GG5` | | (27,18) | `datatype`=2, `index`=1 |
| master:datalabel `GG4` | | (13,26) | `datatype`=2, `index`=1 |
| master:datalabel `GG6` | | (20,26) | `datatype`=2, `index`=1 |
| master:datalabel `GG2` | | (27,26) | `datatype`=2, `index`=1 |
| master:xnode `DC_P` | | (38,14) |  |
| master:xnode `DC_M` | | (38,28) |  |
| master:xnode `RST` | | (4,21) |  |
| master:datatap  | | (10,5) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datalabel `GG1` | | (13,6) | `datatype`=2, `index`=1 |
| master:datatap  | | (11,5) | `Index`=2, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datalabel `GG2` | | (16,6) | `datatype`=2, `index`=1 |
| master:datalabel `GG3` | | (19,6) | `datatype`=2, `index`=1 |
| master:datalabel `GG4` | | (22,6) | `datatype`=2, `index`=1 |
| master:datalabel `GG5` | | (25,6) | `datatype`=2, `index`=1 |
| master:datalabel `GG6` | | (28,6) | `datatype`=2, `index`=1 |
| master:datamerge  | | (14,6) | `N`=2, `Type`=2, `Disp`=1, `Dim1`=1, `Dim2`=1, `Dim3`=1, `Dim4`=1, `Dim5`=1, `Dim6`=1, `Dim7`=1, `Dim8`=1, `Dim9`=1, `Dim10`=1, `Dim11`=1, `Dim12`=1 |
| master:datatap  | | (13,5) | `Index`=3, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (14,5) | `Index`=4, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datamerge  | | (17,6) | `N`=2, `Type`=2, `Disp`=1, `Dim1`=1, `Dim2`=1, `Dim3`=1, `Dim4`=1, `Dim5`=1, `Dim6`=1, `Dim7`=1, `Dim8`=1, `Dim9`=1, `Dim10`=1, `Dim11`=1, `Dim12`=1 |
| master:datatap  | | (16,5) | `Index`=5, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (17,5) | `Index`=6, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datamerge  | | (20,6) | `N`=2, `Type`=2, `Disp`=1, `Dim1`=1, `Dim2`=1, `Dim3`=1, `Dim4`=1, `Dim5`=1, `Dim6`=1, `Dim7`=1, `Dim8`=1, `Dim9`=1, `Dim10`=1, `Dim11`=1, `Dim12`=1 |
| master:datatap  | | (19,5) | `Index`=7, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (20,5) | `Index`=8, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datamerge  | | (23,6) | `N`=2, `Type`=2, `Disp`=1, `Dim1`=1, `Dim2`=1, `Dim3`=1, `Dim4`=1, `Dim5`=1, `Dim6`=1, `Dim7`=1, `Dim8`=1, `Dim9`=1, `Dim10`=1, `Dim11`=1, `Dim12`=1 |
| master:datatap  | | (22,5) | `Index`=9, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (23,5) | `Index`=10, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datamerge  | | (26,6) | `N`=2, `Type`=2, `Disp`=1, `Dim1`=1, `Dim2`=1, `Dim3`=1, `Dim4`=1, `Dim5`=1, `Dim6`=1, `Dim7`=1, `Dim8`=1, `Dim9`=1, `Dim10`=1, `Dim11`=1, `Dim12`=1 |
| master:datatap  | | (25,5) | `Index`=11, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (26,5) | `Index`=12, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datamerge  | | (29,6) | `N`=2, `Type`=2, `Disp`=1, `Dim1`=1, `Dim2`=1, `Dim3`=1, `Dim4`=1, `Dim5`=1, `Dim6`=1, `Dim7`=1, `Dim8`=1, `Dim9`=1, `Dim10`=1, `Dim11`=1, `Dim12`=1 |
| master:peswitch  | | (16,18) | `L`=D1, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=1.7 [kV], `Erw`=1.7 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:capacitor  | | (18,15) | `C`=1.41 [uF] |
| master:capacitor  | | (25,18) | `C`=1.41 [uF] |
| master:capacitor  | | (33,20) | `C`=1.41 [uF] |
| master:peswitch  | | (15,24) | `L`=Q4, `Type`=3, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=1.7 [kV], `Erw`=1.7 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF], `It`=IG4, `V`=VG4 |
| master:peswitch  | | (16,26) | `L`=D4, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=1.2 [kV], `Erw`=1.2 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (22,16) | `L`=Q3, `Type`=3, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=1.7 [kV], `Erw`=1.7 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (23,18) | `L`=D3, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=1.7 [kV], `Erw`=1.7 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (15,16) | `L`=Q1, `Type`=3, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=1.7 [kV], `Erw`=1.7 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF], `It`=IG1, `V`=VG1 |
| master:breakout  | | (6,21) |  |
| master:peswitch  | | (29,16) | `L`=Q3, `Type`=3, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=1.7 [kV], `Erw`=1.7 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (30,18) | `L`=D3, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=1.7 [kV], `Erw`=1.7 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (29,24) | `L`=Q3, `Type`=3, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=1.7 [kV], `Erw`=1.7 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (30,26) | `L`=D3, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=1.7 [kV], `Erw`=1.7 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (22,24) | `L`=Q3, `Type`=3, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=1.7 [kV], `Erw`=1.7 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |
| master:peswitch  | | (23,26) | `L`=D3, `INTR`=1, `RON`=2.5e-3 [ohm], `ROFF`=1.0E6 [ohm], `EFVD`=1.9e-3 [kV], `EBO`=1.7 [kV], `Erw`=1.7 [kV], `TEXT`=0.0 [usec], `RD`=5000.0 [ohm], `CD`=0.05 [uF] |

Wiring (absolute endpoints, intermediate vertices included):

- (16,18) -> (15,18)
- (16,16) -> (15,16)
- (16,26) -> (15,26)
- (16,24) -> (15,24)
- (23,18) -> (22,18)
- (23,16) -> (22,16)
- (23,26) -> (22,26)
- (23,24) -> (22,24)
- (30,18) -> (29,18)
- (30,16) -> (29,16)
- (30,26) -> (29,26)
- (30,24) -> (29,24)
- (15,18) -> (15,24)
- (22,18) -> (22,24)
- (29,18) -> (29,24)
- (15,16) -> (15,14) -> (22,14)
- (22,14) -> (22,16)
- (22,14) -> (29,14) -> (29,16)
- (29,26) -> (29,28) -> (22,28) -> (22,26)
- (22,28) -> (15,28) -> (15,26)
- (8,4) -> (25,4)
- (18,15) -> (18,14)
- (18,22) -> (18,28)
- (25,18) -> (25,14)
- (25,20) -> (25,28)
- (4,21) -> (6,21)
- (8,19) -> (15,19)
- (18,22) -> (18,17)
- (8,21) -> (22,21)
- (8,23) -> (29,23)
- (29,28) -> (38,28)
- (29,14) -> (38,14)
- (33,22) -> (33,28)
- (33,20) -> (33,14)

## Canvas `Main`

| component | type | at | parameters |
| --- | --- | --- | --- |
| master:ground  | | (175,1) |  |
| SimpleSolarFarm:VSC  | | (22,21) | `PFref`=PFref, `Qctrlmode`=Qctrlmode, `Pctrlmode`=Pctrlmode, `Vsrms_ref`=Vsrms_ref, `Ti_Vs`=Ti_Vs, `Kp_Vs`=Kp_Vs, `Ti_PLL`=Ti_PLL, `Kp_PLL`=Kp_PLL, `INV_Qmax`=INV_Qmax, `System_Freq`=60 [Hz], `INV_Vdcbase`=INV_Vdcbase, `INV_Vbase`=INV_Vbase, `INV_Sbase`=INV_Sbase, `Ti_Q`=Ti_Q, `Kp_Q`=Kp_Q, `IqMax`=1, `Tiq`=Tiq, `Kpq`=Kpq, `IdMax`=1, `Ti_dc`=Ti_dc, `Kp_dc`=Kp_dc, `Tid`=Tid, `Kpd`=Kpd, `VdcRef`=VdcRef, `Qref`=Qref, `Vdcref`=VdcRef, `Dblk`=DBlk, `Kp_P`=Kp_P, `Ti_P`=Ti_P, `Pref`=Pref, `Pmax`=0.88 [pu], `Pmin`=0 [pu], `Qmax`=0.6 [pu], `Pramp`=1.0 [pu/s], `Qramp`=1.0 [pu/s], `Vramp`=INV_VrampRate, `Iramp`=INV_IrampRate, `Vdcramp`=INV_VdcrampRate, `Sbase`=2.5 [MVA], `MV_Vbase`=33 [kV], `Scale`=50, `VRT_ENAB`=1, `db_VRT`=0.2 [pu], `m_VRT`=2.5, `db_P_f`=0.4 [Hz], `m_VRT_1`=2.5, `m_P_f`=0.45 [pu/Hz], `P_f_rate`=0.5 [pu/s], `rate_P_f`=0.5 [pu/s] |
| master:datalabel `DBlk` | | (46,24) | `datatype`=2, `index`=1 |
| master:var_switch `Deblock` | | (49,24) | `Display`=1, `Value`=1, `Max`=1, `Ton`=Deblk, `Toff`=Blk, `conv`=1 |
| master:var `Kpd` | | (32,48) | `Max`=200, `Min`=0.0, `Value`=0.1, `Collect`=1 |
| master:datalabel `Kpd` | | (35,48) | `datatype`=2, `index`=1 |
| master:var `Tid` | | (36,48) | `Max`=10, `Min`=0.0, `Value`=0.3, `Collect`=1 |
| master:datalabel `Tid` | | (39,48) | `datatype`=2, `index`=1 |
| master:var `Kpq` | | (40,48) | `Max`=200, `Min`=0.0, `Value`=0.1, `Collect`=1 |
| master:datalabel `Kpq` | | (43,48) | `datatype`=2, `index`=1 |
| master:var `Tiq` | | (44,48) | `Max`=10, `Min`=0.0, `Value`=0.3, `Collect`=1 |
| master:datalabel `Tiq` | | (47,48) | `datatype`=2, `index`=1 |
| master:var `Kp_Q` | | (24,48) | `Max`=20, `Min`=0.0, `Value`=1.0, `Collect`=1 |
| master:datalabel `Kp_Q` | | (27,48) | `datatype`=2, `index`=1 |
| master:var `Ti_Q` | | (28,48) | `Max`=100, `Min`=0.0, `Value`=0.02, `Collect`=1 |
| master:datalabel `Ti_Q` | | (31,48) | `datatype`=2, `index`=1 |
| master:datalabel `Ti_PLL` | | (15,48) | `datatype`=2, `index`=1 |
| master:var `Ti_PLL` | | (12,48) | `Max`=5000, `Min`=0.0, `Value`=1900.0, `Collect`=1 |
| master:datalabel `Kp_PLL` | | (11,48) | `datatype`=2, `index`=1 |
| master:var `Kp_PLL` | | (8,48) | `Max`=2000, `Min`=0.0, `Value`=950.0, `Collect`=1 |
| master:multimeter  | | (28,21) | `MeasV`=1, `MeasI`=1, `MeasP`=1, `MeasQ`=1, `RMS`=1, `S`=1, `BaseV`=33, `BaseA`=1.0, `TS`=0.02, `Freq`=60.0, `Dis`=1, `CurI`=Igrid_POC, `VolI`=Vgrid_POC, `P`=P_POC, `Q`=Q_POC, `Vrms`=Vrms_POC, `Pd`=0.0, `Qd`=0.0, `Vd`=0.0 |
| master:multimeter  | | (38,21) | `MeasP`=1, `MeasQ`=1, `RMS`=1, `S`=1, `BaseV`=33, `BaseA`=1.0, `TS`=0.02, `Freq`=60.0, `Dis`=1, `Pd`=0.0, `Qd`=0.0, `Vd`=0.0 |
| master:datalabel `Ti_P` | | (23,48) | `datatype`=2, `index`=1 |
| master:var `Ti_P` | | (20,48) | `Max`=100, `Min`=0.0, `Value`=0.02, `Collect`=1 |
| master:datalabel `Kp_P` | | (19,48) | `datatype`=2, `index`=1 |
| master:var `Kp_P` | | (16,48) | `Max`=20, `Min`=0.0, `Value`=1.0, `Collect`=1 |
| master:datalabel `DBlk` | | (23,18) | `datatype`=2, `index`=1 |
| master:ground  | | (45,21) |  |
| master:source3 `Source1` | | (43,21) | `Type`=4, `Ctrl`=2, `MVA`=100.0 [MVA], `Vm`=230.0 [kV], `F`=60.0 [Hz], `Tc`=0.05 [s], `Imp`=1, `View`=1, `R1s`=1.0 [ohm], `R1p`=1.0 [ohm], `L1p`=0.1 [H], `Z1`=1.0 [ohm], `Phi1`=80.0 [deg], `RN`=2.0, `R0p`=1.0 [ohm], `L0p`=0.1 [H], `R0s`=1.0 [ohm], `L0s`=0.0001 [H], `Z0`=1.0 [ohm], `Phi0`=80.0 [deg], `Es`=27 [kV], `F0`=60.0 [Hz], `Ph`=0.0 [deg], `Pinit`=0.0 [pu], `Qinit`=0.0 [pu], `Vdes`=1.0 [pu], `Vbase`=230.0 [kV], `Tvm`=0.02 [s], `Tvc`=0.05 [s], `Pdes`=1.0 [pu], `Tpm`=0.02 [s], `Tpc`=0.05 [s], `qset`=1, `PF_QMIN`=-1.0, `PF_QMAX`=1.0 |
| master:const  | | (41,17) | `Value`=0.0, `Dim`=1 |
| master:var `Vs` | | (51,19) | `Display`=1, `Max`=1.5, `Min`=0.0, `Value`=1.0, `Units`=pu, `Collect`=1 |
| master:gain  | | (47,19) | `G`=33, `Dim`=1, `DPath`=1 |
| SimpleSolarFarm:Simple_PPC  | | (22,28) | `Scale`=50, `Sbase`=2.5 [MVA], `untitled`=33 [kV], `con_mode`=1, `Ti_V`=PPC_Ti_V, `Kp_V`=PPC_Ti_V, `Ti_PF`=PPC_Ti_PF, `Kp_PF`=PPC_Kp_PF, `Ti_Q`=PPC_Ti_Q, `Kp_Q`=PPC_Kp_Q, `Vbase`=33 [kV], `Ti_P`=PPC_Ti_P, `Kp_P`=PPC_Kp_P, `HVRT`=1.15 [pu], `LVRT`=0.85 [pu], `Pmax`=1.0 [pu], `Pmin`=0.0 [pu], `Qmax`=0.6 [pu], `Qmin`=-0.6 [pu] |
| master:datalabel `DBlk` | | (22,33) | `datatype`=2, `index`=1 |
| master:datalabel `Vrms_POC` | | (29,29) | `datatype`=2, `index`=1 |
| master:datalabel `P_POC` | | (29,30) | `datatype`=2, `index`=1 |
| master:datalabel `Q_POC` | | (29,31) | `datatype`=2, `index`=1 |
| master:var `Vref` | | (11,26) | `Display`=1, `Max`=1.1, `Min`=0.0, `Value`=1.02, `Units`=pu, `Collect`=1 |
| master:const  | | (15,30) | `Value`=0.0, `Dim`=1 |
| master:const  | | (15,31) | `Value`=1.0, `Dim`=1 |
| master:var `Pref` | | (11,29) | `Display`=1, `Max`=110, `Min`=0.0, `Value`=100.0, `Units`=MW, `Collect`=1 |
| master:tpflt  | | (33,24) | `Grnd`=1, `View`=1, `CLVL`=0.0 [kA], `RON`=0.01 [ohm], `ROFF`=1.0E6 [ohm], `A`=1, `B`=1, `C`=1, `G`=1 |
| master:var `Freq` | | (43,17) | `Display`=1, `Max`=65, `Min`=45, `Value`=60.0, `Units`=Hz, `Collect`=1 |
| master:datalabel `Vgrid_POC` | | (50,3) | `datatype`=2, `index`=1 |
| master:pgb `Vgrid_POC` | | (53,3) | `UseSignalName`=1, `enab`=1, `Display`=1, `Scale`=1.0, `Max`=2.0, `Min`=-2.0 |
| master:pgb `Igrid_POC` | | (53,5) | `UseSignalName`=1, `enab`=1, `Display`=1, `Scale`=1.0, `Max`=2.0, `Min`=-2.0 |
| master:datalabel `Igrid_POC` | | (50,5) | `datatype`=2, `index`=1 |
| master:pgb `Vrms_POC` | | (53,7) | `UseSignalName`=1, `enab`=1, `Display`=1, `Scale`=1.0, `Max`=2.0, `Min`=-2.0 |
| master:datalabel `Vrms_POC` | | (50,7) | `datatype`=2, `index`=1 |
| master:pgb `P_POC` | | (53,9) | `UseSignalName`=1, `enab`=1, `Display`=1, `Scale`=1.0, `Max`=2.0, `Min`=-2.0 |
| master:datalabel `P_POC` | | (50,9) | `datatype`=2, `index`=1 |
| master:pgb `Q_POC` | | (53,11) | `UseSignalName`=1, `enab`=1, `Display`=1, `Scale`=1.0, `Max`=2.0, `Min`=-2.0 |
| master:datalabel `Q_POC` | | (50,11) | `datatype`=2, `index`=1 |
| master:var `PPC_Kp_P` | | (8,58) | `Max`=10.0, `Min`=0.0, `Value`=1.0, `Collect`=1 |
| master:datalabel `PPC_Kp_P` | | (12,58) | `datatype`=2, `index`=1 |
| master:datalabel `PPC_Ti_P` | | (12,60) | `datatype`=2, `index`=1 |
| master:var `PPC_Ti_P` | | (8,60) | `Max`=10.0, `Min`=0.0, `Value`=0.1, `Collect`=1 |
| master:var `PPC_Ti_V` | | (14,60) | `Max`=10.0, `Min`=0.0, `Value`=0.1, `Collect`=1 |
| master:datalabel `PPC_Ti_V` | | (18,60) | `datatype`=2, `index`=1 |
| master:datalabel `PPC_Kp_V` | | (18,58) | `datatype`=2, `index`=1 |
| master:var `PPC_Kp_V` | | (14,58) | `Max`=10.0, `Min`=0.0, `Value`=1.0, `Collect`=1 |
| master:var `PPC_Ti_PF` | | (20,60) | `Max`=10.0, `Min`=0.0, `Value`=0.1, `Collect`=1 |
| master:datalabel `PPC_Ti_PF` | | (24,60) | `datatype`=2, `index`=1 |
| master:datalabel `PPC_Kp_PF` | | (24,58) | `datatype`=2, `index`=1 |
| master:var `PPC_Kp_PF` | | (20,58) | `Max`=10.0, `Min`=0.0, `Value`=1.0, `Collect`=1 |
| master:var `PPC_Ti_Q` | | (26,60) | `Max`=10.0, `Min`=0.0, `Value`=0.1, `Collect`=1 |
| master:datalabel `PPC_Ti_Q` | | (30,60) | `datatype`=2, `index`=1 |
| master:datalabel `PPC_Kp_Q` | | (30,58) | `datatype`=2, `index`=1 |
| master:var `PPC_Kp_Q` | | (26,58) | `Max`=10.0, `Min`=0.0, `Value`=1.0, `Collect`=1 |
| master:tfaultn  | | (37,26) | `TF`=2.5 [s], `DF`=0.12 [s] |
| master:ratelimit  | | (9,19) | `IR`=400 [1/s], `DR`=400 [1/s], `COM`=C/s, `Dim`=1 |
| master:annotation  | | (14,17) | `AL1`=PV Array |
| master:ratelimit  | | (9,22) | `IR`=5 [1/s], `DR`=5 [1/s], `COM`=C/s, `Dim`=1 |
| master:var `Temperature` | | (3,22) | `Display`=1, `Max`=50, `Value`=25.0, `Units`=C, `Collect`=1 |
| master:var `Irradiation` | | (3,19) | `Display`=1, `Max`=1500, `Value`=1000.0, `Units`=W/m2, `Collect`=1 |
| master:photovoltaic_source2 `PVarray1` | | (14,21) | `Nsr`=18, `Npl`=377, `View1`=1, `Tnoc`=45.0, `Gref`=1000.0, `Tref`=25.0, `Pmax_mod`=385 [W], `Voc_mod`=48.9 [V], `Isc_mod`=10.14 [A], `Vmpp_mod`=40.3 [V], `Impp_mod`=9.56 [A], `NCsr`=54, `CT_Isc`=0.057, `CT_Voc`=-0.39, `Gnoc`=800.0, `Vocnoc_mod`=45.0 [V] |

Wiring (absolute endpoints, intermediate vertices included):

- (47,24) -> (46,24)
- (34,48) -> (35,48)
- (38,48) -> (39,48)
- (42,48) -> (43,48)
- (46,48) -> (47,48)
- (26,48) -> (27,48)
- (30,48) -> (31,48)
- (33,19) -> (33,24)
- (33,21) -> (29,21)
- (27,21) -> (25,21)
- (14,48) -> (15,48)
- (10,48) -> (11,48)
- (22,48) -> (23,48)
- (18,48) -> (19,48)
- (37,21) -> (33,21)
- (41,21) -> (39,21)
- (29,29) -> (27,29)
- (29,30) -> (27,30)
- (29,31) -> (27,31)
- (13,29) -> (17,29)
- (17,28) -> (14,28) -> (14,26) -> (13,26)
- (50,3) -> (53,3)
- (50,5) -> (53,5)
- (50,7) -> (53,7)
- (50,9) -> (53,9)
- (50,11) -> (53,11)
- (10,58) -> (12,58)
- (10,60) -> (12,60)
- (16,60) -> (18,60)
- (16,58) -> (18,58)
- (22,60) -> (24,60)
- (22,58) -> (24,58)
- (28,60) -> (30,60)
- (28,58) -> (30,58)
- (34,24) -> (33,24)
- (5,22) -> (7,22)
- (5,19) -> (7,19)
- (14,23) -> (14,24)
- (11,22) -> (12,22)
- (11,19) -> (12,19) -> (12,20)
- (14,19) -> (14,18)
- (14,24) -> (18,24) -> (18,22)
- (14,18) -> (18,18) -> (18,20)
