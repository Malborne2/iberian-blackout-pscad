"""Print every Bus with XML coords and derived grid-unit line extent."""
import re

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
for m in re.finditer(r'<Wire classid="Bus"[^>]*>.*?</Wire>', s, re.S):
    b = m.group(0)
    h = dict(re.findall(r'(\w+)="([^"]*)"', b[:b.find('>')]))
    nm = re.search(r'name="Name" value="([^"]*)"', b).group(1)
    vs = re.findall(r'<vertex x="(-?\d+)" y="(-?\d+)"', b)
    x0 = int(h['x']) + min(int(a) for a, _ in vs)
    x1 = int(h['x']) + max(int(a) for a, _ in vs)
    y = int(h['y']) + int(vs[0][1])
    print('%-7s xml x %5d..%5d y %5d   grid x %6.1f..%6.1f y %6.1f'
          % (nm, x0, x1, y, x0 / 18, x1 / 18, y / 18))
