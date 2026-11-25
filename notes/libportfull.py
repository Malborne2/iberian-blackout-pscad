"""Show Port elements of a library defn with their full params."""
import re, sys

path = r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx'
s = open(path, encoding='utf-8', errors='replace').read()
name = sys.argv[1]
m = re.search(r'<Definition classid="UserCmpDefn" name="%s"' % re.escape(name), s)
a = m.start()
b = s.find('</Definition>', a)
blk = s[a:b]
for p in re.finditer(r'<Port\b[^>]*>.*?</Port>', blk, re.S):
    print(re.sub(r'\s+', ' ', p.group(0)))
