"""Print the raw XML block of the element whose header contains all given substrings."""
import re, sys

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
needles = sys.argv[1:]
for m in re.finditer(r'<(Wire|User|Gfx)\b[^>]*>.*?</\1>', s, re.S):
    blk = m.group(0)
    hdr = blk[:blk.find('>') + 1]
    if all(n in hdr for n in needles):
        print(blk)
        print('-' * 60)
