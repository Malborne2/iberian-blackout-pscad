r"""Module instance -> unit mapping read from the generated Main.f of a build (S30 sec 21, lesson 3).

usage (module): from map_instances import instance_map
                M = instance_map(r"C:\PSCAD_work\rp_cascade\v2.gf81_x86")  ->  {"RES_Plant(3)": {...}, "SyncUnit(10)": {...}, ...}
usage (cli):    python iberia_eq\pscad\map_instances.py <gf81 build folder> [--log build_v2sld_r.out]

PSCAD numbers module instances in the order of their DSDYN calls in Main.f (verified against the load-flow matching of
SyncUnit(10) = E3 embedded CAT in rp_cascade). Each call carries the instance's literal parameters:
  RES_PlantDyn(PR<k>, FRC, ..., Sbase, ...)   PR<k> = plant k of build_v2's RESP list (1-based)
  SyncUnitDyn(Sbase, Vbase, VbaseLN, Ibase, H, P0, Q0, ...)
  PumpUnitDyn(PLD, Sbase, Vbase, VbaseLN, Ibase, H, P0, Q0, ...)
Units are named with the build log (lines "unit <name> at <bus> P .. S .." and "RES <name> at <bus> <mw> MW S <S>").
"""
import os, re, sys


def _calls(main_f, name):
    txt = open(main_f, encoding="utf-8", errors="replace").read().replace("&\n     &", "")
    return [re.split(r"\s*,\s*", m.group(1)) for m in re.finditer(rf"CALL {name}Dyn\(([^)]*)\)", txt)]


def instance_map(build, log=None):
    main_f = os.path.join(build, "Main.f"); M = {}
    units, res = [], []
    if log:
        for ln in open(log, encoding="utf-8", errors="replace"):
            s = ln.strip()
            m = re.match(r"unit (.+?)\s+at (\S+(?: term)?)\s+P\s+(-?[\d.]+) Q\s+([-+\d.]+) S\s+([\d.]+)", s)
            if m: units.append(dict(name=m.group(1).strip(), bus=m.group(2), P=float(m.group(3)), S=float(m.group(5))))
            m = re.match(r"RES (\S+)\s+at (\S+)\s+([\d.]+) MW\s+S\s+([\d.]+)", s)
            if m: res.append(dict(name=m.group(1), bus=m.group(2), mw=float(m.group(3)), S=float(m.group(4))))
    for k, a in enumerate(_calls(main_f, "RES_Plant")):
        pk = int(re.sub(r"\D", "", a[0])); d = dict(Sbase=float(a[3]), PR=pk)
        if res: d.update(res[pk - 1])
        M[f"RES_Plant({k})"] = d
    for k, a in enumerate(_calls(main_f, "SyncUnit")):
        d = dict(Sbase=float(a[0]), P0=float(a[5]))
        cand = [u for u in units if abs(u["S"] - d["Sbase"]) < 1.0 and abs(u["P"] - d["P0"]) < 1.0]
        if len(cand) == 1: d.update(cand[0])
        elif cand: d.update(name="/".join(u["name"] for u in cand), bus=cand[0]["bus"])
        M[f"SyncUnit({k})"] = d
    for k, a in enumerate(_calls(main_f, "PumpUnit")):
        M[f"PumpUnit({k})"] = dict(Sbase=float(a[1]), P0=float(a[6]))
    return M


if __name__ == "__main__":
    log = sys.argv[sys.argv.index("--log") + 1] if "--log" in sys.argv else None
    for k, v in instance_map(sys.argv[1], log).items(): print(k, v)
