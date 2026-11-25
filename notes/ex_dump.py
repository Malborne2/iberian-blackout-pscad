"""Dump the machine / exciter / governor / turbine blocks and every wire of an example."""
import re, sys

path = sys.argv[1]
s = open(path, encoding='utf-8', errors='replace').read()

KEYS = ('sync_machine', 'excac', 'excst', 'excdc', 'exc_scrx', 'hy_gov', 'th_gov',
        'hy_tur', 'th_tur', 'const', 'multimeter', 'ground', 'breaker3')

print('=== key components ===')
for m in re.finditer(r'<User\b[^>]*>.*?</User>', s, re.S):
    blk = m.group(0)
    hdr = blk[:blk.find('>')]
    d = dict(re.findall(r'(\w+)="([^"]*)"', hdr))
    defn = d.get('defn', '')
    if not any(k in defn for k in KEYS):
        continue
    print('\n### %-22s id=%-11s x=%4s y=%4s w=%s h=%s o=%s'
          % (defn, d.get('id'), d.get('x'), d.get('y'), d.get('w'), d.get('h'), d.get('orient')))
    for k2, v2 in re.findall(r'name="(\w+)" value="([^"]*)"', blk):
        print('    %-12s %s' % (k2, v2))

print('\n=== wires ===')
for m in re.finditer(r'<Wire classid="WireOrthogonal"[^>]*>.*?</Wire>', s, re.S):
    blk = m.group(0)
    d = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
    x, y = int(d['x']), int(d['y'])
    pts = [(x + int(a), y + int(b))
           for a, b in re.findall(r'<vertex x="(-?\d+)" y="(-?\d+)"', blk)]
    print('  ', pts)
