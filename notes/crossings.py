"""Detect orthogonal crossings between wires (no shared endpoint) in the model."""
import re

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()

segs = []
for m in re.finditer(r'<Wire classid="WireOrthogonal"[^>]*>.*?</Wire>', s, re.S):
    blk = m.group(0)
    h = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
    x, y = int(h['x']), int(h['y'])
    pts = [(x + int(a), y + int(b))
           for a, b in re.findall(r'<vertex x="(-?\d+)" y="(-?\d+)"', blk)]
    for p, q in zip(pts, pts[1:]):
        segs.append((p, q, h['id']))

print('segments', len(segs))

h = [s_ for s_ in segs if s_[0][1] == s_[1][1]]
v = [s_ for s_ in segs if s_[0][0] == s_[1][0]]
print('horizontal', len(h), 'vertical', len(v))

cross = 0
for (p1, q1, i1) in h:
    x1a, x1b = sorted((p1[0], q1[0]))
    y1 = p1[1]
    for (p2, q2, i2) in v:
        y2a, y2b = sorted((p2[1], q2[1]))
        x2 = p2[0]
        if x1a < x2 < x1b and y2a < y1 < y2b:
            cross += 1
            if cross <= 15:
                print('CROSS  h#%s y=%s x %s..%s   v#%s x=%s y %s..%s'
                      % (i1, y1, x1a, x1b, i2, x2, y2a, y2b))
print('total crossings', cross)
