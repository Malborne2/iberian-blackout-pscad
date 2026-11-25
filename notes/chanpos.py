"""Inspect channel block positions and the canvas size."""
import re
import mhi.pscad as p

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
pos = {}
for m in re.finditer(r'<User classid="UserCmp"[^>]*?defn="master:(datalabel|pgb)"[^>]*>', s):
    h = dict(re.findall(r'(\w+)="([^"]*)"', m.group(0)))
    pos.setdefault((h['x'], h['y']), []).append(h['defn'].split(':')[1])
for k, v in sorted(pos.items()):
    print(k, len(v), v[:6])

app = p.connect()
app.load('Spanish_grid_model.pscx')
main = app.project('Spanish_grid_model').canvas('Main')
print('canvas size', main.size)
print('bounds', main.bounds)
