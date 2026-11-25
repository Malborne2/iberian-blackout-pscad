"""Clone a machine/exciter/governor parameter set from a shipped example.

Reads sync_multiplemachines.pscx, takes the full parameter dict of one
sync_machine / exc_scrx / hydro_gov, and prints them as a Python dict so they can be
replayed through create_component (values keep their unit strings, which the API accepts).
"""
import re, sys, json

EX = r'C:\Users\Public\Documents\PSCAD\5.1.0\Examples\sync_machines\sync_multiplemachines.pscx'
s = open(EX, encoding='utf-8', errors='replace').read()

want = ['master:sync_machine', 'master:exc_scrx', 'master:hydro_gov']
out = {}
for defn in want:
    for m in re.finditer(r'<User\b[^>]*defn="%s"[^>]*>.*?</User>' % re.escape(defn), s, re.S):
        blk = m.group(0)
        hdr = blk[:blk.find('>')]
        d = dict(re.findall(r'(\w+)="([^"]*)"', hdr))
        params = dict(re.findall(r'<param name="(\w+)" value="([^"]*)"', blk))
        out[defn] = {'x': d.get('x'), 'y': d.get('y'), 'w': d.get('w'),
                     'h': d.get('h'), 'orient': d.get('orient'), 'params': params}
        break

with open('notes/ex_params.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1)

for defn, v in out.items():
    print('=' * 20, defn, 'at', (v['x'], v['y']), 'wh', (v['w'], v['h']), 'o', v['orient'])
    for k, val in v['params'].items():
        print('   %-10s %s' % (k, val))
