"""Show the View/YD/Lead/SD parameter definitions of a library component."""
import re, sys

path = r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx'
s = open(path, encoding='utf-8', errors='replace').read()
name = sys.argv[1]
want = sys.argv[2].split(',') if len(sys.argv) > 2 else ['View']

m = re.search(r'<Definition classid="UserCmpDefn" name="%s"' % re.escape(name), s)
a = m.start()
b = s.find('</Definition>', a)
blk = s[a:b]
for p in re.finditer(r'<parameter [^>]*name="(\w+)"[^>]*>(.*?)</parameter>', blk, re.S):
    if p.group(1) not in want:
        continue
    print('=' * 20, p.group(1))
    print(re.sub(r'\s+', ' ', p.group(2))[:1500])
