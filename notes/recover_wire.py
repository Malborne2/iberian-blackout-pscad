"""Re-insert the V_G39 signal wire (id 346521735) from the backup into the working file."""
import re
import xmlutil as X

REF = 'Spanish_grid_model.bakx'

ref = open(REF, encoding='utf-8', errors='replace').read()
m = re.search(r'<Wire classid="WireOrthogonal" id="346521735".*?</Wire>', ref, re.S)
blk = m.group(0)
print('recovered block:\n', blk)

s = X.load()
assert 'id="346521735"' not in s, 'already present'
i = s.rindex('</schematic>')
s = s[:i] + '        ' + blk + '\n      ' + s[i:]
X.save(s)
print('len', len(s))
print('present now:', 'id="346521735"' in X.load())
