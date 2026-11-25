"""Report basic element counts of a .pscx/.bakx file."""
import re, sys, os

for path in sys.argv[1:]:
    try:
        s = open(path, encoding='utf-8', errors='replace').read()
    except Exception as e:
        print(path, 'ERR', e)
        continue
    print('%-34s %8d chars  buses=%d users=%d wires=%d  C1_400=%d C1_132=%d nodelabel=%d'
          % (os.path.basename(path), len(s),
             len(re.findall(r'<Wire classid="Bus"', s)),
             len(re.findall(r'<User classid="UserCmp"', s)),
             len(re.findall(r'<Wire classid="WireOrthogonal"', s)),
             s.count('"C1_400"'), s.count('"C1_132"'),
             len(re.findall(r'defn="master:nodelabel"', s))))
