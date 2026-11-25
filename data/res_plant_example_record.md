# Example record: `statcom_6pls_pwm.pscx`

Source of every line below: the shipped `.pscx` itself (read-only, parsed offline).
Coordinates are PSCAD grid units. This is the specification to copy, not to improve
(PLAN F2 Stage 3, skill P9).

## Canvas `VControl`

Module ports: Qm(dim 1, Input), Vpu(dim 1, Input), Shft(dim 1, Output)

| component | type | at | parameters |
| --- | --- | --- | --- |
| master:var `Vref` | | (21,24) | `Group`=Voltage Reference, `Max`=1.5, `Min`=0.0, `Value`=1.0, `Units`=pu, `Collect`=1 |
| master:sumjct  | | (37,28) | `DPath`=1, `D`=1, `Dim`=1 |
| master:pi_ctlr  | | (47,28) | `GP`=Pgain, `TI`=Tconst, `YHI`=10.0, `YLO`=-10.0, `YINIT`=0.0, `Dim`=1 |
| master:var `Pgain` | | (35,31) | `Group`=PI Controller, `Max`=2.0, `Min`=0.0, `Value`=1.14, `Collect`=1 |
| master:datalabel `Tconst` | | (38,35) | `datatype`=2, `index`=1 |
| master:var `Tconst` | | (38,31) | `Group`=PI Controller, `Max`=1.0, `Min`=0.0, `Value`=0.1, `Collect`=1 |
| master:datalabel `Pgain` | | (35,35) | `datatype`=2, `index`=1 |
| master:pgb `AngleOrder` | | (58,28) | `Display`=1, `Scale`=1.0, `Units`=deg, `Min`=-40, `Max`=20, `enab`=1 |
| master:div  | | (22,13) | `Dim`=1, `DPath`=1 |
| master:const  | | (20,16) | `Value`=300.0, `Dim`=1 |
| master:div  | | (26,13) | `Dim`=1, `DPath`=1 |
| master:gain  | | (30,13) | `G`=0.03, `COM`=Gain, `Dim`=1, `DPath`=1 |
| master:time-sig  | | (23,28) |  |
| master:upramp  | | (27,28) | `X1`=0.0 [pu], `X2`=0.1 [pu], `Y2`=1.0 [pu], `COM`=Up_Ramp_X-fer_Func, `Dim`=1 |
| master:mult  | | (31,28) | `DPath`=1, `Dim`=1 |
| master:cmplx  | | (37,15) | `G`=1.0, `DR`=0.7, `F`=$(lpfreq), `LP`=1, `Dim`=1 |
| master:cmplx  | | (37,19) | `G`=1.0, `DR`=0.16, `F`=$(notchfreq), `HP`=1, `LP`=1, `Dim`=1 |
| master:cmplx  | | (37,23) | `G`=1.0, `DR`=0.16, `F`=$(freq), `HP`=1, `LP`=1, `Dim`=1 |
| master:maxmin  | | (24,19) | `DPath`=1, `Type`=1, `D`=1, `E`=1 |
| master:const  | | (20,21) | `Value`=0.1, `Dim`=1 |
| master:sumjct  | | (34,13) | `DPath`=1, `D`=1, `F`=1, `Dim`=1 |
| master:pgb `Vref` | | (34,28) | `Display`=1, `Scale`=1.0, `Units`=pu, `Max`=1.2, `enab`=1 |
| master:pgb `Verr` | | (40,28) | `Display`=1, `Scale`=1.0, `Units`=pu, `Min`=-0.5, `Max`=0.3, `enab`=1 |
| master:pgb `Vpu_filter` | | (40,23) | `Display`=1, `Scale`=1.0, `Units`=pu, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:gain  | | (52,28) | `G`=57.29578, `COM`=Gain, `Dim`=1, `DPath`=1 |
| master:leadlag  | | (43,28) | `COM`=Lead_Lag, `YO`=0.0, `G`=1.0, `T1`=0.007 [s], `T2`=0.0001 [s], `Max`=10.0, `Min`=-10.0, `Dim`=1 |
| master:import `Qm` | | (16,13) |  |
| master:import `Vpu` | | (16,19) |  |
| master:export `Shft` | | (58,30) |  |

Wiring (absolute endpoints, intermediate vertices included):

- (35,33) -> (35,35)
- (38,33) -> (38,35)
- (49,28) -> (50,28)
- (18,13) -> (20,13)
- (31,24) -> (23,24)
- (31,24) -> (31,26)
- (35,28) -> (33,28)
- (41,28) -> (39,28)
- (18,19) -> (22,19)
- (26,15) -> (26,19)
- (26,19) -> (34,19)
- (34,15) -> (34,19)
- (36,13) -> (37,13)
- (37,26) -> (37,25)
- (37,25) -> (40,25)
- (40,23) -> (40,25)
- (54,28) -> (58,28)
- (22,16) -> (22,15)
- (56,30) -> (56,28)

