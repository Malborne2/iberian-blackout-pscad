"""Print component inventory of the working .pscx."""
import re, collections, sys

path = sys.argv[1] if len(sys.argv) > 1 else 'Spanish_grid_model.pscx'
s = open(path, encoding='utf-8', errors='replace').read()
print('chars', len(s))

c = collections.Counter(re.findall(r'<component[^>]*?defn="([^"]+)"', s))
if not c:
    c = collections.Counter(re.findall(r'defn="([^"]+)"', s))
for k, v in c.most_common():
    print(f'{v:4d}  {k}')

names = re.findall(r'name="Name" value="([^"]*)"', s)
print('--- names (%d) ---' % len(names))
print(' | '.join(names))
