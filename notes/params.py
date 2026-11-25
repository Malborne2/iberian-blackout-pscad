"""Print all params of the first instance of a defn."""
import re, sys

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
defn = sys.argv[1]
for m in re.finditer(r'<User\b[^>]*defn="([^"]+)"[^>]*>.*?</User>', s, re.S):
    b = m.group(0)
    if dict(re.findall(r'(\w+)="([^"]*)"', b[:b.find('>')]))['defn'] == defn:
        for k, v in re.findall(r'name="(\w+)" value="([^"]*)"', b):
            print('%-8s %s' % (k, v))
        break
