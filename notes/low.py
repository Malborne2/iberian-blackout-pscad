"""List elements whose header y >= a threshold, to find a free region."""
import re, sys

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
ythr = int(sys.argv[1]) if len(sys.argv) > 1 else 1900
for m in re.finditer(r'<(Wire|User|Gfx)\b[^>]*>', s):
    h = m.group(0)
    d = dict(re.findall(r'(\w+)="([^"]*)"', h))
    try:
        y = int(d['y'])
        x = int(d['x'])
    except (KeyError, ValueError):
        continue
    if y >= ythr:
        print('%-14s %-34s x=%5s y=%5s' % (d.get('classid'), d.get('defn', ''), x, y))
