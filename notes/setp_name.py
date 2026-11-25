"""Set a parameter of a component identified by its Name.

Usage: python notes/setp_name.py <Name> <param> <value> [<Name2> <param2> <val2> ...]
Example: python notes/setp_name.py RES_C1 PO 1433.333 T_C1 V2 135.96
"""
import re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import xmlutil as X

args = sys.argv[1:]
assert len(args) % 3 == 0, 'give triples: Name param value'
triples = [args[i:i + 3] for i in range(0, len(args), 3)]

s = X.load()


def fix(m):
    blk = m.group(0)
    nm = re.search(r'name="Name" value="([^"]*)"', blk)
    name = nm.group(1) if nm else None
    for tn, tp, tv in triples:
        if name != tn:
            continue
        new, n = re.subn(r'(name="%s" value=")[^"]*(")' % re.escape(tp),
                         lambda mm: mm.group(1) + tv + mm.group(2), blk)
        if n:
            print('  %s.%s = %s' % (tn, tp, tv))
            blk = new
    return blk


s = re.sub(r'\s*<User\b[^>]*>.*?</User>', fix, s, flags=re.S)
X.save(s)
print('written')
