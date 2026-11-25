import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import xmlutil as X

s = X.load()
eid = sys.argv[1]
sp = X.block_span(s, eid)
print('span', sp)
if sp:
    print(s[sp[0]:sp[1]][:900])
