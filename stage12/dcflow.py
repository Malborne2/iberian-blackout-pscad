"""DC power flow of the ib6 network (IEEE-39 equivalent, base 410.4 MVA x KNET).
Gives the machine terminal angles Ph0 [rad] for a dispatch.  Lossless: a starting point,
refined from the locked-rotor run (stage12/README)."""
import numpy as np, sys
KNET = float(sys.argv[1]) if len(sys.argv) > 1 else 1.3
ZB = 400.0**2                     # ohm*MVA at 400 kV
# line id (last digits) -> (from, to); X from the pscx [ohm] (before KNET scaling)
LINES = {0:(13,14,3.938),3:(17,18,3.197),6:(23,24,13.645),9:(10,11,1.676),12:(10,13,1.676),
 15:(14,15,8.460),18:(15,16,3.665),21:(16,17,3.470),24:(16,19,7.602),27:(16,21,5.263),
 30:(16,24,2.300),33:(17,27,6.745),36:(1,2,16.022),39:(1,39,89.961),42:(21,22,5.458),
 45:(22,23,3.743),48:(25,26,12.593),51:(26,27,5.731),54:(26,28,18.480),57:(26,29,24.366),
 60:(28,29,5.887),63:(2,25,3.353),66:(2,3,5.887),69:(3,18,5.185),72:(3,4,8.304),
 75:(4,14,5.029),78:(4,5,4.990),81:(5,6,1.014),84:(5,8,4.366),87:(6,11,3.197),
 90:(6,7,3.587),93:(7,8,1.793),96:(8,9,14.152),99:(9,39,89.961)}
XF = [(2,30,.0181),(6,31,.025),(10,32,.02),(12,11,.0435),(12,13,.0435),(19,20,.0138),
      (19,33,.0142),(20,34,.018),(22,35,.0143),(23,36,.0272),(25,37,.0232),(29,38,.0156)]
TIES = {39, 99}
br = []
for k,(a,b,x) in LINES.items():
    br.append((a,b, x if k in TIES else x/KNET))
for a,b,x in XF:
    br.append((a,b, x*ZB/410.4/KNET))
# injections MW (+ = generation)
LOAD = {3:1792.5,4:2783.4,7:1301.5,8:2905.9,12:41.8,15:1781.4,16:1833.7,18:879.6,20:3785.5,
        21:1525.3,23:1377.8,24:1717.9,25:1247.0,26:773.8,27:1564.3,28:1146.8,29:1578.2,31:51.2,
        39:4530.8}
PLANT = {33:3412.0,34:2990.0,35:3789.0,36:3202.0,38:4760.0}
UNIT = {30:1528.9,31:3387.6,32:3823.5,37:3210.0}
HVDC = {9:-1000.0}
P = np.zeros(40)
for d,s in ((LOAD,-1),(PLANT,1),(UNIT,1),(HVDC,1)):
    for b,v in d.items(): P[b] += s*v
slack = 39
B = np.zeros((40,40))
for a,b,x in br:
    y = ZB/x                    # MW per rad
    B[a,a]+=y; B[b,b]+=y; B[a,b]-=y; B[b,a]-=y
idx = [i for i in range(1,40) if i != slack]
th = np.zeros(40)
th[idx] = np.linalg.solve(B[np.ix_(idx,idx)], P[idx])
ref = -0.17784                  # France Ph0 kept
th += ref
print(f"KNET {KNET}: Iberian gen {sum(UNIT.values())+sum(PLANT.values()):.0f} MW, load {sum(v for k,v in LOAD.items() if k!=39):.0f} + HVDC 1000")
print(f"France slack injection {-P[idx].sum():.0f} MW  -> France P0 (lossless) {LOAD[39]-(P[idx].sum()):.0f}")
for b in (30,31,32,37,39): print(f"  bus {b}: Ph0 = {th[b]:+.5f} rad ({np.degrees(th[b]):+.2f} deg)")
for b in (33,34,35,36,38,9,1): print(f"  bus {b}: angle {np.degrees(th[b]):+.2f} deg")
tie = sum(ZB/x*(th[a]-th[b]) for a,b,x in br if 39 in (a,b) and x>80)
print(f"tie flow Spain->France {tie:.0f} MW")
