import mhi.pscad as p

app = p.connect()
pr = app.project('ieee_39_bus')
m = pr.canvas('Main')
comps = m.components()

def dname(c):
    try:
        return c.definition.name
    except Exception:
        return type(c).__name__

def nm(c):
    try:
        return c.parameters().get('Name', '')
    except Exception:
        return ''

for kind in ('source3', 'capacitor', 'multimeter', 'psse'):
    print('==== %s ====' % kind)
    for c in comps:
        if dname(c) == kind:
            print(c.location, c.orient, c.parameters())

print('==== buses ====')
for c in comps:
    if type(c).__name__ == 'Bus':
        print(c.location, c.parameters())
