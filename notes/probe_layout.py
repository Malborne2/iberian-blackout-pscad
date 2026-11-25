"""Print exact bounds and port offsets of a probe sync_machine2 (for layout planning)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
c = main.create_component('master:sync_machine2', 200, 200, 0, Name='PRBLAY',
                          MVA=1130.0, Vbase_LL=400.0, FRE=50.0, H=5.0, P0=1000.0,
                          Q0=0.0, VT=1.0, T_S2M=0.5, MSat=0, MM=1)
b = c.bounds
ptools.log('bounds', (b.left, b.top, b.right, b.bottom))
for k, v in c.ports().items():
    ptools.log('  %-8s (%d,%d)  rel (%d,%d)' % (k, v.location[0], v.location[1],
                                                v.location[0] - 200, v.location[1] - 200))
c.delete()
pr.save()
