"""Find a clear slot for a sync machine next to a given bus.

The machine body is (mx-3 .. mx+3, my-4 .. my+4) in grid units, its stator port NS is at
(mx+3, my), and a straight wire must run from NS to the bus without touching anything.

Usage: python notes/find_slot.py bx by [maxradius]
Prints candidate slots, best (closest) first.
"""
import re, sys

G = 18.0
bx, by = float(sys.argv[1]), float(sys.argv[2])
R = int(sys.argv[3]) if len(sys.argv) > 3 else 14

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


def hits(x0, y0, x1, y1, pad=0.6):
    for (a, b, c, d) in boxes:
        if a < x1 + pad and c > x0 - pad and b < y1 + pad and d > y0 - pad:
            return True
    return False


cands = []
for mx in range(int(bx - R), int(bx + R) + 1):
    for my in range(int(by - R), int(by + R) + 1):
        # machine body
        if hits(mx - 3, my - 4, mx + 3, my + 4):
            continue
        # stator wire corridor x = mx+3, from my to by
        y0, y1 = sorted((my, by))
        if hits(mx + 3, y0, mx + 3, y1, pad=0.4):
            continue
        d = abs(mx - bx) + abs(my - by)
        cands.append((d, mx, my))

cands.sort()
print('bus', (bx, by), 'candidates', len(cands))
for d, mx, my in cands[:8]:
    print('   slot (%d,%d)  dist %d  NS->(%d,%d)' % (mx, my, d, mx + 3, my))
