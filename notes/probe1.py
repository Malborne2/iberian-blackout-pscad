import sys, time
def log(*a):
    print(*a, flush=True)

log("start")
import mhi.pscad as p
log("imported")
app = p.connect()
log("connected", app.version)
prs = app.projects()
log("projects", [x['name'] if isinstance(x, dict) else x.name for x in prs])
