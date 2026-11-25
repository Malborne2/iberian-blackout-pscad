"""Print a window of the raw .pscx text around a needle."""
import sys

S = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
needle = sys.argv[1]
before = int(sys.argv[2]) if len(sys.argv) > 2 else 700
after = int(sys.argv[3]) if len(sys.argv) > 3 else 500
i = S.find(needle)
print('idx', i)
if i >= 0:
    print(S[max(0, i - before): i + after])
