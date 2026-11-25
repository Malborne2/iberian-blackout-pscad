import inspect
import mhi.pscad as p

app = p.connect()
pr = app.project('Spanish_grid_model')
cls = type(pr)
names = [n for n in dir(cls) if not n.startswith('_')]
print(names)
for n in names:
    low = n.lower()
    if any(k in low for k in ('mess', 'build', 'log', 'notif', 'error', 'warn')):
        try:
            print('\n==', n, inspect.signature(getattr(cls, n)))
            print((inspect.getdoc(getattr(cls, n)) or '')[:600])
        except Exception as e:
            print('\n==', n, 'ERR', e)
