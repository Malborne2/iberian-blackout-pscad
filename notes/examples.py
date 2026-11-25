"""Show first examples of each classid."""
import re

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()

for cid in ['WireOrthogonal', 'UserCmp', 'Port', 'Graphics.Text']:
    i = s.find('classid="%s"' % cid)
    a = s.rfind('<', 0, i)
    b = s.find('</', i)
    b2 = s.find('>', b)
    print('=' * 20, cid, 'at', i)
    print(s[a:b2 + 1][:2500])
    print()
