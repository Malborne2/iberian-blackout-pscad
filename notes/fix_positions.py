"""Move overlapping pgb blocks away from their datalabel so the build passes.

PSCAD aborts the build ("Position is exactly on another instance") when two
components share identical x/y.  The project is saved + unloaded first so the
XML edit is not overwritten by PSCAD.
"""
import os, time, collections
import xml.etree.ElementTree as ET

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

BASE = r'C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model'
P = os.path.join(BASE, 'Spanish_grid_model.pscx')

import mhi.pscad as p
app = p.connect()
pr = app.project('Spanish_grid_model')
log('save + unload')
pr.save()
pr.unload()
time.sleep(2)

root = ET.parse(P).getroot()
main = [d for d in root.find('definitions') if d.get('name') == 'Main'][0]
sch = main.find('schematic')

COMP = ('UserCmp', 'Bus', 'Wire', 'Module')
pos = collections.defaultdict(list)
for el in sch:
    if el.get('classid') in COMP:
        pos[(el.get('x'), el.get('y'))].append(el)

moved = 0
for el in sch:
    if el.get('defn') != 'master:pgb':
        continue
    key = (el.get('x'), el.get('y'))
    others = [o for o in pos.get(key, []) if o is not el]
    if others:
        el.set('x', str(int(float(el.get('x'))) - 90))
        moved += 1
log('moved pgbs:', moved)

pos2 = collections.defaultdict(list)
for el in sch:
    if el.get('classid') in COMP:
        pos2[(el.get('x'), el.get('y'))].append(el.get('defn') or el.get('classid'))
dups = {k: v for k, v in pos2.items() if len(v) > 1}
log('remaining duplicate positions:', len(dups))
for k, v in list(dups.items())[:10]:
    log('  ', k, v)

ET.indent(root)
ET.ElementTree(root).write(P, encoding='utf-8', xml_declaration=True)
log('written')

log('reload')
app.load(P)
time.sleep(3)
pr = app.project('Spanish_grid_model')
ps = pr.parameters()
log('PlotType', ps['PlotType'], 'T', ps['time_duration'], 'sample', ps['sample_step'])
