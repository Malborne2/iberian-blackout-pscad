"""Pilot: build ONE collector group at Bus1 and inspect the result."""
import time
import mhi.pscad as p

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

GX, GY = 22, 118
V2 = 132.0 / 1.03
S_TOT = 4300.0

xf = main.create_component('master:xfmr-3p2w', GX, GY, Name='T_C1', Tmva=5000.0, f=50.0,
                           V1=400.0, V2=V2, Xl=0.12, YD1=0, YD2=0, Lead=1, Tap=0, Ideal=0)
log('xf ports', {k: (v.x, v.y) for k, v in xf.ports().items()})

cb = main.create_bus((GX - 3, GY - 6), (GX + 3, GY - 6))
log('cb bounds', cb.bounds.left, cb.bounds.top, cb.bounds.right, cb.bounds.bottom)
log('cb ports', {k: (v.x, v.y) for k, v in cb.ports().items()})

res = main.create_component('master:fixed_load', GX - 7, GY - 11, Name='RES_C1',
                            PO=-S_TOT / 3, QO=0.0, VBO=132.0 / 3 ** 0.5, VPU=1.0,
                            FR=50.0, NP=0, NQ=0)
log('res ports', {k: (v.x, v.y) for k, v in res.ports().items()})

rea = main.create_component('master:reactive_load', GX + 5, GY - 11, Name='REACT_C1',
                            S=250.0, V=132.0, F=50.0)
log('rea ports', {k: (v.x, v.y) for k, v in rea.ports().items()})

vm = main.create_component('master:voltmeter', GX, GY - 9, Name='V_C1')
log('vm ports', {k: (v.x, v.y) for k, v in vm.ports().items()})

g1 = main.create_component('master:ground', GX - 6, GY)
g2 = main.create_component('master:ground', GX + 6, GY)
log('g ports', {k: (v.x, v.y) for k, v in g1.ports().items()})

def conn(a, b, **kw):
    try:
        r = main.create_connection(a, b, **kw)
        log('  conn ok', kw.get('label', ''), r)
    except Exception as e:
        log('  CONN ERR', type(e).__name__, e)

conn((24, 35), xf.port('G1'), label='ND_C1', electrical=True)
conn(xf.port('G2'), (GX - 3, GY - 6), label='C1_132', electrical=True)
conn(xf.port('N1'), g1.port('A'))
conn(xf.port('N2'), g2.port('A'))
pr.save()
log('saved')
