import re, sys, os
path = r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx'
s = open(path, encoding='utf-8', errors='replace').read()
for name in ('Bus', 'nodelabel'):
    m = re.search(r'<Definition classid="UserCmpDefn" name="%s"' % re.escape(name), s)
    if not m:
        print('no defn', name)
        continue
    a = m.start()
    b = s.find('</Definition>', a)
    blk = s[a:b]
    print('=' * 30, name, len(blk))
    for p in re.finditer(r'<parameter [^>]*name="(\w+)"[^>]*>(.*?)</parameter>', blk, re.S):
        print('---', p.group(1))
        print(re.sub(r'\s+', ' ', p.group(2))[:800])
