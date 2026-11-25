"""Clone the EFG30 const block into an EFG31 const at (378,2754) and wire it to efldn."""
import re, os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
import xmlutil as X

s = X.load()

m = re.search(r'\s*<User classid="UserCmp"[^>]*>.*?name="Name" value="EFG30".*?</User>', s, re.S)
blk = m.group(0)
new = blk.replace('value="EFG30"', 'value="EFG31"').replace('value="1.05"', 'value="1.05"')
new = re.sub(r'\bid="\d+"', 'id="%d"' % random.randrange(10 ** 8, 2 * 10 ** 9), new, count=1)
new = re.sub(r'\bx="\d+" y="\d+"', 'x="378" y="2754"', new, count=1)
s = s[:m.end()] + new + s[m.end():]

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
i = s.rindex('</schematic>')
s = s[:i] + wire + '      ' + s[i:]
X.save(s)
print('EFG31 cloned + wired')
