"""Find a clear slot for a sync machine near a bus, with an L-shaped wire to the bus.

Checks the machine body AND both segments of the route NS -> (NS.x, by) -> (bx, by).

Usage: python notes/find_slot2.py bx by [maxradius] [count]
"""
import re, sys

G = 18.0
bx, by = float(sys.argv[1]), float(sys.argv[2])
R = int(sys.argv[3]) if len(sys.argv) > 3 else 20
N = int(sys.argv[4]) if len(sys.argv) > 4 else 5

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()

boxes = []
for m in re.finditer(r'<(User|Gfx)\b[^>]*>', s):
    d = dict(re.findall(r'(\w+)="([^"]*)"', m.group(0)))
    try:
        x, y = int(d['x']) / G, int(d['y']) / G
        w, h = max(int(d.get('w', 2)), 2) / G, max(int(d.get('h', 2)), 2) / G
    except (KeyError, ValueError):
        continue
    if x > 200:
        continue
    boxes.append((x, y, x + w, y + h))

for m in re.finditer(r'<Wire classid="(?:WireOrthogonal|Bus)"[^>]*>.*?</Wire>', s, re.S):
    blk = m.group(0)
    d = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
    x, y = int(d['x']) / G, int(d['y']) / G
    pts = [(x + int(a) / G, y + int(b) / G)
           for a, b in re.findall(r'<vertex x="(-?\d+)" y="(-?\d+)"', blk)]
    for p, q in zip(pts, pts[1:]):
        boxes.append((min(p[0], q[0]), min(p[1], q[1]),
                      max(p[0], q[0]), max(p[1], q[1])))


def hits(x0, y0, x1, y1, pad=0.5):
    for (a, b, c, d) in boxes:
        if a < x1 + pad and c > x0 - pad and b < y1 + pad and d > y0 - pad:
            return True
    return False


cands = []
for mx in range(int(bx - R), int(bx + R) + 1):
    for my in range(int(by - R), int(by + R) + 1):
        if hits(mx - 3, my - 4, mx + 3, my + 4):
            continue
        nx = mx + 3
        # vertical segment NS -> (nx, by)
        y0, y1 = sorted((my, by))
        if hits(nx, y0, nx, y1, pad=0.3):
            continue
        # horizontal segment (nx,by) -> (bx,by)
        x0, x1 = sorted((nx, bx))
        if x1 - x0 > 0.5 and hits(x0, by, x1, by, pad=0.3):
            continue
        d = abs(mx - bx) + abs(my - by)
        cands.append((d, mx, my))

cands.sort()
print('bus (%g,%g): %d candidates' % (bx, by, len(cands)))
for d, mx, my in cands[:N]:
    print('   slot (%d,%d) dist %d' % (mx, my, d))
