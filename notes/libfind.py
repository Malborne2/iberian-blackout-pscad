"""Find library definitions whose name mentions a keyword, plus their port count/dims."""
import re, sys

path = r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx'
s = open(path, encoding='utf-8', errors='replace').read()
kw = sys.argv[1].lower()
for m in re.finditer(r'<Definition classid="UserCmpDefn" name="([^"]+)"', s):
    nm = m.group(1)
    if kw in nm.lower():
        a = m.start()
        b = s.find('</Definition>', a)
        blk = s[a:b]
        ports = re.findall(r'<Port\b[^>]*x="(-?\d+)" y="(-?\d+)"[^>]*>.*?name" value="([^"]*)"', blk, re.S)
        print('%-28s ports=%s' % (nm, ports[:8]))
