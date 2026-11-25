"""List Name + params for every component of a given defn."""
import re, sys

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
defn = sys.argv[1]
keys = sys.argv[2].split(',') if len(sys.argv) > 2 else ['Name', 'PO', 'QO']
for m in re.finditer(r'<User\b[^>]*defn="([^"]+)"[^>]*>.*?</User>', s, re.S):
    blk = m.group(0)
    hdr = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
    if hdr['defn'] != defn:
        continue
    vals = {}
    for k in keys:
        mm = re.search(r'name="%s" value="([^"]*)"' % k, blk)
        vals[k] = mm.group(1) if mm else None
    print((hdr['x'], hdr['y'], hdr['w'], hdr['h'], 'o%s' % hdr.get('orient')), vals)
