"""Control run: the pristine `iberia1_stage1.pscx` as it sits on disk, nothing changed.

Question: do the ten generator buses read the same `Vd` as the G1 sign-off table in
RUNLOG Session 4 (1.0253, 0.9861, 0.9408, 1.0077, 0.9378, 0.9598, 0.9772, 0.9886,
1.0106, 0.9849), or as the iberia3 run of this session?

Run: python stage1_control_run.py
"""
import pscad_ops as P

PRJ = "iberia1_ctrl"
P.connect()

if PRJ not in [p["name"] for p in P.app().projects()]:
    P.app().load(r"C:\PSCAD_work\iberia1_stage1.pscx")
    print("clone:", P.save_as("iberia1_stage1", PRJ, folder=r"C:\PSCAD_work"))

prm = P.project_parameters(PRJ)
print("time_step", prm.get("time_step"), "sample_step", prm.get("sample_step"),
      "duration", prm.get("time_duration"), "PlotType", prm.get("PlotType"))

P.set_project_parameters(PRJ, {"time_step": 50.0, "time_duration": 3.0,
                               "sample_step": 200.0, "PlotType": "PSOUT"})
P.save(PRJ)
P.app().project(PRJ).clean()
P.app().project(PRJ).build()
errs = [x["text"] for x in P.messages(PRJ)["messages"] if x["status"].startswith("error")]
d = P.build_dimensions(PRJ).get("dimensions") or {}
print(f"build: errors={len(errs)} NODES={d.get('NODES')} BRANCHES={d.get('BRANCHES')}")
P.run(PRJ, wait=True, poll=1.0, timeout=1800)
psout = P.find_output_file(PRJ)
print("psout:", psout)

print(f"{'mm':>4}{'Vd t=0.19':>12}{'Vd t=0.49':>12}{'Vd t=2.9':>12}")
for n in range(1, 11):
    a = P.trace_window(psout, f"Root/Main/multimeter[{n}]/4/Vd", 0.18, 0.20)
    b = P.trace_window(psout, f"Root/Main/multimeter[{n}]/4/Vd", 0.48, 0.50)
    c = P.trace_window(psout, f"Root/Main/multimeter[{n}]/4/Vd", 2.85, 2.99)
    print(f"{n:>4}{a.get('mean', float('nan')):>12.4f}{b.get('mean', float('nan')):>12.4f}"
          f"{c.get('mean', float('nan')):>12.4f}")
