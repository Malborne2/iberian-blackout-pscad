import json, os
import mhi.pscad as p

BASE = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model"
app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

comps = main.components()
print("total top-level components:", len(comps))

rows = []
for c in comps:
    t = type(c).__name__
    row = {'type': t, 'id': getattr(c, 'id', None)}
    try:
        row['defn'] = c.definition.name
    except Exception:
        row['defn'] = None
    try:
        row['loc'] = list(c.location)
    except Exception:
        row['loc'] = None
    try:
        row['orient'] = c.orient
    except Exception:
        row['orient'] = None
    try:
        row['params'] = dict(c.parameters())
    except Exception as e:
        row['params'] = {'<<ERR>>': str(e)}
    try:
        row['ports'] = [(pp.name, list(pp.location)) for pp in c.ports()]
    except Exception:
        row['ports'] = None
    rows.append(row)

with open(os.path.join(BASE, 'notes', 'main_dump.json'), 'w', encoding='utf-8') as f:
    json.dump(rows, f, indent=1, default=str)

from collections import Counter
print(Counter(r['defn'] for r in rows))

for r in rows:
    if r['type'] == 'Bus':
        print("BUS", r['id'], r['params'].get('Name'), r['loc'], {k: v for k, v in r['params'].items() if k != 'Name'})
