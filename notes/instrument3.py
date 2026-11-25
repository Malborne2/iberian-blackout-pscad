"""Re-point the output channels (pgb) at the multimeter signals and tidy the layout.

The multimeter blocks already publish named signals P_Gxx / Q_Gxx / V_Gxx; an
`pgb` with UseSignalName=YES and Name=<signal> records it directly, so no wires
are needed and the datalabels can go.  (The previous instrumentation left all
33 channels named P_G30 and stacked at the same coordinates, which also aborted
the build with "Position is exactly on another instance".)
"""
import os, time
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

# ---- desired channel names, in multimeter order ----------------------------
names = []
for el in sch:
    if 'multimeter' not in (el.get('defn') or ''):
        continue
    pl = {pp.get('name'): pp.get('value') for pp in el.find('paramlist')}
    for k in ('P', 'Q', 'Vrms'):
        v = pl.get(k, '')
        if v:
            names.append((v, k))
log('channels wanted', len(names))

# ---- drop the datalabels ---------------------------------------------------
dead = [el for el in sch if el.get('defn') == 'master:datalabel']
for el in dead:
    sch.remove(el)
log('datalabels removed', len(dead))

# ---- reuse the pgb blocks --------------------------------------------------
pgbs = [el for el in sch if el.get('defn') == 'master:pgb']
log('pgb found', len(pgbs))
for i, el in enumerate(pgbs):
    if i >= len(names):
        sch.remove(el)
        continue
    name, kind = names[i]
    pl = el.find('paramlist')
    vals = {pp.get('name'): pp for pp in pl}
    vals['Name'].set('value', name)
    vals['Name'].set('link', '-1')
    vals['UseSignalName'].set('value', 'YES')
    vals['enab'].set('value', 'YES')
    vals['Display'].set('value', 'YES')
    vals['Units'].set('value', {'P': 'MW', 'Q': 'Mvar', 'Vrms': 'kV'}[kind])
    vals['Scale'].set('value', '1.0')
    vals['Max'].set('value', '3.0')
    vals['Min'].set('value', '-3.0')
    # tidy two-column layout in the free area right of the diagram
    col, row = divmod(i, 15)
    el.set('x', str(1500 + 120 * col))
    el.set('y', str(2400 - 80 * row))
log('pgb retargeted')

# ---- multimeter base: 100 MVA so P/Q read in pu of 100 MVA -----------------
n = 0
for el in sch:
    if 'multimeter' not in (el.get('defn') or ''):
        continue
    for pp in el.find('paramlist'):
        if pp.get('name') == 'S':
            pp.set('value', '100.0 [MVA]')
            n += 1
    # re-save the display values so the graphic shows sane numbers
log('meters re-based', n)

ET.indent(root)
ET.ElementTree(root).write(P, encoding='utf-8', xml_declaration=True)
log('written')

log('reload')
app.load(P)
time.sleep(3)
pr = app.project('Spanish_grid_model')
ps = pr.parameters()
log('PlotType', ps['PlotType'], 'T', ps['time_duration'], 'sample', ps['sample_step'])
