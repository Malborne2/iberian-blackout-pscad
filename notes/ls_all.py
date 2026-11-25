"""Summary of what main.components() returns."""
import mhi.pscad as p

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')
cs = main.components()
print('count', len(cs))
xs = []
for c in cs:
    try:
        b = c.bounds
        xs.append((b.left, b.top, str(getattr(c, 'definition', ''))))
    except Exception as e:
        xs.append((-1, -1, 'ERR %s' % e))
xs.sort()
for r in xs[-8:]:
    print(r)
print('min', xs[0], 'max', xs[-1])
