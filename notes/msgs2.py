"""Print the error messages with every field (including link/id)."""
import mhi.pscad as p

app = p.connect()
pr = app.project('Spanish_grid_model')
for m in pr.messages():
    if str(m.status).lower().startswith('err'):
        print(repr(m))
        print()