## Canvas `PWMControl`

Module ports: Shft(dim 1, Input)

| component | type | at | parameters |
| --- | --- | --- | --- |
| master:var `GpPLL` | | (17,20) | `Group`=PI Controller, `Max`=100.0, `Min`=0.0, `Value`=50.0, `Collect`=1 |
| master:datalabel `GiPLL` | | (20,24) | `datatype`=2, `index`=1 |
| master:var `GiPLL` | | (20,20) | `Group`=PI Controller, `Max`=1000.0, `Min`=0.0, `Value`=500.0, `Collect`=1 |
| master:datalabel `GpPLL` | | (17,24) | `datatype`=2, `index`=1 |
| master:tvekta  | | (30,24) | `Gp`=GpPLL, `Gi`=GiPLL, `Vbas`=100.0 [V], `Fbas`=$(freq), `PMode`=1, `THOFF`=0.0, `TREL`=0.05, `dlead`=1, `HiLimit`=1.2, `LoLimit`=0.8 |
| master:datalabel `Vnc` | | (26,26) | `datatype`=2, `index`=1 |
| master:datalabel `Vnb` | | (26,24) | `datatype`=2, `index`=1 |
| master:datalabel `Vna` | | (26,22) | `datatype`=2, `index`=1 |
| master:mult  | | (36,24) | `DPath`=1, `Dim`=1 |
| master:const  | | (34,21) | `Value`=33.0, `Dim`=1 |
| master:nl_tfun  | | (46,22) | `N`=4, `x1`=0.0, `y1`=0.0, `x2`=90.0, `y2`=1.0, `x3`=270.0, `y3`=-1.0, `x4`=360.0, `y4`=0.0, `x5`=0.0, `y5`=0.0, `x6`=1.0, `y6`=1.0, `x7`=2.0, `y7`=2.0, `x8`=3.0, `y8`=3.0, `x9`=4.0, `y9`=4.0, `x10`=5.0, `y10`=5.0, `Dim`=1 |
| master:pgb `TrgOn_1` | | (56,24) | `Display`=1, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datamerge  | | (54,22) | `N`=6, `Type`=2, `Disp`=1, `Dim1`=1, `Dim2`=1, `Dim3`=1, `Dim4`=1, `Dim5`=1, `Dim6`=1, `Dim7`=1, `Dim8`=1, `Dim9`=1, `Dim10`=1, `Dim11`=1, `Dim12`=1 |
| master:datatap  | | (56,24) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (59,24) | `Index`=4, `Dim`=1, `Type`=2, `Disp`=1 |
| master:nl_tfun  | | (46,26) | `N`=4, `x1`=0.0, `y1`=0.0, `x2`=90.0, `y2`=-1.0, `x3`=270.0, `y3`=1.0, `x4`=360.0, `y4`=0.0, `x5`=0.0, `y5`=0.0, `x6`=1.0, `y6`=1.0, `x7`=2.0, `y7`=2.0, `x8`=3.0, `y8`=3.0, `x9`=4.0, `y9`=4.0, `x10`=5.0, `y10`=5.0, `Dim`=1 |
| master:datatap  | | (56,32) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (59,32) | `Index`=4, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datamerge  | | (54,30) | `N`=6, `Type`=2, `Disp`=1, `Dim1`=1, `Dim2`=1, `Dim3`=1, `Dim4`=1, `Dim5`=1, `Dim6`=1, `Dim7`=1, `Dim8`=1, `Dim9`=1, `Dim10`=1, `Dim11`=1, `Dim12`=1 |
| master:datalabel `TrgOn` | | (62,25) | `datatype`=2, `index`=1 |
| master:datalabel `TrgOff` | | (62,33) | `datatype`=2, `index`=1 |
| master:pgb `TrgOn_4` | | (59,24) | `Display`=1, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:pgb `TrgOff_1` | | (56,32) | `Display`=1, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:pgb `TrgOff_4` | | (59,32) | `Display`=1, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datalabel `g1` | | (4,7) | `datatype`=2, `index`=1 |
| master:pgb `g1` | | (5,6) | `Group`=Gate Pulse, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datatap  | | (5,6) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datalabel `g1` | | (4,9) | `datatype`=2, `index`=1 |
| master:pgb `g1_int` | | (5,8) | `Group`=Gate Pulse, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datatap  | | (5,8) | `Index`=2, `Dim`=1, `Type`=2, `Disp`=1 |
| master:time-sig  | | (46,45) |  |
| master:datalabel `g2` | | (8,7) | `datatype`=2, `index`=1 |
| master:pgb `g2` | | (9,6) | `Group`=Gate Pulse, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datatap  | | (9,6) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datalabel `g2` | | (8,9) | `datatype`=2, `index`=1 |
| master:pgb `g2_int` | | (9,8) | `Group`=Gate Pulse, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datatap  | | (9,8) | `Index`=2, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datalabel `g3` | | (12,7) | `datatype`=2, `index`=1 |
| master:pgb `g3` | | (13,6) | `Group`=Gate Pulse, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datatap  | | (13,6) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datalabel `g3` | | (12,9) | `datatype`=2, `index`=1 |
| master:pgb `g3_int` | | (13,8) | `Group`=Gate Pulse, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datatap  | | (13,8) | `Index`=2, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datalabel `g6` | | (24,7) | `datatype`=2, `index`=1 |
| master:pgb `g6` | | (25,6) | `Group`=Gate Pulse, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datatap  | | (25,6) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datalabel `g6` | | (24,9) | `datatype`=2, `index`=1 |
| master:pgb `g6_int` | | (25,8) | `Group`=Gate Pulse, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datatap  | | (25,8) | `Index`=2, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datalabel `g4` | | (16,7) | `datatype`=2, `index`=1 |
| master:pgb `g4` | | (17,6) | `Group`=Gate Pulse, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datatap  | | (17,6) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datalabel `g4` | | (16,9) | `datatype`=2, `index`=1 |
| master:pgb `g4_int` | | (17,8) | `Group`=Gate Pulse, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datatap  | | (17,8) | `Index`=2, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datalabel `g5` | | (20,7) | `datatype`=2, `index`=1 |
| master:pgb `g5` | | (21,6) | `Group`=Gate Pulse, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datatap  | | (21,6) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datalabel `g5` | | (20,9) | `datatype`=2, `index`=1 |
| master:pgb `g5_int` | | (21,8) | `Group`=Gate Pulse, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datatap  | | (21,8) | `Index`=2, `Dim`=1, `Type`=2, `Disp`=1 |
| master:compare  | | (50,45) | `X`=0.1, `OH`=1, `Dim`=1, `conv`=1 |
| master:tvekta  | | (9,51) | `Gp`=GpPLL, `Gi`=GiPLL, `Vbas`=100.0 [V], `Fbas`=$(freq), `Mode`=1, `PMode`=1, `THOFF`=0.0, `TREL`=0.05, `dlead`=1, `HiLimit`=1.2, `LoLimit`=0.8 |
| master:datalabel `Vnc` | | (5,53) | `datatype`=2, `index`=1 |
| master:datalabel `Vnb` | | (5,51) | `datatype`=2, `index`=1 |
| master:datalabel `Vna` | | (5,49) | `datatype`=2, `index`=1 |
| master:datatap  | | (36,48) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:pgb `RefSgnOn_1` | | (36,48) | `Display`=1, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datatap  | | (39,48) | `Index`=4, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (25,50) | `Index`=4, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (25,51) | `Index`=5, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (25,52) | `Index`=6, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (25,53) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (25,54) | `Index`=2, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (25,55) | `Index`=3, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datamerge  | | (28,54) | `N`=6, `Type`=2, `Disp`=1, `Dim1`=1, `Dim2`=1, `Dim3`=1, `Dim4`=1, `Dim5`=1, `Dim6`=1, `Dim7`=1, `Dim8`=1, `Dim9`=1, `Dim10`=1, `Dim11`=1, `Dim12`=1 |
| master:datatap  | | (36,58) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (39,58) | `Index`=4, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datalabel `g1` | | (59,48) | `datatype`=2, `index`=1 |
| master:datalabel `g4` | | (59,54) | `datatype`=2, `index`=1 |
| master:datalabel `g6` | | (59,58) | `datatype`=2, `index`=1 |
| master:datalabel `g3` | | (59,52) | `datatype`=2, `index`=1 |
| master:datalabel `g2` | | (59,50) | `datatype`=2, `index`=1 |
| master:datalabel `g5` | | (59,56) | `datatype`=2, `index`=1 |
| master:fp_int  | | (54,56) | `Type`=1, `PNum`=1, `Blck`=1, `max`=360.0 [deg], `min`=0.0 [deg], `PTime`=0.005 [s] |
| master:sumjct  | | (15,58) | `DPath`=1, `D`=1, `Dim`=1 |
| master:const  | | (17,60) | `Value`=30.0, `Dim`=1 |
| master:datalabel `TrgOn` | | (50,52) | `datatype`=2, `index`=1 |
| master:datalabel `TrgOff` | | (50,56) | `datatype`=2, `index`=1 |
| statcom_6pls_pwm:PhaseShifter  | | (17,51) |  |
| master:datalabel `RSgnOn` | | (40,47) | `datatype`=2, `index`=1 |
| master:datalabel `RSgnOn` | | (50,50) | `datatype`=2, `index`=1 |
| master:datalabel `RSgnOff` | | (50,54) | `datatype`=2, `index`=1 |
| master:datalabel `RSgnOff` | | (40,57) | `datatype`=2, `index`=1 |
| master:pgb `RefSgnOn_4` | | (39,48) | `Display`=1, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:pgb `RefSgnOff_1` | | (36,58) | `Display`=1, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:pgb `RefSgnOff_4` | | (39,58) | `Display`=1, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:radiolink `Vn` | | (43,6) | `Source`=Main, `dim`=3, `Min`=-1.0, `Max`=1.0, `caption`=$(Name) [$(Rank)] |
| master:datalabel `g1` | | (52,6) | `datatype`=2, `index`=1 |
| master:datalabel `g4` | | (58,6) | `datatype`=2, `index`=1 |
| master:datalabel `g6` | | (58,10) | `datatype`=2, `index`=1 |
| master:datalabel `g3` | | (52,10) | `datatype`=2, `index`=1 |
| master:datalabel `g2` | | (52,8) | `datatype`=2, `index`=1 |
| master:datalabel `g5` | | (58,8) | `datatype`=2, `index`=1 |
| master:radiolink `g1` | | (54,6) | `Source`=Main, `dim`=2, `Mode`=1, `Min`=-1.0, `Max`=1.0, `caption`=$(Name) [$(Rank)] |
| master:radiolink `g2` | | (54,8) | `Source`=Main, `dim`=2, `Mode`=1, `Min`=-1.0, `Max`=1.0, `caption`=$(Name) [$(Rank)] |
| master:radiolink `g3` | | (54,10) | `Source`=Main, `dim`=2, `Mode`=1, `Min`=-1.0, `Max`=1.0, `caption`=$(Name) [$(Rank)] |
| master:radiolink `g4` | | (60,6) | `Source`=Main, `dim`=2, `Mode`=1, `Min`=-1.0, `Max`=1.0, `caption`=$(Name) [$(Rank)] |
| master:radiolink `g5` | | (60,8) | `Source`=Main, `dim`=2, `Mode`=1, `Min`=-1.0, `Max`=1.0, `caption`=$(Name) [$(Rank)] |
| master:radiolink `g6` | | (60,10) | `Source`=Main, `dim`=2, `Mode`=1, `Min`=-1.0, `Max`=1.0, `caption`=$(Name) [$(Rank)] |
| master:datatap  | | (45,7) | `Index`=1, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (47,7) | `Index`=2, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datatap  | | (49,7) | `Index`=3, `Dim`=1, `Type`=2, `Disp`=1 |
| master:datalabel `Vna` | | (45,7) | `datatype`=2, `index`=1 |
| master:datalabel `Vnb` | | (47,7) | `datatype`=2, `index`=1 |
| master:datalabel `Vnc` | | (49,7) | `datatype`=2, `index`=1 |
| master:import `Shft` | | (10,58) |  |
| master:trig  | | (30,57) | `Type`=1, `Mode`=1, `COM`=Trig-Func, `Dim`=6, `const`=false |
| master:trig  | | (30,47) | `Type`=1, `Mode`=1, `COM`=Trig-Func, `Dim`=6, `const`=false |
| master:angle_resolver  | | (40,24) | `IPUnit`=1, `OPUnit`=1, `OPRange`=1, `Dim`=1 |

