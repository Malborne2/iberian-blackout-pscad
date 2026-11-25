"""Collector group v3 - vertical GSU (orient 7), HV up / LV down, neutrals joined to
one ground, 400 kV connection by a pair of electrical node labels on two buses.

Usage: python notes/group_v3.py <X> <Y> <TAG> <target bus name>
"""
import time, sys
import mhi.pscad as p

def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)

X = int(sys.argv[1]); Y = int(sys.argv[2])
TAG = sys.argv[3]; TARGET = sys.argv[4]

# midpoint of each 400 kV bus, grid units (from notes/buses.py)
BUSPTS = {
    'Bus1': (26, 35), 'Bus2': (28, 27), 'Bus12': (43, 66),
    'Bus16': (50, 44), 'Bus22': (64, 51),
}

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

V2 = 132.0 / 1.03
P_RES = -4300.0 / 3.0
VBO = 132.0 / 3 ** 0.5

def show(tag, c):
    log('   ', tag, 'ports', {k: tuple(v.location) for k, v in c.ports().items()})

# ---- GSU, vertical (orient 7): winding #1 on top, #2 below ------------------
xf = main.create_component('master:xfmr-3p2w', X, Y, 7, Name='T_' + TAG, Tmva=5000.0,
                           f=50.0, V1=400.0, V2=V2, Xl=0.12, YD1=0, YD2=0,
                           Lead=1, Tap=0, Ideal=0, View=1)
show('GSU', xf)
P = {k: tuple(v.location) for k, v in xf.ports().items()}
g_top = min(P.items(), key=lambda kv: kv[1][1])[0]      # highest port = HV
g_bot = max(P.items(), key=lambda kv: kv[1][1])[0]      # lowest port = LV
log('    HV terminal', g_top, P[g_top], ' LV terminal', g_bot, P[g_bot])

# ---- buses ----------------------------------------------------------------
YH = Y - 6
YL = Y + 6
b400 = main.create_bus((X - 4, YH), (X + 6, YH))
b132 = main.create_bus((X - 6, YL), (X + 9, YL))
log('    buses at y', YH, YL)

# ---- shunt reactor, RES injection, voltmeter -------------------------------
res = main.create_component('master:fixed_load', X - 5, YL + 2, Name='RES_' + TAG,
                            PO=P_RES, QO=0.0, VBO=VBO, VPU=1.0, FR=50.0,
                            NP=0, NQ=0)
rea = main.create_component('master:reactive_load', X + 2, YL + 1, Name='REACT_' + TAG,
                            S=250.0, V=132.0, F=50.0)
vm = main.create_component('master:voltmeter', X + 7, YL, Name='V_' + TAG)
show('RES', res); show('REACT', rea); show('VM', vm)

# ---- one ground for the joined neutrals ------------------------------------
gnd = main.create_component('master:ground', X + 4, Y - 2)
show('GND', gnd)

# ---- channel --------------------------------------------------------------
dl = main.create_component('master:datalabel', X + 7, YL + 5, Name='V_' + TAG)
pg = main.create_component('master:pgb', X + 12, YL + 5, Name='V_' + TAG,
                           UseSignalName='YES', Units='kV')
show('DL', dl); show('PGB', pg)

def conn(a, b, **kw):
    try:
        r = main.create_connection(a, b, **kw)
        log('    wire', a if isinstance(a, tuple) else 'port', '->',
            b if isinstance(b, tuple) else 'port', 'ok' if r is None else r)
    except Exception as e:
        log('    WIRE ERR', type(e).__name__, e)

conn(P[g_top], (P[g_top][0], YH))              # HV -> 400 kV bus
conn(P[g_bot], (P[g_bot][0], YL))              # LV -> 132 kV bus

# neutrals: join the two neutral stubs, then ground at one point
neuts = [k for k in P if k.startswith('N')]
log('    neutral ports', [(k, P[k]) for k in neuts])
if len(neuts) == 2:
    n1, n2 = P[neuts[0]], P[neuts[1]]
    if n1[0] == n2[0]:
        conn(n1, n2)
    else:
        mid_y = min(n1[1], n2[1]) - 1
        conn(n1, (n1[0], mid_y))
        conn((n1[0], mid_y), (n2[0], mid_y))
        conn((n2[0], mid_y), n2)
    conn((n1[0], min(n1[1], n2[1]) - 1), gnd.port('A'))

conn(res.port('IA'), (res.port('IA').location[0], YL))
conn(rea.port('A'), (rea.port('A').location[0], YL))
conn(vm.port('N1'), (vm.port('N1').location[0], YL))
conn(dl.port('A'), pg.port('Signl'))

# ---- 400 kV connection by electrical node labels --------------------------
tpt = BUSPTS[TARGET]
log('    label connection ->', TARGET, tpt)
conn((X + 1, YH), tpt, label='ND_' + TAG, electrical=True)

pr.save()
log('saved')
