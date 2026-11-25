"""Inventory an example .pscx: component definitions used, and the elements that touch a
named/defn component of interest."""
import re, sys, collections

path = sys.argv[1]
want = sys.argv[2] if len(sys.argv) > 2 else None

s = open(path, encoding='utf-8', errors='replace').read()
print('%s  %d chars' % (path.split('\\')[-1], len(s)))

c = collections.Counter(re.findall(r'<User classid="UserCmp"[^>]*?defn="([^"]+)"', s))
print('--- component inventory ---')
for k, v in c.most_common():
    print('%4d  %s' % (v, k))

if want:
    print('\n--- blocks mentioning %s ---' % want)
    for m in re.finditer(r'<User\b[^>]*>.*?</User>', s, re.S):
        blk = m.group(0)
        if want not in blk:
            continue
        hdr = blk[:blk.find('>')]
        d = dict(re.findall(r'(\w+)="([^"]*)"', hdr))
        print('\n###', d.get('defn'), 'id', d.get('id'), 'at', (d.get('x'), d.get('y')),
              'orient', d.get('orient'))
        for k2, v2 in re.findall(r'name="(\w+)" value="([^"]*)"', blk):
            print('    %-12s %s' % (k2, v2))
