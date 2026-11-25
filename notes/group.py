"""Collector group - corrected port semantics.

xfmr-3p2w ports (verified):
    N1 / N2 = winding phase terminals   (3-dim, connect to the network)
    G1 / G2 = wye neutrals              (1-dim, join together and ground once)

Same layout as the shipped 33/34 transformers: orient 7 (vertical), #1 up, #2 down,
neutrals on the right.

Usage: python notes/group.py <X> <Y> <TAG> <target bus>
"""
import time, sys
import mhi.pscad as p

def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)

X = int(sys.argv[1]); Y = int(sys.argv[2])
TAG = sys.argv[3]; TARGET = sys.argv[4]

BUSPTS = {
    'Bus1': (26, 35), 'Bus2': (28, 27), 'Bus12': (43, 66),
    'Bus16': (50, 44), 'Bus22': (64, 51),
}
BASEKV = {'Bus1': 400, 'Bus2': 400, 'Bus12': 400, 'Bus16': 400, 'Bus22': 400}

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

V2 = 132.0 / 1.03
P_RES = -4300.0 / 3.0
VBO = 132.0 / 3 ** 0.5

def make(defn, x, y, orient=0, **kw):
    return main.create_component(defn, x, y, orient, **kw)

# ---- GSU ------------------------------------------------------------------
xf = make('master:xfmr-3p2w', X, Y, 7, Name='T_' + TAG, Tmva=5000.0, f=50.0,
          V1=400.0, V2=V2, Xl=0.12, YD1=0, YD2=0, Lead=1, Tap=0, Ideal=0, View=1)
P = {k: tuple(v.location) for k, v in xf.ports().items()}
log('GSU ports', P)

# ---- buses ----------------------------------------------------------------
YH, YL = Y - 6, Y + 6
b400 = main.create_bus((X - 4, YH), (X + 6, YH))
b132 = main.create_bus((X - 6, YL), (X + 9, YL))

# ---- equipment ------------------------------------------------------------
res = make('master:fixed_load', X - 5, YL + 2, Name='RES_' + TAG, PO=P_RES, QO=0.0,
           VBO=VBO, VPU=1.0, FR=50.0, NP=0, NQ=0)
rea = make('master:reactive_load', X + 3, YL + 1, Name='REACT_' + TAG,
           S=250.0, V=132.0, F=50.0)
vm = make('master:voltmeter', X + 8, YL + 1, Name='V_' + TAG)
gnd = make('master:ground', X + 2, Y - 1)                 # lands on G1
gnd2 = make('master:ground', X + 8, YL + 2)               # voltmeter reference
dl = make('master:datalabel', X + 8, YL + 5, Name='V_' + TAG)
pg = make('master:pgb', X + 13, YL + 5, Name='V_' + TAG, UseSignalName='YES', Units='kV')

def conn(a, b, **kw):
    try:
        r = main.create_connection(a, b, **kw)
        log('   wire', a if isinstance(a, tuple) else 'port',
            '->', b if isinstance(b, tuple) else 'port',
            '' if r is None else r)
        return True
    except Exception as e:
        log('   WIRE ERR', (a, b), type(e).__name__, e)
        return False

# ---- power circuit --------------------------------------------------------
conn(P['N1'], (X, YH))                 # HV phase terminal -> 400 kV bus
conn(P['N2'], (X, YL))                 # LV phase terminal -> 132 kV bus
conn(P['G1'], P['G2'])                 # join the two neutrals
# the ground sits directly on G1 (port coincidence), as in the shipped design
conn(res.port('IA'), (res.port('IA').location[0], YL))
conn(rea.port('A'), (rea.port('A').location[0], YL))
conn(vm.port('N1'), (vm.port('N1').location[0], YL))
conn(vm.port('N2'), gnd2.port('A'))
conn(dl.port('A'), pg.port('Signl'))

# ---- 400 kV connection ----------------------------------------------------
name = conn((X + 1, YH), BUSPTS[TARGET], label='ND_' + TAG, electrical=True)
log('   400 kV node label ->', TARGET, BUSPTS[TARGET], name)

pr.save()
log('saved')
