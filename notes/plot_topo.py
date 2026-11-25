import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

path = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model\Spanish_grid_model.pscx"
root = ET.parse(path).getroot()
main = [d for d in root.find('definitions') if d.get('name') == 'Main'][0]
sch = main.find('schematic')

fig, ax = plt.subplots(figsize=(26, 15), dpi=110)

def verts(el):
    x0 = float(el.get('x')); y0 = float(el.get('y'))
    vs = [(x0 + float(v.get('x')), y0 + float(v.get('y'))) for v in el.findall('vertex')]
    return vs

buses = []
for el in sch:
    cls = el.get('classid')
    if cls == 'Bus':
        vs = verts(el)
        buses.append((el, vs))
    elif cls == 'WireOrthogonal':
        vs = verts(el)
        ax.plot([p[0] for p in vs], [-p[1] for p in vs], color='#7f7f7f', lw=1.0, zorder=1)

# buses
for el, vs in buses:
    pl = el.find('paramlist')
    name = ''
    basekv = ''
    if pl is not None:
        d = {p.get('name'): p.get('value') for p in pl}
        name = d.get('Name', '')
        basekv = d.get('BaseKV', '')
    ax.plot([p[0] for p in vs], [-p[1] for p in vs], color='k', lw=3.5, solid_capstyle='butt', zorder=3)
    mx = sum(p[0] for p in vs) / len(vs)
    my = -sum(p[1] for p in vs) / len(vs)
    ax.text(mx, my + 6, name.replace('Bus', ''), fontsize=7, ha='center', va='bottom', color='navy', zorder=5)

# components
colour = {
    'master:source3': ('red', 'S'),
    'master:fixed_load': ('blue', 'v'),
    'master:xfmr-3p2w': ('green', 's'),
    'master:multimeter': ('orange', 'D'),
    'master:capacitor': ('purple', 'o'),
    'master:const': ('brown', '.'),
    'master:ground': ('gray', 'x'),
    'master:annotation': ('black', None),
}
for el in sch:
    if el.get('classid') != 'UserCmp':
        continue
    d = el.get('defn')
    x = float(el.get('x')); y = float(el.get('y'))
    c, m = colour.get(d, ('magenta', '+'))
    if m:
        ax.text(x, -y, {'red':'S','blue':'L','green':'T','orange':'M','purple':'C','brown':'.','gray':'g','black':''}.get(c,'*'),
                color=c, fontsize=8, fontweight='bold', ha='center', va='center', zorder=4)
    if d in ('master:source3', 'master:xfmr-3p2w', 'master:multimeter', 'master:capacitor'):
        pl = el.find('paramlist')
        dd = {p.get('name'): p.get('value') for p in pl}
        lab = dd.get('Name') or (dd.get('Pd', '') if d == 'master:multimeter' else '')
        if d == 'master:multimeter':
            lab = 'Pd=%s' % dd.get('Pd', '')
        if d == 'master:xfmr-3p2w':
            lab = '%s/%s T%s' % (dd.get('V1', '').split()[0], dd.get('V2', '').split()[0], dd.get('Tap', ''))
        if d == 'master:source3':
            lab = '%s P%s' % (dd.get('Name', ''), dd.get('Pinit', ''))
        if d == 'master:capacitor':
            lab = dd.get('C', '')
        ax.text(x + 3, -y - 3, lab, fontsize=5, color=c, zorder=5)

ax.set_aspect('equal')
ax.set_title('Main canvas geometry')
plt.tight_layout()
plt.savefig(r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model\notes\topology.png")
print("saved; buses:", len(buses))
