"""Set the machine reactances so that a FIXED field still holds ~1.0 pu.

A machine with Xd = 1.9 pu cannot hold 1.0 pu with a fixed field (it needs E ~ 2 pu, which
drives the network unstable at this load level).  Lowering Xd/Xq approximates the effect of
the missing AVR on the network: the machine becomes a stiff voltage source that still has
inertia H, so the frequency dynamics (which is what the event study needs) are preserved.

Usage: python notes/tune_machines.py [efld]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools
import re
import xmlutil as X

EF = sys.argv[1] if len(sys.argv) > 1 else '1.05'
MACH = ['SMG30', 'SMG31', 'SMG32', 'SMG33', 'SMG34', 'SMG35']
CONST = ['EFG30', 'EFG31', 'EFG32', 'EFG33', 'EFG34', 'EFG35']
PARAMS = {'Xd': '0.45', 'Xq': '0.43', 'Xd_': '0.25', 'Xq_': '0.22',
          'Xd__': '0.15', 'Xq__': '0.14', 'Xp': '0.10'}

try:
    ptools.save_unload()
    print('offloaded')
except Exception:
    pass

s = X.load()
n = 0


def fix(m):
    global n
    blk = m.group(0)
    nm = re.search(r'name="Name" value="([^"]*)"', blk)
    if not nm:
        return blk
    name = nm.group(1)
    if name in MACH:
        for k, v in PARAMS.items():
            blk, c = re.subn(r'(name="%s" value=")[^"]*(")' % k,
                             lambda mm, v=v: mm.group(1) + v + mm.group(2), blk)
            n += c
    elif name in CONST:
        blk, c = re.subn(r'(name="Value" value=")[^"]*(")',
                         lambda mm: mm.group(1) + EF + mm.group(2), blk)
        n += c
    return blk


s = re.sub(r'\s*<User\b[^>]*>.*?</User>', fix, s, flags=re.S)
X.save(s)
print('parameters updated:', n)