Wiring (absolute endpoints, intermediate vertices included):

- (17,22) -> (17,24)
- (20,22) -> (20,24)
- (26,26) -> (28,26)
- (26,24) -> (28,24)
- (26,22) -> (28,22)
- (44,22) -> (44,26)
- (50,18) -> (53,18)
- (50,22) -> (53,22)
- (50,20) -> (53,20)
- (50,18) -> (50,20)
- (51,19) -> (51,26)
- (51,19) -> (53,19)
- (51,21) -> (53,21)
- (51,23) -> (53,23)
- (54,25) -> (62,25)
- (50,20) -> (50,22)
- (54,33) -> (62,33)
- (50,26) -> (53,26)
- (50,30) -> (53,30)
- (50,28) -> (53,28)
- (50,26) -> (48,26)
- (51,27) -> (51,31)
- (51,27) -> (53,27)
- (51,29) -> (53,29)
- (51,31) -> (53,31)
- (50,26) -> (50,30)
- (49,31) -> (51,31)
- (49,22) -> (49,31)
- (48,22) -> (50,22)
- (36,22) -> (36,21)
- (5,53) -> (7,53)
- (5,51) -> (7,51)
- (5,49) -> (7,49)
- (13,51) -> (14,51)
- (20,51) -> (22,51)
- (32,47) -> (40,47)
- (24,57) -> (24,51)
- (22,47) -> (22,57)
- (22,57) -> (24,57)
- (22,47) -> (28,47)
- (25,50) -> (27,50)
- (25,51) -> (27,51)
- (25,52) -> (27,52)
- (25,53) -> (27,53)
- (25,54) -> (27,54)
- (25,55) -> (27,55)
- (32,57) -> (40,57)
- (56,48) -> (59,48)
- (56,50) -> (59,50)
- (56,52) -> (59,52)
- (56,54) -> (59,54)
- (56,56) -> (59,56)
- (56,58) -> (59,58)
- (50,54) -> (52,54)
- (50,56) -> (52,56)
- (50,50) -> (52,50)
- (52,52) -> (50,52)
- (17,54) -> (17,58)
- (12,58) -> (13,58)
- (52,45) -> (54,45) -> (54,46)
- (52,6) -> (54,6)
- (52,8) -> (54,8)
- (52,10) -> (54,10)
- (58,6) -> (60,6)
- (58,8) -> (60,8)
- (58,10) -> (60,10)
- (43,6) -> (48,6)
- (42,24) -> (44,24)

