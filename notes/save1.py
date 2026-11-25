import time, os
def log(*a): print(time.strftime("%H:%M:%S"), *a, flush=True)
import mhi.pscad as p
app = p.connect()
pr = app.project('Spanish_grid_model')
log("saving")
pr.save()
log("saved")
log("PlotType", pr.parameters()['PlotType'])
