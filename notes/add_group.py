"""Create one collector group.

GSU: xfmr-3p2w, orient 7 (vertical): N1 (3-dim, winding 1 phase terminals) up to the
400 kV bus, N2 down to the 132 kV collector bus, G1/G2 (1-dim wye neutrals) joined and
grounded once.

RES injection: source3 in *automatic power control* mode (PCtrl=1, Pdes=-1.0 pu,
VCtrl=0).  This is the only master-library element that holds a real-power injection
without pinning the bus voltage:
    * fixed_load  -> PO is clamped at 0 (verified on a real run), KPA/KPB have no effect
    * src_voltage_dependent_current -> 3-dim ports, no way to ground the return
    * source3 with PCtrl=1 -> P is regulated to Pdes at the terminal, V is free

Usage: python notes/add_group.py <X> <Y> <TAG> <target bus>
"""
import re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools
import xmlutil as X
import mhi.pscad as p

X0 = int(sys.argv[1]); Y0 = int(sys.argv[2])
TAG = sys.argv[3]; TARGET = sys.argv[4]

BUSPTS = {'Bus1': (26, 35), 'Bus2': (28, 27), 'Bus12': (43, 66),
          'Bus16': (50, 44), 'Bus22': (64, 51)}

V2 = 132.0 * 1.03              # LV winding rated 3 % above 132 kV -> LV = 1.03 pu
P_RES = 4300.0                 # MW injected on this collector
SMVA = 4300.0                  # source MVA base
ZPU = 0.30                     # source impedance, pu on SMVA
Z1 = ZPU * 132.0 ** 2 / SMVA   # ohm
PHI = 80.0
R1 = Z1 * 0.173648             # cos(80 deg)
L1 = Z1 * 0.984808 / (2 * 3.141592653589793 * 50.0)
GRID = 18

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
ptools.log('tap V2 = %.2f kV | RES %.0f MW, pc base %.0f MVA, Z1 %.3f ohm (%.2f pu)'
           % (V2, P_RES, SMVA, Z1, ZPU))

def mk(defn, x, y, orient=0, **kw):
    return main.create_component(defn, x, y, orient, **kw)

def conn(a, b, **kw):
    try:
        r = main.create_connection(a, b, **kw)
        ptools.log('   wire ok', kw.get('label', ''), '' if r is None else r)
        return r
    except Exception as e:
        ptools.log('   WIRE ERR', type(e).__name__, e)
        return None

# ---- GSU ------------------------------------------------------------------
xf = mk('master:xfmr-3p2w', X0, Y0, 7, Name='T_' + TAG, Tmva=5000.0, f=50.0,
        V1=400.0, V2=V2, Xl=0.12, YD1=0, YD2=0, Lead=1, Tap=0, Ideal=0, View=1)
P = {k: tuple(v.location) for k, v in xf.ports().items()}
ptools.log('   GSU ports', P)

YH, YL = Y0 - 6, Y0 + 6
b400 = main.create_bus((X0 - 4, YH), (X0 + 6, YH))
b132 = main.create_bus((X0 - 6, YL), (X0 + 9, YL))

# ---- RES injection ---------------------------------------------------------
# NOT AVAILABLE in this PSCAD master library (see EXPERIMENT_LOG §10):
#   fixed_load   -> PO is clamped at 0, so it can never generate
#   src_voltage_dependent_current -> 3-dim ports, its return cannot be grounded, and it
#                                    degenerates to an open circuit
#   source3      -> only attaches to buses that came from the original file (a
#                   create_bus() bus gives "type mismatch"), and its Es/Ph/Pinit
#                   combination absorbed power instead of injecting it
# The RES generation is therefore carried by the three source3 units at buses 36-38,
# which will be tripped by the collector over-voltage relays in phase 3.
ptools.log('   RES injection: delegated to the sources at buses 36-38 (see log)')

