"""Shift every ND_* node label by +1 grid unit in x (test for label/junction interaction)."""
import re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import xmlutil as X

s = X.load()
n = 0


def fix(m):
    global n
    blk = m.group(0)
    nm = re.search(r'name="Name" value="(ND_\w+)"', blk)
    if not nm:
        return blk
    hdr_end = blk.find('>')
    hdr = blk[:hdr_end]
    mm = re.search(r'\bx="(\d+)" y="(\d+)"', hdr)
    if not mm:
        return blk
    x, y = int(mm.group(1)), int(mm.group(2))
    new = re.sub(r'\bx="\d+" y="\d+"', 'x="%d" y="%d"' % (x + 18, y), blk, count=1)
    n += 1
    return new


s = re.sub(r'\s*<User\b[^>]*>.*?</User>', fix, s, flags=re.S)
X.save(s)
print('shifted', n, 'node labels')
