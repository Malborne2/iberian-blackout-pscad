"""Delete the stray probe bus at xml (1746,2412) by header regex; verify."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
import xmlutil as X

s = X.load()
pat = re.compile(r'\s*<Wire classid="Bus"[^>]*?x="1746" y="2412".*?</Wire>', re.S)
s2, n = pat.subn('', s)
print('removed', n, 'delta', len(s) - len(s2))
X.save(s2)
s = X.load()
print('still there?', 'y="2412"' in s)
print('buses', len(re.findall(r'<Wire classid="Bus"', s)))
