"""Show the RES_C1 source3 block params (look for odd signal names)."""
import re

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
for m in re.finditer(r'<User classid="UserCmp"[^>]*?defn="master:source3"[^>]*>.*?</User>', s, re.S):
    blk = m.group(0)
    if 'RES_C1' not in blk:
        continue
    for k, v in re.findall(r'name="(\w+)" value="([^"]*)"', blk):
        print('%-8s %s' % (k, v))
    break
