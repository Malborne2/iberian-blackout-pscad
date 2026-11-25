"""Dump the XML snippet for a named component and its neighbours."""
import sys

path = 'Spanish_grid_model.pscx'
s = open(path, encoding='utf-8', errors='replace').read()

target = sys.argv[1] if len(sys.argv) > 1 else 'Bus1'
span = int(sys.argv[2]) if len(sys.argv) > 2 else 6000
i = s.find('"%s"' % target)
print('index', i)
print(s[max(0, i - span): i + span])
