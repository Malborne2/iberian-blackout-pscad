import inspect
import mhi.pscad as p

app = p.connect()
print('projects:', [str(x) for x in app.projects()])
cls = type(app)
for nm in ('load', 'open', 'workspace'):
    if hasattr(cls, nm):
        f = getattr(cls, nm)
        print('\n---', nm, inspect.signature(f))
        print((inspect.getdoc(f) or '')[:1200])
