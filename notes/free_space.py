"""Find free rectangular patches of canvas (grid units) for placing machines.

A patch is free if no component body, no wire segment and no bus line falls inside it
(inflated by a margin).
"""
import re, sys

MARGIN = 1          # grid units
W = int(sys.argv[1]) if len(sys.argv) > 1 else 12
H = int(sys.argv[2]) if len(sys.argv) > 2 else 12
COUNT = int(sys.argv[3]) if len(sys.argv) > 3 else 8

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
G = 18.0

boxes = []      # (x0,y0,x1,y1) in grid units
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

print('obstacles', len(boxes))


def free(cx, cy):
    x0, y0 = cx - MARGIN, cy - MARGIN
    x1, y1 = cx + W + MARGIN, cy + H + MARGIN
    for (a, b, c, d) in boxes:
        if a < x1 and c > x0 and b < y1 and d > y0:
            return False
    return True


found = []
for cy in range(98, 176 - H, 2):
    for cx in range(4, 132 - W, 2):
        if free(cx, cy):
            # keep the spots apart
            if all(abs(cx - f[0]) > W or abs(cy - f[1]) > H for f in found):
                found.append((cx, cy))
                if len(found) >= COUNT:
                    break
    if len(found) >= COUNT:
        break

print('free patches (%dx%d grid units):' % (W, H))
for f in found:
    print('   ', f)
