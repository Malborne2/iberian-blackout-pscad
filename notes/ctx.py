"""Print a component instance (matched by Name) and the wire endpoints near it."""
import re, sys

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
pat_name = sys.argv[1]

# find User blocks and check the Name param
found = None
for m in re.finditer(r'<User\b[^>]*defn="([^"]+)"[^>]*>.*?</User>', s, re.S):
    blk = m.group(0)
    if ('value="%s"' % pat_name) in blk:
        found = (m.start(), blk)
        break
if not found:
    print('not found', pat_name)
    sys.exit()
blk = found[1]
hdr = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
print('HEADER', hdr)
print(blk[:1200])
x, y, w, h = int(hdr['x']), int(hdr['y']), int(hdr['w']), int(hdr['h'])

print('\n--- wires with an endpoint within 60 units of the component box ---')
for wm in re.finditer(r'<Wire classid="WireOrthogonal"[^>]*>.*?</Wire>', s, re.S):
    b2 = wm.group(0)
    hh = dict(re.findall(r'(\w+)="([^"]*)"', b2[:b2.find('>')]))
    wx, wy = int(hh['x']), int(hh['y'])
    vs = [(wx + int(a), wy + int(b)) for a, b in
          re.findall(r'<vertex x="(-?\d+)" y="(-?\d+)"', b2)]
    if any(x - 60 <= px <= x + w + 60 and y - 60 <= py <= y + h + 60 for px, py in vs):
        print(' ', vs)

print('\n--- bus rects within 200 ---')
for bm in re.finditer(r'<Wire classid="Bus"[^>]*>.*?</Wire>', s, re.S):
    b2 = bm.group(0)
    hh = dict(re.findall(r'(\w+)="([^"]*)"', b2[:b2.find('>')]))
    nm = re.search(r'name="Name" value="([^"]*)"', b2).group(1)
    bx, by, bw = int(hh['x']), int(hh['y']), int(hh['w'])
    if abs(bx - x) < 200 and abs(by - y) < 200:
        print(' ', nm, (bx, by), 'w', bw)
