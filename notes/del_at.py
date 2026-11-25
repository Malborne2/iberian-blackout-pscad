"""Delete the User component at an exact XML position (any definition)."""
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
    if 'classid="UserCmp"' not in hdr:
        return blk
    d = dict(re.findall(r'(\w+)="([^"]*)"', hdr))
    if int(d.get('x', -1)) == x and int(d.get('y', -1)) == y:
        n += 1
        print('deleting', d.get('defn'), 'at', (x, y))
        return ''
    return blk


s = re.sub(r'\s*<User\b[^>]*>.*?</User>', fix, s, flags=re.S)
X.save(s)
print('deleted', n)