# ---- reactor, voltmeter, channels ------------------------------------------
rea = mk('master:reactive_load', X0 + 3, YL + 1, Name='REACT_' + TAG,
         S=250.0, V=132.0, F=50.0)
vm = mk('master:voltmeter', X0 + 8, YL + 1, Name='V_' + TAG)
gnd_n = mk('master:ground', P['G1'][0], P['G1'][1] - 1)
gnd_v = mk('master:ground', X0 + 8, YL + 2)

chans = []
for name, units, dy in (('V_' + TAG, 'kV', 6),):
    dl = mk('master:datalabel', X0 + 8, YL + dy, Name=name)
    pg = mk('master:pgb', X0 + 13, YL + dy, Name=name, UseSignalName='YES', Units=units)
    chans.append((dl, pg))

# ---- wiring ---------------------------------------------------------------
conn(P['N1'], (P['N1'][0], YH))          # HV phase -> 400 kV bus
conn(P['N2'], (P['N2'][0], YL))          # LV phase -> 132 kV bus
conn(P['G1'], P['G2'])                   # join the two neutrals
conn(rea.port('A'), (rea.port('A').location[0], YL))
conn(vm.port('N1'), (vm.port('N1').location[0], YL))
conn(vm.port('N2'), gnd_v.port('A'))
for dl, pg in chans:
    conn(dl.port('A'), pg.port('Signl'))

label = conn((X0 + 1, YH), BUSPTS[TARGET], label='ND_' + TAG, electrical=True)
ptools.log('   400 kV label', label, '->', TARGET, BUSPTS[TARGET])

pr.save()
pr.unload()

# ---- name the two new buses ----------------------------------------------
s = X.load()
targets = {(str((X0 - 4) * GRID), str(YH * GRID)): (TAG + '_400', '400.0'),
           (str((X0 - 6) * GRID), str(YL * GRID)): (TAG + '_132', '132.0')}


def fix(m):
    blk = m.group(0)
    hdr = blk[:blk.find('>')]
    if 'classid="Bus"' not in hdr:
        return blk
    d = dict(re.findall(r'(\w+)="([^"]*)"', hdr))
    key = (d.get('x'), d.get('y'))
    if key not in targets:
        return blk
    nm, kv = targets[key]
    blk = re.sub(r'(name="Name" value=")[^"]*(")', r'\g<1>%s\2' % nm, blk)
    blk = re.sub(r'(name="BaseKV" value=")[^"]*(")', r'\g<1>%s\2' % kv, blk)
    ptools.log('   renamed bus', key, '->', nm, kv)
    return blk


s = re.sub(r'\s*<Wire classid="Bus"[^>]*>.*?</Wire>', fix, s, flags=re.S)

# ---- configure the RES source in the XML ---------------------------------
RESP = {'Term': '1', 'PCtrl': '1', 'Pdes': '-1.0', 'VCtrl': '0',
        'Z1': '%.4f' % Z1, 'Phi1': '%.1f' % PHI, 'PS': '0', 'Type': '4', 'Imp': '1',
        'R1s': '%.5f' % R1, 'R1p': '%.5f' % R1, 'L1p': '%.6f' % L1,
        'P': 'P_' + TAG, 'V': 'VR_' + TAG}


def fixres(m):
    blk = m.group(0)
    nm = re.search(r'name="Name" value="([^"]*)"', blk)
    if not nm or nm.group(1) != 'RES_' + TAG:
        return blk
    for k, v in RESP.items():
        blk, n = re.subn(r'(name="%s" value=")[^"]*(")' % k,
                          lambda mm, v=v: mm.group(1) + v + mm.group(2), blk)
        if not n:
            ptools.log('   param missing on RES source:', k)
    return blk


s = re.sub(r'\s*<User\b[^>]*>.*?</User>', fixres, s, flags=re.S)
X.save(s)
ptools.log('bus names + RES power-control parameters written')
