"""Probe xfmr-3p2w ports for all 8 orientations (creates and deletes each)."""
import time
import mhi.pscad as p

def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

GX, GY = 400, 300
for o in range(8):
    c = main.create_component('master:xfmr-3p2w', GX, GY, o, Name='PRB%d' % o,
                              Tmva=5000.0, f=50.0, V1=400.0, V2=128.16, Xl=0.12,
                              YD1=0, YD2=0, Lead=1, Tap=0, Ideal=0, View=1)
    b = c.bounds
    rel = {k: (v.location[0] - GX, v.location[1] - GY) for k, v in c.ports().items()}
    log('orient', o, 'wh', (b.right - b.left, b.bottom - b.top), 'ports', rel)
    c.delete()
log('done')
