r"""Disable recorded channels no analysis uses (S30 sec 23, run-speed optimisation). Project must not be loaded.

usage: python iberia_eq\pscad\trim_channels.py --pscx <v2.pscx> [--restore]
Sets enab = 0 on the module pgbs listed in OFF (about 300 of ~700 channels in the replay case); --restore sets them back
to 1. Kept: everything read by read_v2 / plot_v2 / diag_release / fidelity_v2 / run_v2 health (VD, ID, IQ, VDF of the
RES plants; Wspd, POUT, QOUT, VIT, TMECH, EFD0ch, DPGOV, DVR, QERR of the machines; all Main channels).
"""
import argparse
import xml.etree.ElementTree as ET

OFF = {"RES_Plant": {"VbrA", "VbrB", "VbrC", "IsrcA", "VQ", "THETA_TR", "STGSH", "VA_PU", "IA_PU", "TRIP"},
       "SyncUnit": {"ExInit", "VREFO", "THETA"},
       "PumpUnit": {"ExInit", "VREFO", "THETA", "EFD0ch", "DPGOV"}}
ap = argparse.ArgumentParser(); ap.add_argument("--pscx", required=True); ap.add_argument("--restore", action="store_true"); a = ap.parse_args()
tree = ET.parse(a.pscx); root = tree.getroot(); n = 0
for dn, names in OFF.items():
    d = [x for x in root.iter("Definition") if x.get("name") == dn]
    if not d: continue
    for u in d[0].find("schematic"):
        if u.get("defn") != "master:pgb": continue
        P = {p.get("name"): p for p in u.iter("param")}
        if P.get("Name") is not None and P["Name"].get("value") in names:
            P["enab"].set("value", "1" if a.restore else "0"); n += 1
open(a.pscx, "w", encoding="utf-8").write(ET.tostring(root, encoding="unicode"))
print(f"{'restored' if a.restore else 'disabled'} {n} module channel blocks ({sum(len(v) for v in OFF.values())} names) in {a.pscx}")
