import re, xml.etree.ElementTree as ET, collections
P = r'C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model\Spanish_grid_model.pscx'
root = ET.parse(P).getroot()
main = [d for d in root.find('definitions') if d.get('name') == 'Main'][0]
sch = main.find('schematic')

rows = []
for el in sch:
    d = el.get('defn') or ''
    if d in ('master:datalabel', 'master:pgb'):
        pl = el.find('paramlist')
        vals = {p.get('name'): p.get('value') for p in pl}
        rows.append((d, el.get('classid'), el.get('name'), vals.get('x'), vals.get('y'), vals.get('w'), vals.get('h')))
        if len(rows) < 4:
            print('PARAMS', d, sorted(vals.items()))

print('count', len(rows))
pos = collections.Counter((r[3], r[4]) for r in rows)
print('duplicate positions:', [k for k, v in pos.items() if v > 1])
for r in rows:
    print(r)
