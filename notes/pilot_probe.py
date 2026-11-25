import time
import mhi.pscad as p

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

xf = main.create_component('master:xfmr-3p2w', 100, 100, Name='T_C1', Tmva=5000.0, f=50.0,
                           V1=400.0, V2=128.155, Xl=0.12, YD1='Y', YD2='Y',
                           Lead='Lags', Tap='None', Ideal='No')
log('xfmr', {k: (v.x, v.y) for k, v in xf.ports().items()})

bus = main.create_component('master:Bus', 98, 94, Name='C1', BaseKV=132.0)
log('bus', type(bus).__name__, [(k, (v.x, v.y)) for k, v in bus.ports().items()] if hasattr(bus, 'ports') else 'no ports')
log('bus attrs', [a for a in dir(bus) if not a.startswith('_')])

res = main.create_component('master:fixed_load', 92, 88, Name='RES_C1', PO=-1433.33, QO=0.0,
                            VBO=76.21, VPU=1.0, FR=50.0, NP=0, NQ=0)
log('res', {k: (v.x, v.y) for k, v in res.ports().items()})

rea = main.create_component('master:reactive_load', 108, 88, Name='REACT_C1', S=250.0, V=132.0, F=50.0)
log('rea', {k: (v.x, v.y) for k, v in rea.ports().items()})

vm = main.create_component('master:voltmeter', 100, 91, Name='V_C1')
log('vm', {k: (v.x, v.y) for k, v in vm.ports().items()})

gnd = main.create_component('master:ground', 103, 88)
log('gnd', {k: (v.x, v.y) for k, v in gnd.ports().items()})

bx = bus.bounds
log('bus bounds', bx)
pr.save()
log('saved (components left in place for inspection)')
