"""List all empty 11x15 rectangles and pick the nearest unused one for each generator bus."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

BUSES = [('Bus30', 27, 17), ('Bus31', 34, 83), ('Bus32', 43, 94), ('Bus33', 58, 89),
         ('Bus34', 51, 89), ('Bus35', 64, 43), ('Bus36', 64, 81), ('Bus37', 32, 10),
         ('Bus38', 68, 31), ('Bus39', 24, 55)]

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
rects = main.get_empty_rects(11, 15)
print('empty 11x15 rects:', len(rects))
cand = [(r.left, r.top, r.right, r.bottom) for r in rects]
print(cand[:25])

used = set()
assign = {}
for name, bx, by in BUSES:
    best = None
    for c in cand:
        key = (c[0], c[1])
        if key in used:
            continue
        d = abs(c[0] + 5 - bx) + abs(c[1] + 7 - by)
        if best is None or d < best[0]:
            best = (d, c)
    if best:
        used.add((best[1][0], best[1][1]))
        assign[name] = best[1]
        print('%-6s -> (%d,%d) dist %d' % (name, best[1][0], best[1][1], best[0]))
    else:
        print('%-6s -> none' % name)
