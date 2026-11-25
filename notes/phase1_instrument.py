"""Instrument the model: named P/Q/V signals from the 10 multimeters -> pgb output channels.
Also probes sync_machine ports so we know how to wire real machines later.
"""
import time, os, json
def log(*a): print(time.strftime("%H:%M:%S"), *a, flush=True)
import mhi.pscad as p

BASE = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model"

# multimeter iid -> generator bus label (from geometry match with source3 instances)
MM = [
    ("1837570401", "G37"), ("470679792", "G30"), ("1917341412", "G39"), ("827627569", "G31"),
    ("351692673", "G32"), ("882978752", "G34"), ("873234036", "G33"), ("48983152", "G36"),
    ("1853913980", "G35"), ("198841240", "G38"),
]

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

pr.parameters(time_duration=0.5, sample_step=100)

made = []
x0 = 1460
for i, (iid, lab) in enumerate(MM):
    mm = main.component(int(iid))
    mm.parameters(P='P_%s' % lab, Q='Q_%s' % lab, Vrms='V_%s' % lab,
                  MeasP='YES', MeasQ='YES', MeasV='YES', S='100.0 [MVA]')
    for j, (sig, unit) in enumerate([('P_%s' % lab, 'MW'), ('Q_%s' % lab, 'MVAR'), ('V_%s' % lab, 'pu')]):
        y = 100 + 40 * (3 * i + j)
        main.create_component('master:datalabel', x0, y, 0, Name=sig)
        main.create_component('master:pgb', x0 + 40, y, 0, Name=sig, Units=unit)
        main.create_wire((x0, y), (x0 + 40, y))
    log("done", lab)

log("probe sync_machine")
sm = main.create_component('master:sync_machine', 1500, 1500, 0)
log("sync_machine iid", sm.iid)
ps = sm.parameters()
for k, v in ps.items():
    log("   ", k, "=", v)
try:
    for pt in sm.ports():
        log("   port", pt.name, list(pt.location))
except Exception as e:
    log("port err", e)
log("delete probe")
sm.delete()

log("save")
pr.save()
log("saved")
