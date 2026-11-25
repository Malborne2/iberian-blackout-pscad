"""Fix up the C1 pilot group in the XML: drop the stray probe bus, name the 132 kV bus."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import xmlutil as X

s = X.load()

# 1. stray bus from probe_geom.py
s = X.remove(s, '1781359292')

# 2. collector bus of group C1
s = X.setp(s, '1926451628', 'Name', 'C1_132')
s = X.setp(s, '1926451628', 'BaseKV', '132.0')

X.save(s)
print('bus count now', len([1 for m in X.BLOCK.finditer(s)
                             if 'classid="Bus"' in s[m.start():m.start() + 120]]))
print('C1_132 base', X.get(s, '1926451628', 'BaseKV'))
