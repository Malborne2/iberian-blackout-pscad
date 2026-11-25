import inspect
import mhi.pscad as p

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

print([m for m in dir(main) if not m.startswith('_')])
for name in ('create_wire', 'create_component', 'create_connection'):
    if hasattr(main, name):
        f = getattr(main, name)
        try:
            print(name, inspect.signature(f))
            print('   ', (f.__doc__ or '')[:600])
        except Exception as e:
            print(name, 'err', e)
