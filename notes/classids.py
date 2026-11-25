"""List all distinct classid values and show one example of a connection."""
import re, collections

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
c = collections.Counter(re.findall(r'classid="([^"]+)"', s))
for k, v in c.most_common():
    print(f'{v:4d}  {k}')

print()
print('--- look for Connection / Wire classids ---')
for m in re.finditer(r'classid="([^"]*onnection[^"]*)"', s):
    print(m.start(), m.group(1))
    break
