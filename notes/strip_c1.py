"""Strip the first collector-group attempt (region x>=430, y>=1950) and its nodelabels."""
import re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import xmlutil as X

s = X.load()

# 1. everything in the group region
reg = re.compile(r'\s*<(Wire|User|Gfx)\b[^>]*?(?:x="(\d+)"[^>]*?y="(\d+)")[^>]*>.*?</\1>', re.S)
removed = []

def repl(m):
    x = int(m.group(2) or 0)
    y = int(m.group(3) or 0)
    if x >= 430 and 1850 <= y <= 2400:
        removed.append((m.group(1), x, y))
        return ''
    return m.group(0)

s = reg.sub(repl, s)
print('removed', len(removed), 'elements')
for r in removed:
    print('  ', r)

# 2. the nodelabel pair (one is at 612,2052 - already gone; the other on Bus1)
s = re.sub(r'\s*<User classid="UserCmp"[^>]*defn="master:nodelabel"[^>]*>.*?</User>', '', s, flags=re.S)

X.save(s)
s = X.load()
print('users', len(re.findall(r'<User classid="UserCmp"', s)),
      'buses', len(re.findall(r'<Wire classid="Bus"', s)),
      'wires', len(re.findall(r'<Wire classid="WireOrthogonal"', s)))
