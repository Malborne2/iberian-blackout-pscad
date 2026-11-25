"""Delete the source3 whose header position matches, plus any wire left dangling."""
import re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import xmlutil as X

x, y = int(sys.argv[1]), int(sys.argv[2])
s = X.load()
n = 0


def fix(m):
    global n
    blk = m.group(0)
    hdr = blk[:blk.find('>')]
    if 'defn="master:source3"' not in hdr:
        return blk
    d = dict(re.findall(r'(\w+)="([^"]*)"', hdr))
    if int(d.get('x', -1)) == x and int(d.get('y', -1)) == y:
        n += 1
        print('deleting source3 at', (x, y), 'id', d.get('id'))
        return ''
    return blk


s = re.sub(r'\s*<User\b[^>]*>.*?</User>', fix, s, flags=re.S)
X.save(s)
print('deleted', n)
