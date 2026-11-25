import xml.etree.ElementTree as ET, json, os
BASE = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model"
path = os.path.join(BASE, "Spanish_grid_model.pscx")
root = ET.parse(path).getroot()
main = [d for d in root.find('definitions') if d.get('name') == 'Main'][0]
sch = main.find('schematic')

rows = []
for el in sch:
    cls = el.get('classid')
    if cls not in ('UserCmp', 'Bus'):
        continue
    d = el.get('defn')
    pl = el.find('paramlist')
    params = {}
    if pl is not None:
        for pp in pl:
            params[pp.get('name')] = pp.get('value')
    rows.append({'id': el.get('id'), 'cls': cls, 'defn': d,
                 'x': int(el.get('x')), 'y': int(el.get('y')),
                 'w': int(el.get('w')), 'h': int(el.get('h')),
                 'orient': el.get('orient'), 'params': params})

with open(os.path.join(BASE, 'notes', 'comps.json'), 'w', encoding='utf-8') as f:
    json.dump(rows, f, indent=1, default=str)

loads = [r for r in rows if r['defn'] == 'master:fixed_load']
srcs = [r for r in rows if r['defn'] == 'master:source3']
xf = [r for r in rows if r['defn'] == 'master:xfmr-3p2w']
caps = [r for r in rows if r['defn'] == 'master:capacitor']
mms = [r for r in rows if r['defn'] == 'master:multimeter']
buses = [r for r in rows if r['cls'] == 'Bus']

def fnum(s):
    try:
        return float(str(s).split()[0])
    except Exception:
        return 0.0

P = sum(fnum(r['params'].get('PO')) for r in loads)
Q = sum(fnum(r['params'].get('QO')) for r in loads)
print(f"loads: n={len(loads)}  P={P:.1f} MW  Q={Q:.1f} MVAR")

print("\nsources:")
tot = 0
for r in srcs:
    pinit = fnum(r['params'].get('Pinit')); qinit = fnum(r['params'].get('Qinit'))
    tot += pinit
    print(f"  id={r['id']:12s} at ({r['x']:4d},{r['y']:4d}) Pinit={pinit:6.3f} Qinit={qinit:7.3f} Vm={r['params'].get('Vm')} Es={r['params'].get('Es')} Name={r['params'].get('Name')!r}")
print(f"  total Pinit = {tot:.3f} pu")

print("\ntransformers:")
for r in xf:
    print(f"  id={r['id']:12s} at ({r['x']:4d},{r['y']:4d}) o={r['orient']} Tmva={r['params'].get('Tmva')} V1={r['params'].get('V1')} V2={r['params'].get('V2')} Xl={r['params'].get('Xl')} Tap={r['params'].get('Tap')}")

print("\ncapacitors:", [(r['id'], r['params'].get('C'), (r['x'], r['y'])) for r in caps])
print("\nmultimeters:")
for r in mms:
    print(f"  id={r['id']:12s} at ({r['x']:4d},{r['y']:4d}) Pd={r['params'].get('Pd')} Qd={r['params'].get('Qd')} Vd={r['params'].get('Vd')} P={r['params'].get('P')!r} Q={r['params'].get('Q')!r} Vrms={r['params'].get('Vrms')!r}")

print("\nbuses:")
for r in buses:
    print(f"  {r['params'].get('Name'):8s} id={r['id']:12s} ({r['x']:4d},{r['y']:4d}) w={r['w']} BaseKV={r['params'].get('BaseKV')} VM={r['params'].get('VM')}")
