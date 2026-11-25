r"""S26: cold-start copy of ib6 at another time step (P13), for the 18 Hz ripple falsifier.

A snapshot is tied to the project's own .map and to the time step (S25 §5), so a dt test cannot use
ib6b_settled32.snp.  This makes a renamed cold-start case (no snapshot) in its own build folder,
exactly as C:\PSCAD_work\s25dt50\ was made for the S25 time-step test.

usage: python stage12\make_dt_copy.py --src C:/PSCAD_work/s25/ib6.pscx --dst C:/PSCAD_work/s26dt10/ib6dt10.pscx --dt 10 --dur 5
"""
import argparse, re

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True)
ap.add_argument("--dst", required=True)
ap.add_argument("--name", default=None, help="new project name (default ib6dt<dt>)")
ap.add_argument("--dt", type=float, default=10.0, help="time step [us]")
ap.add_argument("--sample", type=float, default=None, help="sample step [us] (default 10 x dt)")
ap.add_argument("--dur", type=float, default=5.0, help="time_duration [s]")
a = ap.parse_args()

new = a.name or "ib6dt%g" % a.dt
sample = a.sample if a.sample is not None else 10 * a.dt

txt = open(a.src, encoding="utf-8").read()
n_old = txt.count('"ib6:')
txt = txt.replace('<project name="ib6"', '<project name="%s"' % new)
txt = txt.replace('"ib6:', '"%s:' % new)
assert 'ib6:' not in txt.replace('"%s:' % new, ''), "leftover ib6: prefix"
txt = re.sub(r'(<param name="time_step" value=")[^"]*(")', r'\g<1>%g\g<2>' % a.dt, txt)
txt = re.sub(r'(<param name="sample_step" value=")[^"]*(")', r'\g<1>%g\g<2>' % sample, txt)
txt = re.sub(r'(<param name="time_duration" value=")[^"]*(")', r'\g<1>%g\g<2>' % a.dur, txt)
txt = re.sub(r'(<param name="StartType" value=")[^"]*(")', r'\g<1>0\g<2>', txt)          # STANDARD (cold)
txt = re.sub(r'(<param name="SnapType" value=")[^"]*(")', r'\g<1>0\g<2>', txt)           # 0 = NONE
txt = re.sub(r'(<param name="remove_time_offset" value=")[^"]*(")', r'\g<1>1\g<2>', txt)  # cold start
open(a.dst, "w", encoding="utf-8").write(txt)
print("written %s: project %s, dt %g us, sample %g us, duration %g s, %d prefixes renamed"
      % (a.dst, new, a.dt, sample, a.dur, n_old))
