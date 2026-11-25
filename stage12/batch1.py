r"""S27 Batch 1 (PLAN v1.2 §1c.3): eight event runs in parallel from ONE settled snapshot.

usage: python stage12/batch1.py <case.pscx> <snapshot.snp> <T0 = snapshot time> <settled psout> <w0,w1> [--go]
Writes C:\PSCAD_work\s27b1\<run>\ (make_variant) and, with --go, launches run_instance.py on each, 25 s apart.
Every event starts at T0 + 1 s, so the first second of each run is the S5 pre-event proof.
"""
import json, os, subprocess, sys, time

case, snap, T0, ps, win = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4], sys.argv[5]
go = "--go" in sys.argv
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = r"C:\PSCAD_work\s27b1"
E = T0 + 1.0
HVDC = "247853765"
OV = [(1.089, 1.5), (1.10, 0.0), (1.10, 0.5), (1.111, 0.1), (1.139, 0.2), (1.15, 0.6)]   # document order k -> (k-1)%6
proj = lambda d: {"time_duration": str(d), "sample_step": "500", "SnapType": "0",
                  "startup_filename": os.path.basename(snap)}
caseB = {"ov_report": True, "plants": {"18": {"Tforce": E}}, "ids": {HVDC: {"Qmax": 0.0, "Qmin": 0.0}},
         "project": proj(25)}
runs = {
    "r1_wp82_twounit": {"breakers": {"31": E, "32": E + 0.5}, "project": proj(8)},
    "r2_wp84_robust": {"plants": {"5": {"Tforce": E}, "6": {"Tforce": E}}, "project": proj(6)},
    "r3_wp76_granada": {"plants": {"18": {"Tforce": E}}, "project": proj(6)},
    "r4_caseB": caseB,
    "r6_caseB_P7_H120": {**caseB, "units": {b: {"H": 3.0} for b in ("30", "31", "32", "37")}},
    "r7_caseB_P6_hvdcQ": {**caseB, "ids": {HVDC: {"Qmax": 0.4, "Qmin": -0.6}}},
}
# P5: OV protection compliant with 1.10 pu / 60 min -> no setting at or below 1.10 pu (raised to 1.111 pu,
# the next observed setting, delay kept). Applied per plant in document order, as ov_report does.
p5 = dict(caseB); p5.pop("ov_report")
import xml.etree.ElementTree as ET
M = [d for d in ET.parse(case).getroot().iter("Definition") if d.get("name") == "Main"][0].find("schematic")
doc_ids = [c.get("id") for c in M if (c.get("defn") or "").endswith(":RES_Plant")]
p5["ids"] = {**caseB["ids"], **{i: {"Vt1": max(OV[k % 6][0], 1.111), "Tt1": OV[k % 6][1]} for k, i in enumerate(doc_ids)}}
runs["r5_caseB_P5_ov111"] = p5
# Case A from the measured plant MW of the settled window
spA = os.path.join(BASE, "caseA_spec.json"); os.makedirs(BASE, exist_ok=True)
subprocess.run([sys.executable, os.path.join(HERE, "caseA_spec.py"), str(T0), spA, win, ps], check=True)
sA = json.load(open(spA)); sA["project"]["startup_filename"] = os.path.basename(snap)
runs["r8_caseA"] = sA

# P1 (WP11): RES voltage control. Qmode 1 is IQREF = 2*(Vset - VDF); with Vset = VDF0 + Kpf*ID0/2 the plant's
# pre-event q-current equals the fixed-PF one (IQREF = Kpf*IDREF), so the switch at the snapshot is bumpless.
import mhi.psout, numpy as np
KPF = -0.1751820703
w0, w1 = (float(x) for x in win.split(","))
rr = mhi.psout.File(ps).run(0)
tt = np.asarray(rr.call("Root/Main/RES_Plant[1]/VDF/0/1", sep="/").domain.data); mw = (tt >= w0) & (tt <= w1)
p1pl = {}
for k in range(1, 19):
    vdf = float(np.asarray(rr.call(f"Root/Main/RES_Plant[{k}]/VDF/0/1", sep="/").data)[mw].mean())
    idm = float(np.asarray(rr.call(f"Root/Main/RES_Plant[{k}]/ID/0/1", sep="/").data)[mw].mean())
    p1pl[str(k)] = {"Qmode": 1, "Vset": round(vdf + KPF * idm / 2.0, 5)}
p1pl["18"]["Tforce"] = E
runs["r9_caseB_P1_qv"] = {**caseB, "plants": p1pl}
print("P1 Vset:", {k: v["Vset"] for k, v in p1pl.items()})

for name, spec in runs.items():
    d = os.path.join(BASE, name); os.makedirs(d, exist_ok=True)
    js = os.path.join(d, "spec_in.json"); json.dump(spec, open(js, "w"), indent=1)
    subprocess.run([sys.executable, os.path.join(HERE, "make_variant.py"), case, d, js], check=True)
if go:
    MAXPAR = int(os.environ.get("MAXPAR", "6"))   # licence 8; measured S27: per-run speed falls ~proportionally beyond 4-5
    order = sorted(runs, key=lambda n: float(runs[n]["project"]["time_duration"]))   # short runs first
    for name in order:
        while sum(1 for l in subprocess.run("tasklist", capture_output=True, text=True).stdout.splitlines()
                  if l.lower().startswith("ib6.exe")) >= MAXPAR:
            time.sleep(30)
        d = os.path.join(BASE, name)
        subprocess.Popen([sys.executable, os.path.join(HERE, "run_instance.py"), d, "--snap", snap],
                         stdout=open(os.path.join(d, "stdout.txt"), "w"), stderr=subprocess.STDOUT)
        print("launched", name); time.sleep(25)
