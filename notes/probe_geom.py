"""Probe geometry of the collector-group components inside the live project.

Creates one instance of each needed component in an empty area, prints the port
locations relative to the component origin (grid units), then deletes them.
Nothing is saved, so the project on disk is untouched.
"""
import time, json, os
import mhi.pscad as p

def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

GX, GY = 100, 140          # empty area, grid units

out = {}

def dump(tag, c):
    b = c.bounds
    d = {'bounds': [b.left, b.top, b.right, b.bottom]}
    try:
        d['ports'] = {k: [v.location[0], v.location[1]] for k, v in c.ports().items()}
        d['rel'] = {k: [v.location[0] - b.left, v.location[1] - b.top]
                    for k, v in c.ports().items()}
    except Exception as e:
        d['ports'] = 'ERR %s %s' % (type(e).__name__, e)
    out[tag] = d
    log(tag, d)

made = []

def mk(tag, defn, x, y, **kw):
    try:
        c = main.create_component(defn, x, y, **kw)
    except Exception as e:
        log(tag, 'CREATE ERR', type(e).__name__, e)
        out[tag] = {'error': str(e)}
        return None
    made.append(c)
    dump(tag, c)
    return c

xf = mk('xfmr', 'master:xfmr-3p2w', GX, GY, Name='T_C1', Tmva=5000.0, f=50.0,
        V1=400.0, V2=132.0 / 1.03, Xl=0.12, YD1=0, YD2=0, Lead=1, Tap=0, Ideal=0)

# bus
try:
    bus = main.create_bus((GX - 3, GY - 6), (GX + 3, GY - 6))
    log('bus', bus, 'bounds', bus.bounds.left, bus.bounds.top, bus.bounds.right, bus.bounds.bottom)
    out['bus'] = {'bounds': [bus.bounds.left, bus.bounds.top, bus.bounds.right, bus.bounds.bottom]}
except Exception as e:
    log('bus ERR', type(e).__name__, e)
    out['bus'] = {'error': str(e)}

res = mk('fixed_load', 'master:fixed_load', GX - 8, GY - 12, Name='RES_C1',
         PO=-4300.0 / 3, QO=0.0, VBO=132.0 / 3 ** 0.5, VPU=1.0, FR=50.0, NP=0, NQ=0)
rea = mk('reactive_load', 'master:reactive_load', GX + 6, GY - 12, Name='REACT_C1',
         S=250.0, V=132.0, F=50.0)
vm = mk('voltmeter', 'master:voltmeter', GX, GY - 9, Name='V_C1')
g1 = mk('ground1', 'master:ground', GX - 4, GY + 3)
g2 = mk('ground2', 'master:ground', GX + 4, GY + 3)

with open(os.path.join('notes', 'geom2.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1)

for c in made:
    try:
        c.delete()
    except Exception as e:
        log('del err', e)

log('done')
