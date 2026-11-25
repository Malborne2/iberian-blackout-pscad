"""Delete components by Name (XML).  Usage: python notes/del_name.py EFG30 EFG31 ..."""
import re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import xmlutil as X

names = set(sys.argv[1:])
s = X.load()
n = 0


def fix(m):
    global n
    blk = m.group(0)
    if 'classid="UserCmp"' not in blk[:blk.find('>')]:
        return blk
    nm = re.search(r'name="Name" value="([^"]*)"', blk)
    if nm and nm.group(1) in names:
        n += 1
        print('   deleted', nm.group(1))
        return ''
    return blk


s = re.sub(r'\s*<User\b[^>]*>.*?</User>', fix, s, flags=re.S)
X.save(s)
print('deleted', n)
