import re, collections

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
c = collections.Counter(re.findall(r'<User classid="UserCmp"[^>]*?defn="([^"]+)"', s))
for k, v in c.most_common(24):
    print('%4d  %s' % (v, k))

print('\n--- duplicate (defn, x, y, Name) groups ---')
seen = collections.Counter()
for m in re.finditer(r'<User classid="UserCmp"[^>]*>.*?</User>', s, re.S):
    blk = m.group(0)
    h = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
    nm = re.search(r'name="Name" value="([^"]*)"', blk)
    seen[(h.get('defn'), h['x'], h['y'], nm.group(1) if nm else '')] += 1
for k, v in seen.items():
    if v > 1:
        print(v, k)
