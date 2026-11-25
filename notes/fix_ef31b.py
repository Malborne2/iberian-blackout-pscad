"""Clone a const block to create the missing EFG31, without touching the original."""
import re, os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
import xmlutil as X

s = X.load()
target = None
for m in re.finditer(r'\s*<User classid="UserCmp"[^>]*>.*?</User>', s, re.S):
    blk = m.group(0)
    if 'value="EFG30"' in blk:
        target = (m.start(), m.end(), blk)
        break
if target is None:
    print('EFG30 not found')
    raise SystemExit(1)

a, b, blk = target
new = blk.replace('value="EFG30"', 'value="EFG31"')
new = re.sub(r'\bid="\d+"', 'id="%d"' % random.randrange(10 ** 8, 2 * 10 ** 9), new, count=1)
new = re.sub(r'\bx="\d+" y="\d+"', 'x="378" y="2754"', new, count=1)

used = set(re.findall(r'\bid="(\d+)"', s))
while True:
    wid = random.randrange(10 ** 8, 2 * 10 ** 9)
    if str(wid) not in used:
        break
wire = ('\n        <Wire classid="WireOrthogonal" id="%d" name="" x="414" y="2754" '
        'w="10" h="64" orient="0" disable="false">\n'
        '          <vertex x="0" y="0" />\n'
        '          <vertex x="0" y="54" />\n'
        '        </Wire>\n' % wid)

s = s[:b] + new + wire + s[b:]
X.save(s)
print('created EFG31 at (378,2754) with a wire to (414,2808)')
