"""Print the Port elements of a master library definition."""
import re, sys

path = r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx'
s = open(path, encoding='utf-8', errors='replace').read()
name = sys.argv[1]

m = re.search(r'<Definition classid="UserCmpDefn" name="%s"' % re.escape(name), s)
if not m:
    print('not found')
    sys.exit()
a = m.start()
b = s.find('</Definition>', a)
blk = s[a:b]
print('defn length', len(blk))
ports = re.findall(r'<Port[^>]*>.*?</Port>', blk, re.S) or re.findall(r'<Port[^>]*/>', blk)
print('ports:', len(ports))
for p in ports:
    d = dict(re.findall(r'(\w+)="([^"]*)"', p))
    nm = re.search(r'name" value="([^"]*)"', p)
    print('  ', {k: d[k] for k in ('id', 'x', 'y', 'classid') if k in d}, 'name=', nm.group(1) if nm else '?')
