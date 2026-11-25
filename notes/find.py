import sys, hashlib
S = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
print('len', len(S), 'md5', hashlib.md5(S.encode('utf-8', 'replace')).hexdigest())
needle = sys.argv[1]
i = S.find(needle)
print('needle', repr(needle), 'idx', i, 'count', S.count(needle))
