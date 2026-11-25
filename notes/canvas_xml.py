"""Find the Main canvas size attributes in the .pscx so the canvas can be enlarged."""
import re

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
i = s.find('classid="UserCmpDefn" name="Main"')
print('Main defn at', i)
print(s[i - 200:i + 600])
print('---- first <schematic> header ----')
j = s.find('<schematic')
print(s[j:j + 300])
print('---- canvas-ish tags ----')
for m in re.finditer(r'<(UserCanvas|RowCanvas|StationCanvas)\b[^>]*>', s):
    print(m.group(0)[:200])
    if m.start() > 40000:
        break
