import time
import mhi.pscad as p

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

dl = main.create_component('master:datalabel', 3000, 3000, Name='P_G30')
log('datalabel ports', {k: v.location for k, v in dl.ports().items()})
log('datalabel params', {k: str(v) for k, v in dl.parameters().items()})
dl.delete()
log('deleted')
