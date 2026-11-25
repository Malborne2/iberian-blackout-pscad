"""List multimeter signal names."""
import re

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
for m in re.finditer(r'<User classid="UserCmp"[^>]*?defn="master:multimeter"[^>]*>.*?</User>', s, re.S):
    blk = m.group(0)
    h = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
    d = dict(re.findall(r'name="(\w+)" value="([^"]*)"', blk))
    print('%-10s %s  P=%-8s Q=%-8s Vrms=%-8s Pd=%s'
          % (h['x'], h['y'], d.get('P'), d.get('Q'), d.get('Vrms'), d.get('Pd')))
