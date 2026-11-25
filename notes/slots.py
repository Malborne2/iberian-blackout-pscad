"""Find clear slots for machines near generator buses.

Obstacles: every component body and wire segment.  Bus elements are excluded from the wire
corridor checks because a wire is *supposed* to end on its bus.

Usage: python notes/slots.py [radius]
Prints one slot per generator bus.
"""
import re, sys

G = 18.0
R = int(sys.argv[1]) if len(sys.argv) > 1 else 20

BUSES = [('Bus30', 27, 17, 1130.0), ('Bus31', 34, 83, 1130.0), ('Bus32', 43, 94, 1130.0),
         ('Bus33', 58, 89, 1500.0), ('Bus34', 51, 89, 1500.0), ('Bus35', 64, 43, 720.0),
         ('Bus36', 64, 81, 7200.0), ('Bus37', 32, 10, 7200.0), ('Bus38', 68, 31, 7200.0),
         ('Bus39', 24, 55, 4000.0)]

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()

bodies = []
wires = []
for m in re.finditer(r'<(User|Gfx)\b[^>]*>', s):
    d = dict(re.findall(r'(\w+)="([^"]*)"', m.group(0)))
    try:
        x, y = int(d['x']) / G, int(d['y']) / G
        w, h = max(int(d.get('w', 2)), 2) / G, max(int(d.get('h', 2)), 2) / G
    except (KeyError, ValueError):
        continue
    if x > 200:
        continue
    bodies.append((x, y, x + w, y + h))

for m in re.finditer(r'<Wire classid="(WireOrthogonal|Bus)"[^>]*>.*?</Wire>', s, re.S):
    blk = m.group(0)
    d = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
    x, y = int(d['x']) / G, int(d['y']) / G
    pts = [(x + int(a) / G, y + int(b) / G)
           for a, b in re.findall(r'<vertex x="(-?\d+)" y="(-?\d+)"', blk)]
    segs = list(zip(pts, pts[1:]))
    tgt = bodies if d.get('classid') == 'Bus' else wires
    for p, q in segs:
        tgt.append((min(p[0], q[0]), min(p[1], q[1]), max(p[0], q[0]), max(p[1], q[1])))


def hits(lst, x0, y0, x1, y1, pad=0.5):
    for (a, b, c, d) in lst:
        if a < x1 + pad and c > x0 - pad and b < y1 + pad and d > y0 - pad:
            return True
    return False


def clear_route(nx, my, bx, by):
    y0, y1 = sorted((my, by))
    if hits(wires, nx, y0, nx, y1, pad=0.3):
        return False
    x0, x1 = sorted((nx, bx))
    if x1 - x0 > 0.5 and hits(wires, x0, by, x1, by, pad=0.3):
        return False
    return True


def find(bx, by):
    best = None
    for mx in range(int(bx - R), int(bx + R) + 1):
        for my in range(int(by - R), int(by + R) + 1):
            if hits(bodies, mx - 3, my - 4, mx + 3, my + 4, pad=0.4):
                continue
            if not clear_route(mx + 3, my, bx, by):
                continue
            d = abs(mx - bx) + abs(my - by)
            if abs(mx + 3 - bx) > 6:
                continue
            if best is None or d < best[0]:
                best = (d, mx, my)
    return best


print('bus      slot      NS        route')
for name, bx, by, mva in BUSES:
    b = find(bx, by)
    if b is None:
        print('%-7s  none' % name)
    else:
        d, mx, my = b
        print('%-7s  (%3d,%3d)  (%3d,%3d)  v x=%d %d..%d, h y=%d %d..%d'
              % (name, mx, my, mx + 3, my, mx + 3, min(my, by), max(my, by),
                 by, min(mx + 3, bx), max(mx + 3, bx)))