## Canvas `Main` - Main Page

| component | type | at | parameters |
| --- | --- | --- | --- |
| master:source3 `src` | | (20,35) | `Type`=3, `MVA`=100.0 [MVA], `Vm`=115. [kV], `F`=$(freq), `Tc`=50e-6 [s], `Imp`=1, `View`=1, `R1s`=1.0 [ohm], `R1p`=1.0 [ohm], `L1p`=0.1 [H], `Z1`=26.45[ohm], `Phi1`=80.0 [deg], `RN`=2.0, `R0p`=1.0 [ohm], `L0p`=0.1 [H], `Z0`=1.0 [ohm], `Phi0`=80.0 [deg], `Es`=100. [kV], `F0`=$(freq), `Ph`=0.0 [deg], `Pinit`=0.0 [pu], `Qinit`=0.0 [pu], `Vdes`=1.0 [pu], `Vbase`=230.0 [kV], `Tvm`=0.02 [s], `Tvc`=0.05 [s], `Pdes`=1.0 [pu], `Tpm`=0.02 [s], `Tpc`=0.05 [s], `Ia`=ia, `Ib`=ib, `Ic`=ic, `R0s`=1.0 [ohm], `L0s`=0.0001 [H], `qset`=1, `PF_QMIN`=-1.0, `PF_QMAX`=1.0 |
| master:ground  | | (18,35) |  |
| master:resistor  | | (26,35) | `R`=0.1 [ohm] |
| master:ground  | | (37,37) |  |
| master:pgb `Active Power` | | (35,14) | `Group`=System, `Display`=1, `Scale`=1.0, `Units`=MW, `Min`=-40, `Max`=20, `enab`=1 |
| master:pgb `Reactive Power` | | (35,17) | `Group`=System, `Display`=1, `Scale`=1.0, `Units`=MVAR, `Min`=-50, `Max`=400, `enab`=1 |
| master:datalabel `dcCur` | | (43,20) | `datatype`=2, `index`=1 |
| master:pgb `DC Current` | | (45,20) | `Group`=STATCOM, `Display`=1, `Scale`=1.0, `Units`=kA, `Max`=300, `enab`=1 |
| master:datalabel `Idi1` | | (38,10) | `datatype`=2, `index`=1 |
| master:pgb `Diode Currents` | | (45,11) | `Group`=STATCOM, `Display`=1, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:ground  | | (54,43) |  |
| master:datalabel `g1` | | (44,31) | `datatype`=2, `index`=1 |
| master:datalabel `g2` | | (54,41) | `datatype`=2, `index`=1 |
| master:datalabel `g3` | | (49,31) | `datatype`=2, `index`=1 |
| master:datalabel `g4` | | (44,41) | `datatype`=2, `index`=1 |
| master:datalabel `g5` | | (54,31) | `datatype`=2, `index`=1 |
| master:datalabel `g6` | | (49,41) | `datatype`=2, `index`=1 |
| master:peswitch  | | (46,29) | `L`=1, `Type`=2, `SNUB`=1, `INTR`=1, `RON`=0.005 [ohm], `ROFF`=1.0E8 [ohm], `EFVD`=0.0 [kV], `EBO`=1.0E5 [kV], `Erw`=1.0E5 [kV], `TEXT`=0.0 [us], `RD`=5000.0 [ohm], `CD`=0.05 [uF], `I`=Igto1, `V`=Vgto1 |
| master:peswitch  | | (48,31) | `INTR`=1, `RON`=0.005[ohm], `ROFF`=1.0E8 [ohm], `EFVD`=0.0 [kV], `EBO`=1.0E5 [kV], `Erw`=1.0E5 [kV], `TEXT`=0.0 [us], `RD`=5000.0 [ohm], `CD`=0.05 [uF], `I`=Idi1 |
| master:capacitor  | | (61,36) | `C`=300.0 [uF] |
| master:peswitch  | | (51,29) | `L`=3, `Type`=2, `SNUB`=1, `INTR`=1, `RON`=0.005 [ohm], `ROFF`=1.0E8 [ohm], `EFVD`=0.0 [kV], `EBO`=1.0E5 [kV], `Erw`=1.0E5 [kV], `TEXT`=0.0 [us], `RD`=5000.0 [ohm], `CD`=0.05 [uF], `I`=Igto3 |
| master:peswitch  | | (53,31) | `INTR`=1, `RON`=0.005[ohm], `ROFF`=1.0E8 [ohm], `EFVD`=0.0 [kV], `EBO`=1.0E5 [kV], `Erw`=1.0E5 [kV], `TEXT`=0.0 [us], `RD`=5000.0 [ohm], `CD`=0.05 [uF], `I`=Idi3 |
| master:peswitch  | | (56,29) | `L`=5, `Type`=2, `SNUB`=1, `INTR`=1, `RON`=0.005 [ohm], `ROFF`=1.0E8 [ohm], `EFVD`=0.0 [kV], `EBO`=1.0E5 [kV], `Erw`=1.0E5 [kV], `TEXT`=0.0 [us], `RD`=5000.0 [ohm], `CD`=0.05 [uF], `I`=Igto5 |
| master:peswitch  | | (58,31) | `INTR`=1, `RON`=0.005[ohm], `ROFF`=1.0E8 [ohm], `EFVD`=0.0 [kV], `EBO`=1.0E5 [kV], `Erw`=1.0E5 [kV], `TEXT`=0.0 [us], `RD`=5000.0 [ohm], `CD`=0.05 [uF], `I`=Idi5 |
| master:peswitch  | | (46,39) | `L`=4, `Type`=2, `SNUB`=1, `INTR`=1, `RON`=0.005 [ohm], `ROFF`=1.0E8 [ohm], `EFVD`=0.0 [kV], `EBO`=1.0E5 [kV], `Erw`=1.0E5 [kV], `TEXT`=0.0 [us], `RD`=5000.0 [ohm], `CD`=0.05 [uF], `I`=Igto4, `V`=Vgto4 |
| master:peswitch  | | (48,41) | `INTR`=1, `RON`=0.005[ohm], `ROFF`=1.0E8 [ohm], `EFVD`=0.0 [kV], `EBO`=1.0E5 [kV], `Erw`=1.0E5 [kV], `TEXT`=0.0 [us], `RD`=5000.0 [ohm], `CD`=0.05 [uF], `I`=Idi4 |
| master:peswitch  | | (51,39) | `L`=6, `Type`=2, `SNUB`=1, `INTR`=1, `RON`=0.005 [ohm], `ROFF`=1.0E8 [ohm], `EFVD`=0.0 [kV], `EBO`=1.0E5 [kV], `Erw`=1.0E5 [kV], `TEXT`=0.0 [us], `RD`=5000.0 [ohm], `CD`=0.05 [uF], `I`=Igto6 |
| master:peswitch  | | (53,41) | `INTR`=1, `RON`=0.005[ohm], `ROFF`=1.0E8 [ohm], `EFVD`=0.0 [kV], `EBO`=1.0E5 [kV], `Erw`=1.0E5 [kV], `TEXT`=0.0 [us], `RD`=5000.0 [ohm], `CD`=0.05 [uF], `I`=Idi6 |
| master:peswitch  | | (56,39) | `L`=2, `Type`=2, `SNUB`=1, `INTR`=1, `RON`=0.005 [ohm], `ROFF`=1.0E8 [ohm], `EFVD`=0.0 [kV], `EBO`=1.0E5 [kV], `Erw`=1.0E5 [kV], `TEXT`=0.0 [us], `RD`=5000.0 [ohm], `CD`=0.05 [uF], `I`=Igto2 |
| master:peswitch  | | (58,41) | `INTR`=1, `RON`=0.005[ohm], `ROFF`=1.0E8 [ohm], `EFVD`=0.0 [kV], `EBO`=1.0E5 [kV], `Erw`=1.0E5 [kV], `TEXT`=0.0 [us], `RD`=5000.0 [ohm], `CD`=0.05 [uF], `I`=Idi2 |
| master:datalabel `dcVltg` | | (43,17) | `datatype`=2, `index`=1 |
| master:pgb `DC Voltage` | | (45,17) | `Group`=STATCOM, `Display`=1, `Scale`=1.0, `Units`=kV, `Max`=60, `enab`=1 |
| master:datalabel `Igto4` | | (41,6) | `datatype`=2, `index`=1 |
| master:datalabel `Idi4` | | (41,9) | `datatype`=2, `index`=1 |
| master:datalabel `Igto1` | | (38,7) | `datatype`=2, `index`=1 |
| master:pgb `GTO Currents` | | (45,8) | `Group`=STATCOM, `Display`=1, `Scale`=1.0, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datalabel `Igto3` | | (40,7) | `datatype`=2, `index`=1 |
| master:datalabel `Igto6` | | (43,6) | `datatype`=2, `index`=1 |
| master:datalabel `Igto5` | | (42,7) | `datatype`=2, `index`=1 |
| master:datalabel `Igto2` | | (39,6) | `datatype`=2, `index`=1 |
| master:datalabel `Qm` | | (33,17) | `datatype`=2, `index`=1 |
| master:ammeter `IL` | | (22,32) |  |
| master:ground  | | (16,32) |  |
| master:tpflt  | | (19,44) | `Grnd`=1, `View`=1, `CLVL`=0.0 [kA], `RON`=0.01 [ohm], `ROFF`=1.0E6 [ohm], `A`=1, `B`=1, `C`=1, `G`=1, `Ifla`=Ifa, `Iflb`=Ifb, `Iflc`=Ifc |
| master:tfault  | | (23,46) | `TF`=1.5[s], `DF`=0.75 [s] |
| master:pgb `RMS Voltage` | | (35,20) | `Group`=System, `Display`=1, `Scale`=1.0, `Units`=pu, `Max`=1.2, `enab`=1 |
| master:datalabel `Vpu` | | (33,20) | `datatype`=2, `index`=1 |
| master:pgb `Fault Currents` | | (45,14) | `Group`=System, `Display`=1, `Scale`=1.0, `Units`=kA, `Min`=-2.0, `Max`=2.0, `enab`=1 |
| master:datalabel `Ifa` | | (41,13) | `datatype`=2, `index`=1 |
| master:datalabel `Ifb` | | (42,13) | `datatype`=2, `index`=1 |
| master:datalabel `Ifc` | | (43,13) | `datatype`=2, `index`=1 |
| master:resistor  | | (20,38) | `R`=53.033 [ohm] |
| master:inductor  | | (20,42) | `L`=0.14067 [H] |
| master:resistor  | | (20,32) | `R`=135.9462 [ohm] |
| master:inductor  | | (16,32) | `L`=0.168154 [H] |
| master:datalabel `Idi2` | | (39,9) | `datatype`=2, `index`=1 |
| master:datalabel `Idi3` | | (40,10) | `datatype`=2, `index`=1 |
| master:datalabel `Idi5` | | (42,10) | `datatype`=2, `index`=1 |
| master:datalabel `Idi6` | | (43,9) | `datatype`=2, `index`=1 |
| master:pin  | | (46,33) |  |
| master:pin  | | (51,35) |  |
| master:pin  | | (56,37) |  |
| master:capacitor  | | (32,36) | `C`=2.0 [uF] |
| statcom_6pls_pwm:PWMControl  | | (11,21) |  |
| statcom_6pls_pwm:VControl  | | (7,21) |  |
| master:datalabel `g1` | | (54,6) | `datatype`=2, `index`=1 |
| master:datalabel `g4` | | (54,12) | `datatype`=2, `index`=1 |
| master:datalabel `g6` | | (54,16) | `datatype`=2, `index`=1 |
| master:datalabel `g3` | | (54,10) | `datatype`=2, `index`=1 |
| master:datalabel `g2` | | (54,8) | `datatype`=2, `index`=1 |
| master:datalabel `g5` | | (54,14) | `datatype`=2, `index`=1 |
| master:radiolink `g1` | | (56,6) | `Source`=PWMControl, `dim`=2, `Min`=-1.0, `Max`=1.0, `caption`=$(Name) [$(Rank)] |
| master:radiolink `g2` | | (56,8) | `Source`=PWMControl, `dim`=2, `Min`=-1.0, `Max`=1.0, `caption`=$(Name) [$(Rank)] |
| master:radiolink `g3` | | (56,10) | `Source`=PWMControl, `dim`=2, `Min`=-1.0, `Max`=1.0, `caption`=$(Name) [$(Rank)] |
| master:radiolink `g4` | | (56,12) | `Source`=PWMControl, `dim`=2, `Min`=-1.0, `Max`=1.0, `caption`=$(Name) [$(Rank)] |
| master:radiolink `g5` | | (56,14) | `Source`=PWMControl, `dim`=2, `Min`=-1.0, `Max`=1.0, `caption`=$(Name) [$(Rank)] |
| master:radiolink `g6` | | (56,16) | `Source`=PWMControl, `dim`=2, `Min`=-1.0, `Max`=1.0, `caption`=$(Name) [$(Rank)] |
| master:datalabel `Vpu` | | (3,22) | `datatype`=2, `index`=1 |
| master:radiolink `Vn` | | (56,19) | `Source`=Main, `dim`=3, `Mode`=1, `Min`=-1.0, `Max`=1.0, `caption`=$(Name) [$(Rank)] |
| master:datalabel `Vn` | | (54,19) | `datatype`=2, `index`=1 |
| master:breakout  | | (40,35) |  |
| master:ground  | | (32,38) |  |
| master:multimeter  | | (29,35) | `MeasV`=1, `MeasP`=1, `MeasQ`=1, `RMS`=1, `S`=1.0 [MVA], `BaseV`=115.0 [kV], `TS`=0.01 [s], `Freq`=$(freq), `VolI`=Vn, `P`=Pm, `Q`=Qm, `Vrms`=Vpu, `Pd`=0.0, `Qd`=0.0, `Vd`=0.0, `BaseA`=1.0 |
| master:datalabel `Pm` | | (33,14) | `datatype`=2, `index`=1 |
| master:multimeter  | | (61,28) | `MeasI`=1, `MeasV`=1, `S`=1.0 [MVA], `BaseV`=115.0 [kV], `TS`=0.01 [s], `Freq`=$(freq), `CurI`=dcCur, `VolI`=dcVltg, `P`=Pm, `Q`=Qm, `Vrms`=Vpu, `Pd`=0.0, `Qd`=0.0, `Vd`=0.0, `BaseA`=1.0 |
| master:datalabel `qm` | | (3,20) | `datatype`=2, `index`=1 |
| master:datamerge  | | (42,8) | `N`=6, `Type`=2, `Dim1`=1, `Dim2`=1, `Dim3`=1, `Dim4`=1, `Dim5`=1, `Dim6`=1, `Dim7`=1, `Dim8`=1, `Dim9`=1, `Dim10`=1, `Dim11`=1, `Dim12`=1 |
| master:datamerge  | | (42,11) | `N`=6, `Type`=2, `Dim1`=1, `Dim2`=1, `Dim3`=1, `Dim4`=1, `Dim5`=1, `Dim6`=1, `Dim7`=1, `Dim8`=1, `Dim9`=1, `Dim10`=1, `Dim11`=1, `Dim12`=1 |
| master:datamerge  | | (45,14) | `N`=3, `Type`=2, `Dim1`=1, `Dim2`=1, `Dim3`=1, `Dim4`=1, `Dim5`=1, `Dim6`=1, `Dim7`=1, `Dim8`=1, `Dim9`=1, `Dim10`=1, `Dim11`=1, `Dim12`=1 |
| master:xfmr_3p2w `tr` | | (38,35) | `ModType`=1, `View`=1, `Tmva`=100.0 [MVA], `f`=$(freq), `YD2`=1, `YD2_VG`=11, `V1`=115 [kV], `V2`=25.0 [kV], `V1ph`=132.79 [kV], `V2ph`=132.79 [kV], `NLL`=0.0 [pu], `Im1`=1.0 [%], `CuL`=0.0 [pu], `Xl`=0.1 [pu], `Xair`=0.2 [pu], `Xknee`=1.17 [pu], `LW2`=10 [%], `Bnom`=1.7 [T], `material`=1, `Fremn1`=0.0 [pu], `Fremn2`=0.0 [pu], `Fremn3`=0.0 [pu], `C`=0.1, `K`=5.0e-5 [A/m], `BETA`=0.96, `alpha`=1.325e-5, `Msat`=1.72e6 [A/m], `F1`=2730, `F2`=3209, `F3`=20294, `Fb`=2, `ILA1`=Itfpa, `ILB1`=Itfpb, `ILC1`=Itfpc |

