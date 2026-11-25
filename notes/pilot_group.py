"""Pilot: one collector group (GSU + 132 kV bus + RES + reactor + voltmeter)."""
import time, sys
import mhi.pscad as p

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

BASEV_LL = 400.0
COLL_LL = 132.0
TAP = 1.03
V2 = COLL_LL / TAP
S_TOT = 4300.0     # MW on this collector
Q_REACT = 250.0    # Mvar absorbed

xf = main.create_component('master:xfmr-3p2w', 100, 100, Name='T_C1', Tmva=5000.0, f=50.0,
                           V1=BASEV_LL, V2=V2, Xl=0.12, YD1='Y', YD2='Y',
                           Lead='Lags', Tap='None', Ideal='No', View='Single line (circles)')
log('xfmr ports', {k: (v.x, v.y) for k, v in xf.ports().items()})

bus = main.create_component('master:Bus', 98, 94, Name='C1', BaseKV=COLL_LL)
log('bus created', bus)

res = main.create_component('master:fixed_load', 92, 88, Name='RES_C1',
                            PO=-S_TOT / 3, QO=0.0, VBO=COLL_LL / 3 ** 0.5,
                            VPU=1.0, FR=50.0, NP=0, NQ=0, PQdef='Rated Voltage')
log('res ports', {k: (v.x, v.y) for k, v in res.ports().items()})

rea = main.create_component('master:reactive_load', 108, 88, Name='REACT_C1',
                            S=Q_REACT, V=COLL_LL, F=50.0, SD='Star')
log('rea ports', {k: (v.x, v.y) for k, v in rea.ports().items()})

vm = main.create_component('master:voltmeter', 100, 91, Name='V_C1')
gnd = main.create_component('master:ground', 103, 88)
log('vm ports', {k: (v.x, v.y) for k, v in vm.ports().items()})
log('gnd ports', {k: (v.x, v.y) for k, v in gnd.ports().items()})

dl = main.create_component('master:datalabel', 120, 91, Name='V_C1')
pg = main.create_component('master:pgb', 124, 91, Name='V_C1', UseSignalName='YES',
                           enab='YES', Display='YES', Units='kV', Scale=1.0, Min=0.0, Max=2.0)

def conn(a, b):
    r = main.create_connection(a, b)
    log('   conn', a, b, '->', r)

conn(bus.port('A') if 'A' in {k for k, _ in bus.ports().items()} else bus.ports(), xf.port('G2'))
conn(xf.port('G1'), bus.port('B') if 'B' in {k for k, _ in bus.ports().items()} else bus.ports())
conn(res.port('A'), res.port('G'))
conn(rea.port('A'), rea.port('G'))
conn(vm.port('N1'), vm.port('N2'))
conn(dl.port('A'), pg.port('Signl'))
pr.save()
log('saved')
