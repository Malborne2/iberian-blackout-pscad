import sys, os, time
import mhi.pscad as p

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
log('build...')
t0 = time.time()
b = pr.build()
log('build done', round(time.time() - t0, 1))
