"""Compare element ids between the current project and a backup to find lost elements."""
import re, sys, os
sys.path.insert(0, os.path.dirname(__file__))


def ids(path):
    s = open(path, encoding='utf-8', errors='replace').read()
    out = {}
    for m in re.finditer(r'<Wire classid="WireOrthogonal"[^>]*>', s):
        h = m.group(0)
        i = re.search(r'\bid="([^"]*)"', h).group(1)
        out[i] = h
    return out


cur = ids('Spanish_grid_model.pscx')
for ref in sys.argv[1:]:
    old = ids(ref)
    lost = set(old) - set(cur)
    new = set(cur) - set(old)
    print(ref, 'wires', len(old), '->', len(cur), 'lost', len(lost), 'new', len(new))
    for i in lost:
        print('   LOST', old[i][:150])
