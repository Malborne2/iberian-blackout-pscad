"""Report counts and positions of datalabel/pgb blocks in one or more files."""
import re, sys, os, collections

for path in sys.argv[1:]:
    s = open(path, encoding='utf-8', errors='replace').read()
    print('=' * 70)
    print(os.path.basename(path), len(s), 'chars')
    for defn in ('master:datalabel', 'master:pgb'):
        pos = collections.Counter()
        n = 0
        for m in re.finditer(r'<User\b[^>]*>', s):
            h = m.group(0)
            if 'defn="%s"' % defn in h or 'name="%s"' % defn in h:
                d = dict(re.findall(r'(\w+)="([^"]*)"', h))
                pos[(d.get('x'), d.get('y'))] += 1
                n += 1
        print('%-18s %3d blocks' % (defn, n))
        for k, v in sorted(pos.items())[:6]:
            print('      ', k, v)
    print('wires', len(re.findall(r'<Wire classid="WireOrthogonal"', s)))
