import time
import mhi.pscad as p

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

for defn in ('master:voltmeter', 'master:reactive_load'):
    c = main.create_component(defn, 3000, 2000)
    log(defn, 'ports', {k: v.location for k, v in c.ports().items()})
    log(defn, 'params', {k: str(v) for k, v in c.parameters().items()})
    c.delete()

xf = main.create_component('master:xfmr-3p2w', 3000, 1800)
log('xfmr ports', {k: v.location for k, v in xf.ports().items()})
log('xfmr params', {k: str(v) for k, v in xf.parameters().items()})
xf.delete()
log('done')
