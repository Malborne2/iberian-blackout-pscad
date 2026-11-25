"""Show a UserCmp instance and the wires whose bounding box is nearby."""
import re, sys

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
defn = sys.argv[1] if len(sys.argv) > 1 else 'master:xfmr-3p2w'

pat = re.compile(r'<User\b[^>]*defn="%s"[^>]*>.*?</User>' % re.escape(defn), re.S)
m = pat.search(s)
print(m.group(0))
hdr = dict(re.findall(r'(\w+)="([^"]*)"', m.group(0)[:m.group(0).find('>')]))
x, y = int(hdr['x']), int(hdr['y'])
w, h = int(hdr['w']), int(hdr['h'])
print('\nHEADER', hdr)

# nearby wires
print('\n--- wires within 140 units ---')
for wm in re.finditer(r'<Wire classid="WireOrthogonal"[^>]*>.*?</Wire>', s, re.S):
    blk = wm.group(0)
    hh = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
    wx, wy = int(hh['x']), int(hh['y'])
    vs = [(int(a), int(b)) for a, b in re.findall(r'<vertex x="(-?\d+)" y="(-?\d+)"', blk)]
    if not vs:
        continue
    xs = [wx + a for a, b in vs]
    ys = [wy + b for a, b in vs]
    if (min(xs) - 140 < x + w and max(xs) + 140 > x and
            min(ys) - 140 < y + h and max(ys) + 140 > y):
        print(' ', [(wx + a, wy + b) for a, b in vs])
