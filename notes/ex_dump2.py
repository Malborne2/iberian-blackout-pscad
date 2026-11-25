"""Dump an example's components + wires to a text file (robust, no pipes)."""
import re, sys, os, traceback

path = sys.argv[1]
out = sys.argv[2]
s = open(path, encoding='utf-8', errors='replace').read()
lines = []


def w(*a):
    lines.append(' '.join(str(x) for x in a))


try:
    for m in re.finditer(r'<User\b[^>]*>.*?</User>', s, re.S):
        blk = m.group(0)
        hdr = blk[:blk.find('>')]
        d = dict(re.findall(r'(\w+)="([^"]*)"', hdr))
        w('COMP', d.get('defn'), 'x=%s y=%s w=%s h=%s o=%s' %
          (d.get('x'), d.get('y'), d.get('w'), d.get('h'), d.get('orient')))
        for k2, v2 in re.findall(r'name="(\w+)" value="([^"]*)"', blk):
            w('   ', k2, '=', v2)
    w('')
    w('=== WIRES ===')
    for m in re.finditer(r'<Wire classid="WireOrthogonal"[^>]*>.*?</Wire>', s, re.S):
        blk = m.group(0)
        d = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
        x, y = int(d['x']), int(d['y'])
        pts = [(x + int(a), y + int(b))
               for a, b in re.findall(r'<vertex x="(-?\d+)" y="(-?\d+)"', blk)]
        w('WIRE', pts)
    w('')
    w('=== BUSES ===')
    for m in re.finditer(r'<Wire classid="Bus"[^>]*>.*?</Wire>', s, re.S):
        blk = m.group(0)
        d = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
        nm = re.search(r'name="Name" value="([^"]*)"', blk)
        w('BUS', nm.group(1) if nm else '?', 'x=%s y=%s w=%s' % (d.get('x'), d.get('y'), d.get('w')))
except Exception:
    w('ERROR')
    w(traceback.format_exc())

open(out, 'w', encoding='utf-8').write('\n'.join(lines))
print('wrote', out, len(lines), 'lines')
