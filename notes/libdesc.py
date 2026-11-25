import re, sys
path = r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx'
s = open(path, encoding='utf-8', errors='replace').read()
for name in ('xnode', 'nodelabel', 'ground'):
    m = re.search(r'<Definition classid="UserCmpDefn" name="%s"' % re.escape(name), s)
    if not m:
        print('no defn', name)
        continue
    a = m.start()
    b = s.find('</Definition>', a)
    blk = s[a:b]
    d = re.search(r'name="Description" value="([^"]*)"', blk)
    print('=' * 10, name, '->', d.group(1) if d else '?')
    for h in re.findall(r'<help><!\[CDATA\[(.*?)\]\]></help>', blk, re.S)[:6]:
        print('   help:', h[:300])
