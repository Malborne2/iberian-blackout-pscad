"""Probe port offsets of xfmr-3p2w / fixed_load / voltmeter / reactive_load for all
orientations.  Creates each in an empty area, prints offsets relative to the
component origin, then deletes."""
import time, json
import mhi.pscad as p

def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
app.load('Spanish_grid_model.pscx')
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

GX, GY = 200, 300
out = {}

def probe(defn, orient, **kw):
    x = GX + orient * 12
    c = main.create_component(defn, x, GY, orient, **kw)
    pl = c.ports()
    d = {'bounds': [c.bounds.left, c.bounds.top, c.bounds.right, c.bounds.bottom],
         'ports': {k: (v.location[0] - x, v.location[1] - GY) for k, v in pl.items()},
         'dims': {k: v.dim for k, v in pl.items()}}
    out['%s|o%d' % (defn, orient)] = d
    log(defn, 'o%d' % orient, d)
    c.delete()

for o in range(8):
    probe('master:xfmr-3p2w', o, Name='PRB', Tmva=5000.0, f=50.0, V1=400.0, V2=128.16,
          Xl=0.12, YD1=0, YD2=0, Lead=1, Tap=0, Ideal=0, View=1)

for o in (0, 2):
    probe('master:fixed_load', o, Name='PRB2', PO=-100.0, QO=0.0, VBO=76.2, VPU=1.0,
          FR=50.0, NP=0, NQ=0)
for o in (0, 2):
    probe('master:voltmeter', o, Name='PRB3')
for o in (0, 2):
    probe('master:reactive_load', o, Name='PRB4', S=250.0, V=132.0, F=50.0)
for o in (0, 2):
    probe('master:ground', o)

with open('notes/geom3.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1)
log('done')
