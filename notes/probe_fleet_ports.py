"""Print the ports of a machine created with the fleet parameters (checks port layout)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
sm = main.create_component('master:sync_machine2', 19, 15, 0, Name='PRBFLT',
                           MVA=1130.0, Vbase_LL=400.0, FRE=50.0, H=5.0, NOM=1.0,
                           MSat=0, MM=1, Ra=0.002, Xp=0.10, Xd=0.45, Xd_=0.25,
                           Tdo_=8.0, Xd__=0.15, Tdo__=0.03, Xq=0.43, Xq_=0.22,
                           Xq__=0.14, P0=1000.0, Q0=0.0, VT=1.0, Pheta=0.0,
                           T_S2M=0.5, Iexc=0, Igov=0, Interface_E=0, Interface_G=0,
                           POut='P_PRB', QOut='Q_PRB')
b = sm.bounds
ptools.log('bounds', (b.left, b.top, b.right, b.bottom))
for k, v in sm.ports().items():
    ptools.log('  %-8s (%d,%d)' % (k, v.location[0], v.location[1]))
sm.delete()
pr.save()
