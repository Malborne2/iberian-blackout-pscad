"""Find vertical corridors: x positions on a bus from which a straight vertical wire
down to the free band (y_target) does not pass through any component body."""
import re, sys

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()

# component bodies (any User/Gfx element) - conservative boxes
obs = []
for m in re.finditer(r'<(User|Gfx)\b[^>]*>', s):
    d = dict(re.findall(r'(\w+)="([^"]*)"', m.group(0)))
    try:
        x, y = int(d['x']), int(d['y'])
        w, h = int(d.get('w', 0)), int(d.get('h', 0))
    except (KeyError, ValueError):
        continue
    if x > 5000:          # instrumentation column, irrelevant
        continue
    obs.append((x, y, x + max(w, 1), y + max(h, 1)))

# bus lines
buses = {}
for m in re.finditer(r'<Wire classid="Bus"[^>]*>.*?</Wire>', s, re.S):
    blk = m.group(0)
    d = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
    nm = re.search(r'name="Name" value="([^"]*)"', blk).group(1)
    vs = re.findall(r'<vertex x="(-?\d+)" y="(-?\d+)"', blk)
    x0 = int(d['x']) + min(int(a) for a, _ in vs)
    x1 = int(d['x']) + max(int(a) for a, _ in vs)
    buses[nm] = (x0, x1, int(d['y']))

YT = int(sys.argv[1]) if len(sys.argv) > 1 else 1746   # xml target y (97 grid)
for nm in ('Bus1', 'Bus2', 'Bus12', 'Bus16', 'Bus22'):
    x0, x1, y = buses[nm]
    free = []
    for x in range(x0 + 4, x1 - 2, 6):        # stay off the bus ends
        ok = True
        for (a, b, c, dd) in obs:
            if a - 4 <= x <= c + 4 and b <= YT and dd >= y:
                ok = False
                break
        if ok:
            free.append((x, round(x / 18, 2)))
    print('%-6s xml y=%4d x %4d..%4d  grid x %5.1f..%5.1f' % (nm, y, x0, x1, x0 / 18, x1 / 18))
    print('        free columns (xml, grid):', free)
