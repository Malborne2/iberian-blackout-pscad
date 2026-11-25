"""Print wire endpoints near an XML point."""
import re, sys

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
X, Y = int(sys.argv[1]), int(sys.argv[2])
R = int(sys.argv[3]) if len(sys.argv) > 3 else 60

for wm in re.finditer(r'<Wire classid="WireOrthogonal"[^>]*>.*?</Wire>', s, re.S):
    b2 = wm.group(0)
    hh = dict(re.findall(r'(\w+)="([^"]*)"', b2[:b2.find('>')]))
    wx, wy = int(hh['x']), int(hh['y'])
    vs = [(wx + int(a), wy + int(b)) for a, b in
          re.findall(r'<vertex x="(-?\d+)" y="(-?\d+)"', b2)]
    if any(abs(px - X) <= R and abs(py - Y) <= R for px, py in vs):
        print(' ', vs)

print('--- grounds ---')
for gm in re.finditer(r'<User\b[^>]*defn="master:ground"[^>]*>', s):
    hh = dict(re.findall(r'(\w+)="([^"]*)"', gm.group(0)))
    gx, gy = int(hh['x']), int(hh['y'])
    if abs(gx - X) <= R and abs(gy - Y) <= R:
        print('  ground at', (gx, gy), hh.get('orient'))