Wiring (absolute endpoints, intermediate vertices included):

- (30,35) -> (35,35)
- (22,35) -> (24,35)
- (42,33) -> (46,33)
- (42,35) -> (51,35)
- (42,37) -> (56,37)
- (46,29) -> (46,27) -> (61,27)
- (43,20) -> (45,20)
- (51,29) -> (51,27)
- (56,29) -> (56,27)
- (46,39) -> (46,31)
- (51,39) -> (51,31)
- (56,39) -> (56,31)
- (46,41) -> (46,43) -> (61,43) -> (61,36)
- (51,43) -> (51,41)
- (56,43) -> (56,41)
- (51,31) -> (53,31)
- (51,29) -> (53,29)
- (56,31) -> (58,31)
- (56,29) -> (58,29)
- (46,41) -> (48,41)
- (46,39) -> (48,39)
- (51,41) -> (53,41)
- (51,39) -> (53,39)
- (56,41) -> (58,41)
- (56,39) -> (58,39)
- (46,31) -> (48,31)
- (46,29) -> (48,29)
- (43,17) -> (45,17)
- (20,38) -> (22,38)
- (35,20) -> (33,20)
- (33,17) -> (35,17)
- (33,14) -> (35,14)
- (32,35) -> (32,36)
- (54,6) -> (56,6)
- (54,8) -> (56,8)
- (54,10) -> (56,10)
- (54,12) -> (56,12)
- (54,14) -> (56,14)
- (54,16) -> (56,16)
- (3,22) -> (5,22)
- (56,19) -> (54,19)
- (26,35) -> (28,35)
- (22,31) -> (22,39)
- (20,40) -> (20,42)
- (61,29) -> (61,34)
- (3,20) -> (5,20)
- (41,7) -> (41,6)
- (39,7) -> (39,6)
- (43,7) -> (43,6)
- (41,10) -> (41,9)
- (39,10) -> (39,9)
- (43,10) -> (43,9)
