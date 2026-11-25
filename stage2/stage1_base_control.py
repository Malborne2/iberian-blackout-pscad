"""Is the +4 % offset of today's bus voltages in the rebased model a settling-time artefact?

Runs the pristine 60 Hz Bergeron base (`iberia_base.pscx`) for 3 s and reads the same ten
multimeters that the G1 comparison used at t = 0.2 s.

Run: python stage1_base_control.py
"""
import pscad_ops as P

PRJ = "base_ctrl"
P.connect()

if PRJ not in [p["name"] for p in P.app().projects()]:
    P.app().load(r"C:\PSCAD_work\iberia_base.pscx")
    print("clone:", P.save_as("iberia_base", PRJ, folder=r"C:\PSCAD_work"))

P.set_project_parameters(PRJ, {"time_step": 20.0, "time_duration": 3.0,
                               "sample_step": 200.0, "PlotType": "PSOUT"})
P.save(PRJ)
P.app().project(PRJ).clean()
P.app().project(PRJ).build()
errs = [x["text"] for x in P.messages(PRJ)["messages"] if x["status"].startswith("error")]
print("errors:", errs[:3])
P.run(PRJ, wait=True, poll=1.0, timeout=3600)
psout = P.find_output_file(PRJ)
print("psout:", psout)

import mhi.psout  # noqa: E402

with mhi.psout.File(psout) as f:
    run = f.run(0)
    for n in range(1, 11):
        tr = run.call(f"Root/Main/multimeter[{n}]/4/Vd", sep="/")
        vals = [round(v, 4) for v in tr.data]
        tt = [round(x, 2) for x in tr.domain.data]
        print(f"mm{n:>2}  t={tt}  Vd={vals}")
