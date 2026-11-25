"""Show the raw XML of the first element with a given attribute value."""
import re, sys

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
needle = sys.argv[1]
i = s.find(needle)
print('index', i)
if i >= 0:
    a = s.rfind('<', 0, i)
    tag = re.match(r'<(\w+)', s[a:]).group(1)
    b = s.find('</%s>' % tag, a)
    print(s[a:b + len(tag) + 3])
