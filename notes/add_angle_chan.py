"""Log the rotor angle of a machine (nameable signal) -> frequency by differentiation.

sync_machine2 has nameable outputs Theta (rotor mechanical angle) and Wang.  Setting
Theta='TH_Gxx' publishes that signal, which the normal datalabel -> pgb channel picks up.
Frequency is then f = (1/2pi) d(theta)/dt in post-processing.

Usage: python notes/add_angle_chan.py <machine Name> <tag>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

MACH = sys.argv[1]
TAG = sys.argv[2]

app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')

sm = None
for c in main.components():
    try:
        if str(c.parameters().get('Name', '')) == MACH:
            sm = c
            break
    except Exception:
        pass
if sm is None:
    ptools.log('machine not found:', MACH)
    raise SystemExit(1)

sm.parameters(Theta='TH_' + TAG)
ptools.log('theta signal set on', MACH)

dl = main.create_component('master:datalabel', 100, 156, Name='TH_' + TAG)
pg = main.create_component('master:pgb', 108, 156, Name='TH_' + TAG, UseSignalName='YES',
                           enab='YES', Display='YES', Units='rad', Scale=1.0,
                           Min=-100.0, Max=100.0)
try:
    main.create_connection(dl.port('A'), pg.port('Signl'))
    ptools.log('channel wired')
except Exception as e:
    ptools.log('ERR', type(e).__name__, e)
pr.save()
ptools.log('saved TH_' + TAG)
