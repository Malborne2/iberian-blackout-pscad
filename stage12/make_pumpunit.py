"""v2: PumpUnit = ib6 SyncUnit + input port PLD (pu of Sbase) added to the turbine/pump torque sum, and the
held-power term PMH removed: PMT = TRIM + PTRT, TRIM = Pmec * ramp (from the 5 s release), PTRT = PTRP + PLD.
Used for pumps in pumping mode: Pmec < 0 (pump load), PLD > 0 drops stages of pump load (driven by external
under-frequency stage logic). Everything else (machine, AVR, governor) is identical to SyncUnit.
usage: python stage12/make_pumpunit.py <source pscx with SyncUnit> <target pscx> <target project name>
The target project must exist and be unloaded (P12)."""
import sys, copy, random, xml.etree.ElementTree as ET
src, dst, pname = sys.argv[1:4]
D0 = [d for d in ET.parse(src).getroot().iter("Definition") if d.get("name") == "SyncUnit"][0]
T = ET.parse(dst); R = T.getroot()
parent = next(p for p in R.iter() if any(c.tag == "Definition" for c in p))
for d in list(parent):
    if d.tag == "Definition" and d.get("name") == "PumpUnit": parent.remove(d)
D = copy.deepcopy(D0); D.set("name", "PumpUnit"); D.set("id", str(random.randint(1300000000, 1399999999)))
S = D.find("schematic")
used = {int(e.get("id")) for e in R.iter() if (e.get("id") or "").isdigit()} | {int(e.get("id")) for e in D.iter() if (e.get("id") or "").isdigit()}
def nid():
    while True:
        k = random.randint(1400000000, 1499999999)
        if k not in used: used.add(k); return str(k)
for e in S.iter("User"):                                   # unique ids inside the copied definition
    if (e.get("id") or "").isdigit(): e.set("id", nid())
# torque sum PMT (grid 30,86): inputs B = PTRP->PTRT (top), D = PMH (left), F = TRIM (bottom).
# PumpUnit: D disabled -> PMT = PTRT + TRIM, i.e. Pmec is the FULL pump power (pu of Sbase, < 0 when pumping),
# ramped in from the release at 5 s by the module's upramp; no held-power (PMH) term (bench lt6, RUNLOG S27 sec 28).
tsum = [e for e in S if e.get("defn") == "master:sumjct" and e.get("x") == "540" and e.get("y") == "1548"][0]
next(p for p in tsum.iter("param") if p.get("name") == "D").set("value", "0")
lab = [e for e in S if e.get("defn") == "master:datalabel" and e.get("x") == "540" and e.get("y") == "1512"][0]
next(p for p in lab.iter("param") if p.get("name") == "Name").set("value", "PTRT")
tmpl_lab = lab; tmpl_sum = [e for e in S if e.get("defn") == "master:sumjct" and e.get("x") == "540" and e.get("y") == "1548"][0]
tmpl_imp = [e for e in S if e.get("defn") == "master:import"][0]
def place(t, x, y, **pv):
    e = copy.deepcopy(t); e.set("id", nid()); e.set("x", str(x)); e.set("y", str(y))
    for p in e.iter("param"):
        if p.get("name") in pv: p.set("value", str(pv[p.get("name")]))
    S.append(e); return e
place(tmpl_sum, 720, 1980, A=0, B=0, C=0, D=1, E=0, F=1, G=0)   # grid (40,110): IND (38,110) INF (40,112) OUT (42,110)
place(tmpl_lab, 684, 1980, Name="PTRP"); place(tmpl_lab, 756, 1980, Name="PTRT")
place(tmpl_imp, 684, 2016, Name="PLD")                          # import output port = +2 grid -> (720,2016) = INF
G = D.find("graphics"); pT = G.find("Port"); pP = copy.deepcopy(pT); pP.set("id", nid()); pP.set("x", "0"); pP.set("y", "36")
for p in pP.iter("param"):
    v = {"name": "PLD", "mode": "1", "datatype": "3", "electype": "0", "dim": "1"}.get(p.get("name"))
    if v is not None: p.set("value", v)
G.insert(list(G).index(pT) + 1, pP)
parent.append(D); T.write(dst, encoding="utf-8")
print("PumpUnit written to", dst, "id", D.get("id"))
