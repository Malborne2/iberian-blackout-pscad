r"""S27 Batch F0 (event fidelity): how much does the collector / 400 kV voltage rise after each forced initiator, as a
function of the frozen pre-event reactive balance? Relays parked (case default 1.5 pu), so the runs measure the
network's voltage sensitivity only; any relay filter is then evaluated offline with relay_emul.py (valid to the first
trip). Plus two cold settles with load absorption placed AWAY from the RES buses (Batch 2b spread it by PO, which put
~0.65 Gvar on bus 20 and pulled the Badajoz collectors down faster than the load buses).

  f_c1..f_c4 : Case B2 parked from the Batch 2b snapshots (ib6g_07.snp, t 28 s): Q 4 / 6 / 8 Gvar, and 6 Gvar + KA 10
  d1_Q5x     : cold settle, 5 Gvar on the 15 load buses not next to a RES collector (not 20/23/29), NQ 2, KA 40
  d2_Q5x_KA10: same + KA 10 on units 30/31/32/37
usage: python stage12/batch_f0.py [--go]
"""
import json, os, subprocess, sys, time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__)); BASE = r"C:\PSCAD_work\s29f"; SRC = r"C:\PSCAD_work\s29b"
T0 = 28.0; E = T0 + 1.0
tm = lambda t: E + 3.0 + (t - 76.443)
HVDC = "247853765"
force = {"18": {"Tforce": E}, "5": {"Tforce": round(tm(76.443), 3)}, "6": {"Tforce": round(tm(76.820), 3)}}
B2P = {"ov_report": False, "plants": force, "ids": {HVDC: {"Qmax": 0.0, "Qmin": 0.0}},
       "project": {"time_duration": "10", "sample_step": "500", "SnapType": "0", "startup_filename": "ib6g_07.snp"}}

CASE = r"C:\PSCAD_work\s29\ib6.pscx"
LOADB = {"744210529": 3, "1004648478": 7, "1522722771": 8, "1862156076": 12, "914258219": 15, "1925407754": 16,
         "1087233095": 18, "2071274910": 20, "775660433": 21, "553408281": 23, "1468690411": 24, "1275297413": 25,
         "979306711": 26, "768585174": 27, "2117866167": 28, "427020063": 29, "1446795315": 31, "2035760321": 4}
RESADJ = {20, 23, 29}
M = [d for d in ET.parse(CASE).getroot().iter("Definition") if d.get("name") == "Main"][0].find("schematic")
PO = {c.get("id"): float(next(p.get("value") for p in c.find("paramlist") if p.get("name") == "PO"))
      for c in M if c.get("id") in LOADB and LOADB[c.get("id")] not in RESADJ}
assert len(PO) == 15
def loads(gvar):
    s = sum(PO.values()); return {i: {"QO": round(gvar * 1000 / 3 * po / s, 4), "NQ": 2} for i, po in PO.items()}

ev = {f"f_{c}": c for c in ("c1_Q4", "c2_Q6", "c3_Q8", "c4_Q6_KA10")}
cold = {"d1_Q5x": {"ids": loads(5)},
        "d2_Q5x_KA10": {"ids": loads(5), "units": {b: {"KA": 10} for b in ("30", "31", "32", "37")}}}
for name, c in ev.items():
    d = os.path.join(BASE, name); os.makedirs(d, exist_ok=True)
    json.dump(B2P, open(os.path.join(d, "spec_in.json"), "w"), indent=1)
    subprocess.run([sys.executable, os.path.join(HERE, "make_variant.py"), os.path.join(SRC, c, "ib6.pscx"), d,
                    os.path.join(d, "spec_in.json")], check=True)
for name, spec in cold.items():
    d = os.path.join(BASE, name); os.makedirs(d, exist_ok=True)
    spec["project"] = {"time_duration": "28", "snapshot_filename": "ib6g.snp"}
    json.dump(spec, open(os.path.join(d, "spec_in.json"), "w"), indent=1)
    subprocess.run([sys.executable, os.path.join(HERE, "make_variant.py"), CASE, d, os.path.join(d, "spec_in.json")], check=True)
if "--go" in sys.argv:
    env = {k: v for k, v in os.environ.items() if k != "NoDefaultCurrentDirectoryInExePath"}
    for name, c in ev.items():
        d = os.path.join(BASE, name)
        subprocess.Popen([sys.executable, os.path.join(HERE, "run_instance.py"), d, "--snap", os.path.join(SRC, c, "snaps", "ib6g_07.snp")],
                         stdout=open(os.path.join(d, "stdout.txt"), "w"), stderr=subprocess.STDOUT, env=env)
        print("launched", name, flush=True); time.sleep(30)
    for name in cold:
        d = os.path.join(BASE, name)
        subprocess.Popen([sys.executable, os.path.join(HERE, "run_instance.py"), d, "--set", "StartType=0"],
                         stdout=open(os.path.join(d, "stdout.txt"), "w"), stderr=subprocess.STDOUT, env=env)
        print("launched", name, flush=True); time.sleep(40)
