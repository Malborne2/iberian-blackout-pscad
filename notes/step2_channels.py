import time, os, sys
def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)

import mhi.pscad as p

BASE = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model"
OUT = os.path.join(BASE, "Spanish_grid_model.gf81_x86", "Spanish_grid_model.out")

log("connect")
app = p.connect()
pr = app.project('Spanish_grid_model')

log("reload to discard any in-memory edits")
pr.reload()
time.sleep(2)
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

log("set project params")
pr.parameters(PlotType='PSOUT', time_duration=0.5, sample_step=100)
ps = pr.parameters()
log("params now:", ps['PlotType'], ps['time_duration'])

mm = main.component(1837570401)
mm.parameters(P='P_G30', Q='Q_G30', Vrms='V_G30', MeasV='YES', MeasP='YES', MeasQ='YES')
log("mm params set")

items = [('P_G30', 'MW'), ('Q_G30', 'MVAR'), ('V_G30', 'kV')]
x0, y0 = 1400, 120
for i, (nm, unit) in enumerate(items):
    y = y0 + 40 * i
    dl = main.create_component('master:datalabel', x0, y, 0, Name=nm)
    log("datalabel", nm, "iid", dl.iid)
    pg = main.create_component('master:pgb', x0 + 36, y, 0, Name=nm, Units=unit)
    log("pgb", nm, "iid", pg.iid)
    main.create_wire((x0, y), (x0 + 36, y))
    log("wire ok")

log("build")
pr.build()
log("run")
pr.run()
log("run finished")
log("status", pr.run_status())
log("out exists:", os.path.exists(OUT))
