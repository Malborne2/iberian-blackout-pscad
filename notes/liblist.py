"""List every definition name in a library file, optionally filtered."""
import re, sys

path = sys.argv[1] if len(sys.argv) > 1 else r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx'
kw = sys.argv[2].lower() if len(sys.argv) > 2 else ''
s = open(path, encoding='utf-8', errors='replace').read()
names = re.findall(r'<Definition classid="UserCmpDefn" name="([^"]+)"', s)
hit = [n for n in names if kw in n.lower()]
print('total defs', len(names), 'matching', len(hit))
for n in sorted(hit):
    print('  ', n)
