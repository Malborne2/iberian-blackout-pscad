r"""S27 Batch 1b: Case B2 = the report's three initiators forced, everything after them from the relays.

Why (r4, measured): Case B with Granada alone does not cascade. Every plant keeps >= 0.020 pu margin to its report OV
setting (held-for-delay peak), and the collectors return to their pre-event value within 2 s. The report itself has
no trip between event 3 (57.22 s) and event 4a (76.443 s): Fig 3-7a shows the 400 kV maximum drifting 421.8 -> 427.8
kV (1.07 pu, below every observed fleet setting at the POI) with cumulative loss flat at 891 MW. So events 4a (582 MW)
and 4b (145 MW) are initiators, not OV outcomes at the 400 kV level, and they are forced here at the Case A clock.
From event 5a on (12:33:17.37) the report's trips are the OV cascade: those must come from the relays (C6).

usage: python stage12/batch1b.py <case.pscx> <snapshot.snp> <T0> <settled psout> <w0,w1> [--go]
Plants by PSOUT index (make_variant maps to document order): Granada 18 (489 MW; report 355), event 4a (582 MW) ->
plant 5 (580 MW), event 4b (145 MW) -> plant 6 (145 MW), both bus 34 as Badajoz substations 1 and 2 share one area.
(The Case A greedy map 12 + 3 gives 948 MW for 727 - a 30 % larger initiator; rejected.)
"""
import json, os, subprocess, sys, time
import xml.etree.ElementTree as ET
import mhi.psout, numpy as np

case, snap, T0, ps, win = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4], sys.argv[5]
go = "--go" in sys.argv
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = r"C:\PSCAD_work\s27b1b"
E = T0 + 1.0
tm = lambda t: E + 3.0 + (t - 76.443)          # Case A clock from event 4a on (k = 1)
HVDC = "247853765"
OV = [(1.089, 1.5), (1.10, 0.0), (1.10, 0.5), (1.111, 0.1), (1.139, 0.2), (1.15, 0.6)]
DUR = 10
proj = {"time_duration": str(DUR), "sample_step": "500", "SnapType": "0", "startup_filename": os.path.basename(snap)}
force = {"18": {"Tforce": E}, "5": {"Tforce": round(tm(76.443), 3)}, "6": {"Tforce": round(tm(76.820), 3)}}
B2 = {"ov_report": True, "plants": force, "ids": {HVDC: {"Qmax": 0.0, "Qmin": 0.0}}, "project": proj}

M = [d for d in ET.parse(case).getroot().iter("Definition") if d.get("name") == "Main"][0].find("schematic")
doc_ids = [c.get("id") for c in M if (c.get("defn") or "").endswith(":RES_Plant")]
p5 = {k: v for k, v in B2.items() if k != "ov_report"}
p5["ids"] = {**B2["ids"], **{i: {"Vt1": max(OV[k % 6][0], 1.111), "Tt1": OV[k % 6][1]} for k, i in enumerate(doc_ids)}}

KPF = -0.1751820703
w0, w1 = (float(x) for x in win.split(","))
rr = mhi.psout.File(ps).run(0)
tt = np.asarray(rr.call("Root/Main/RES_Plant[1]/VDF/0/1", sep="/").domain.data); mw = (tt >= w0) & (tt <= w1)
p1 = {}
for k in range(1, 19):
    vdf = float(np.asarray(rr.call(f"Root/Main/RES_Plant[{k}]/VDF/0/1", sep="/").data)[mw].mean())
    idm = float(np.asarray(rr.call(f"Root/Main/RES_Plant[{k}]/ID/0/1", sep="/").data)[mw].mean())
    p1[str(k)] = {"Qmode": 1, "Vset": round(vdf + KPF * idm / 2.0, 5), **force.get(str(k), {})}

runs = {
    "b1_B2": B2,
    "b2_B2_P5_ov111": p5,
    "b3_B2_P6_hvdcQ": {**B2, "ids": {HVDC: {"Qmax": 0.4, "Qmin": -0.6}}},
    "b4_B2_P1_qv": {**B2, "plants": p1},
    "b5_B2_parked": {**B2, "ov_report": False},    # C6 control: same forced trips, relays parked (case default 1.5 pu)
}
print("forced:", force, "| P1 Vset:", {k: v["Vset"] for k, v in p1.items()})
for name, spec in runs.items():
    d = os.path.join(BASE, name); os.makedirs(d, exist_ok=True)
    js = os.path.join(d, "spec_in.json"); json.dump(spec, open(js, "w"), indent=1)
    subprocess.run([sys.executable, os.path.join(HERE, "make_variant.py"), case, d, js], check=True)
if go:
    for name in runs:
        d = os.path.join(BASE, name)
        subprocess.Popen([sys.executable, os.path.join(HERE, "run_instance.py"), d, "--snap", snap],
                         stdout=open(os.path.join(d, "stdout.txt"), "w"), stderr=subprocess.STDOUT)
        print("launched", name); time.sleep(25)
