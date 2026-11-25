import inspect
import mhi.pscad as p

app = p.connect()
main = app.project('Spanish_grid_model').canvas('Main')
cls = type(main)
print([n for n in dir(cls) if not n.startswith('_')])
for n in ('create_connection', 'create_wire', 'create_line', 'create_node', 'create_bus',
          'create_component', 'create_text'):
    if hasattr(cls, n):
        print('\n==', n, inspect.signature(getattr(cls, n)))
        d = inspect.getdoc(getattr(cls, n)) or ''
        print(d[:900])
