r"""S27 Batch 2b: cold settles for the FROZEN pre-event items (event fidelity first; prevention later).

Measured on the s28 settle (28 s): Iberian load buses 1.14-1.165 pu (report: every 400 kV bus 400-420 kV), units
32/37/30 absorb 2.2-2.7 Gvar each on KA 40 voltage control (report: conventional units in the south ~74 Mvar),
all loads QO = 0. Load PO/QO and AVR gains are set in *_Begin and restored from a snapshot (stage12/snap_live.py),
so every one of these needs a cold settle. Five in parallel, from the s29 case (s28 + relay filter `Trel`):
  c1 Q4  : 4 Gvar total load absorption at 1 pu (constant impedance, NQ 2), shared by PO over the 18 Iberian loads
  c2 Q6  : 6 Gvar
  c3 Q8  : 8 Gvar
  c4 Q6 + KA 10 on the four Iberian units (weaker voltage control: the report's units absorbed little)
  c5 Q6 at 10 us (the 17 Hz numerical mode falls 5x at 10 us, D26-1): checks whether event dynamics depend on dt
28 s each, snapshots every 4 s. Pmec/dispatch is LIVE -> trimmed warm afterwards.
usage: python stage12/batch2b.py [--go]
"""
import json, os, subprocess, sys, time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__)); CASE = r"C:\PSCAD_work\s29\ib6.pscx"; BASE = r"C:\PSCAD_work\s29b"
LOADB = {"744210529": 3, "1004648478": 7, "1522722771": 8, "1862156076": 12, "914258219": 15, "1925407754": 16,
         "1087233095": 18, "2071274910": 20, "775660433": 21, "553408281": 23, "1468690411": 24, "1275297413": 25,
         "979306711": 26, "768585174": 27, "2117866167": 28, "427020063": 29, "1446795315": 31, "2035760321": 4}
M = [d for d in ET.parse(CASE).getroot().iter("Definition") if d.get("name") == "Main"][0].find("schematic")
PO = {c.get("id"): float(next(p.get("value") for p in c.find("paramlist") if p.get("name") == "PO")) for c in M if c.get("id") in LOADB}
assert len(PO) == 18
def loads(gvar):    # QO is per phase, MVar
    s = sum(PO.values()); return {i: {"QO": round(gvar * 1000 / 3 * po / s, 4), "NQ": 2} for i, po in PO.items()}
UNITS = ("30", "31", "32", "37")
runs = {
    "c1_Q4": ({"ids": loads(4)}, ""),
    "c2_Q6": ({"ids": loads(6)}, ""),
    "c3_Q8": ({"ids": loads(8)}, ""),
    "c4_Q6_KA10": ({"ids": loads(6), "units": {b: {"KA": 10} for b in UNITS}}, ""),
    "c5_Q6_dt10": ({"ids": loads(6)}, ",time_step=10"),
}
for name, (spec, extra) in runs.items():
    d = os.path.join(BASE, name); os.makedirs(d, exist_ok=True)
    spec["project"] = {"time_duration": "28", "snapshot_filename": "ib6g.snp"}
    json.dump(spec, open(os.path.join(d, "spec_in.json"), "w"), indent=1)
    subprocess.run([sys.executable, os.path.join(HERE, "make_variant.py"), CASE, d, os.path.join(d, "spec_in.json")], check=True)
if "--go" in sys.argv:
    env = {k: v for k, v in os.environ.items() if k != "NoDefaultCurrentDirectoryInExePath"}
    for name, (spec, extra) in runs.items():
        d = os.path.join(BASE, name)
        subprocess.Popen([sys.executable, os.path.join(HERE, "run_instance.py"), d, "--set", "StartType=0" + extra],
                         stdout=open(os.path.join(d, "stdout.txt"), "w"), stderr=subprocess.STDOUT, env=env)
        print("launched", name); time.sleep(40)
