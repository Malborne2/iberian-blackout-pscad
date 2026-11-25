import time
def log(*a): print(*a, flush=True)
import mhi.pscad as p
app = p.connect()
pr = app.project('Spanish_grid_model')
log("PlotType:", pr.parameters()['PlotType'])
log("--- messages ---")
for m in pr.messages():
    log(m)
log("--- output text (tail) ---")
txt = pr.output()
log(txt[-3000:] if txt else "(none)")
