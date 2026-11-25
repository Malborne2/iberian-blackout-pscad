"""Dump raw XML of all drawing elements inside an XML bounding window."""
import re, sys

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
x0, y0, x1, y1 = (int(v) for v in sys.argv[1:5])

for m in re.finditer(r'<(Wire|User|Gfx)\b[^>]*>.*?</\1>', s, re.S):
    blk = m.group(0)
    hdr = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
    try:
        bx, by = int(hdr['x']), int(hdr['y'])
        bw, bh = int(hdr.get('w', 0)), int(hdr.get('h', 0))
    except (KeyError, ValueError):
        continue
    if x0 <= bx <= x1 and y0 <= by <= y1:
        # compact: header + Name/PO/QO + vertices
        name = re.search(r'name="Name" value="([^"]*)"', blk)
        po = re.search(r'name="PO" value="([^"]*)"', blk)
        vs = re.findall(r'<vertex x="(-?\d+)" y="(-?\d+)"', blk)
        print(hdr.get('classid'), hdr.get('defn', ''), 'x=%s y=%s w=%s h=%s o=%s' % (bx, by, bw, bh, hdr.get('orient')),
              'name=%s' % (name.group(1) if name else ''),
              'PO=%s' % (po.group(1) if po else ''),
              'verts=%s' % (vs if vs else ''))
