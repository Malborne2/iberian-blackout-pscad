"""Pilot: build collector group C1 (GSU + 132 kV bus + RES + reactor + voltmeter).

Group origin (X, Y) in grid units.  Geometry learned from notes/probe_geom.py:
    xfmr-3p2w  G1=(X-1,Y+2)  G2=(X,Y+2)  N1=(X-3,Y)  N2=(X+2,Y)
    fixed_load IA=(x,y-1) [G port is internal]
    reactive_load A=(x,y)
    voltmeter  N1=(x,y)  N2=(x,y+2)
    ground     A=(x,y+1)
"""
import time, sys
import mhi.pscad as p

def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)

X = int(sys.argv[1]) if len(sys.argv) > 1 else 35
Y = int(sys.argv[2]) if len(sys.argv) > 2 else 112
TAG = sys.argv[3] if len(sys.argv) > 3 else 'C1'
TARGET = sys.argv[4] if len(sys.argv) > 4 else '26,35'

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

V2 = 132.0 / 1.03
P_RES = -4300.0 / 3.0        # per phase, negative = generation
VBO = 132.0 / 3 ** 0.5

def mk(tag, defn, x, y, **kw):
    c = main.create_component(defn, x, y, **kw)
    log('  +', tag, 'at', (x, y), 'ports',
        {k: tuple(v.location) for k, v in c.ports().items()})
    return c

log('group', TAG, 'at', (X, Y), 'target bus point', TARGET)

xf = mk('GSU', 'master:xfmr-3p2w', X, Y, Name='T_' + TAG, Tmva=5000.0, f=50.0,
        V1=400.0, V2=V2, Xl=0.12, YD1=0, YD2=0, Lead=1, Tap=0, Ideal=0, View=1)

bus = main.create_bus((X - 10, Y + 7), (X + 11, Y + 7))
log('  + 132 bus', bus)

res = mk('RES', 'master:fixed_load', X - 8, Y + 9, Name='RES_' + TAG,
         PO=P_RES, QO=0.0, VBO=VBO, VPU=1.0, FR=50.0, NP=0, NQ=0, PQdef=0)

rea = mk('REACT', 'master:reactive_load', X + 4, Y + 8, Name='REACT_' + TAG,
         S=250.0, V=132.0, F=50.0)

vm = mk('VM', 'master:voltmeter', X + 9, Y + 7, Name='V_' + TAG)

g1 = mk('GND1', 'master:ground', X - 4, Y - 1)
g2 = mk('GND2', 'master:ground', X + 3, Y - 1)
g3 = mk('GND3', 'master:ground', X + 9, Y + 10)

dl = mk('DL', 'master:datalabel', X + 9, Y + 14, Name='V_' + TAG)
pg = mk('PGB', 'master:pgb', X + 14, Y + 14, Name='V_' + TAG,
        UseSignalName='YES', Units='kV')

def conn(a, b, **kw):
    try:
        r = main.create_connection(a, b, **kw)
        log('    wire', a, '->', b, 'ok' if r is None else r)
    except Exception as e:
        log('    WIRE ERR', a, b, type(e).__name__, e)

# 400 kV side: electrical node label to the transmission bus
conn(xf.port('G1'), (int(TARGET.split(',')[0]), int(TARGET.split(',')[1])),
     label='ND_' + TAG, electrical=True)

# 132 kV side
conn(xf.port('G2'), (X, Y + 7))                 # GSU -> 132 kV bus
conn(res.port('IA'), (X - 8, Y + 7))            # RES injection -> bus
conn(rea.port('A'), (X + 4, Y + 7))             # reactor -> bus
conn(vm.port('N2'), g3.port('A'))               # voltmeter reference -> ground
conn(xf.port('N1'), g1.port('A'))               # neutral grounds
conn(xf.port('N2'), g2.port('A'))
conn(dl.port('A'), pg.port('Signl'))            # channel

pr.save()
log('saved')
