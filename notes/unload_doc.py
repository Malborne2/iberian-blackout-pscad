import inspect
import mhi.pscad as p

app = p.connect()
pr = app.project('Spanish_grid_model')
print(inspect.signature(type(pr).unload))
print(inspect.getdoc(type(pr).unload))
print('dirty', pr.dirty())
