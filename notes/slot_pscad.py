"""Ask PSCAD for the nearest empty rectangle of machine size next to each generator bus."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

BUSES = [('Bus30', 27, 17), ('Bus31', 34, 83), ('Bus32', 43, 94), ('Bus33', 58, 89),
         ('Bus34', 51, 89), ('Bus35', 64, 43), ('Bus36', 64, 81), ('Bus37', 32, 10),
         ('Bus38', 68, 31), ('Bus39', 24, 55)]

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
print('canvas size', main.size)
for name, bx, by in BUSES:
    for w, h in ((7, 9), (9, 11)):
        try:
            r = main.closest_empty_rect(w, h, (bx, by))
            print('%-6s size %dx%d -> left=%s top=%s right=%s bottom=%s  (dist %s)'
                  % (name, w, h, r.left, r.top, r.right, r.bottom,
                     abs(r.left - bx) + abs(r.top - by)))
        except Exception as e:
            print('%-6s size %dx%d ERR %s %s' % (name, w, h, type(e).__name__, e))
