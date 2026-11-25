import mhi.pscad as p
app = p.connect()
pr = app.project('ieee_39_bus')
m = pr.canvas('Main')
comps = m.components()
print('total components:', len(comps))
for c in comps:
    t = type(c).__name__
    nm = getattr(c, 'name', None)
    if t == 'Bus':
        print('BUS', nm)
        continue
    try:
        d = c.definition.name
    except Exception:
        d = '?'
    try:
        pars = c.parameters()
    except Exception as e:
        pars = 'ERR %s' % e
    print(f'{t} {nm} | {d} | {pars}')
