"""Phase 1: rebase the IEEE-39 model to the Spanish system.

  * 60 Hz -> 50 Hz
  * 230 kV -> 400 kV
  * power scale k = 4.0979 (total load 6.149 GW -> 25.2 GW)
  * impedances rescaled so the per-unit network is preserved
All edits are made directly in the .pscx XML (fast, repeatable).
"""
import os, sys, time
import xml.etree.ElementTree as ET

def log(*a): print(time.strftime("%H:%M:%S"), *a, flush=True)

BASE = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model"
PSCX = os.path.join(BASE, "Spanish_grid_model.pscx")

K = 4.0979            # power scale
VOLD, VNEW = 230.0, 400.0
R = VNEW / VOLD       # 1.7391
R2 = R * R            # 3.0246
ZSCALE = R2 / K       # ohm scaling for series impedances (0.7381)
FNEW = 50.0

SMVA = 100.0 * K      # new system MVA base = 409.79 MVA
VPH = VNEW / 3 ** 0.5

EDIT_ONLY = '--edit-only' in sys.argv


def num(s):
    return float(str(s).split()[0])


def with_unit(old, newval):
    parts = str(old).split()
    if len(parts) >= 2 and parts[1].startswith('['):
        return f"{newval:g} {parts[1]}"
    return f"{newval:g}"


def setp(pl, name, fn):
    for pp in pl:
        if pp.get('name') == name:
            old = pp.get('value')
            new = fn(old)
            pp.set('value', new)
            return old, new
    return None, None


def edit(path):
    tree = ET.parse(path)
    root = tree.getroot()
    root.set('name', 'Spanish_grid_model')
    out = root.find('output')
    if out is not None:
        out.set('name', 'Spanish_grid_model')

    # --- project settings ---
    settings = root.find("paramlist[@name='Settings']")
    for pp in settings:
        if pp.get('name') == 'time_duration':
            pp.set('value', '2')
        if pp.get('name') == 'sample_step':
            pp.set('value', '500')
        if pp.get('name') == 'PlotType':
            pp.set('value', '1')   # PSOUT
        if pp.get('name') == 'description':
            pp.set('value', 'Spain/Portugal 28 Apr 2025 blackout reconstruction (IEEE-39 backbone, 400 kV, 50 Hz)')

    defs = root.find('definitions')
    main = [d for d in defs if d.get('name') == 'Main'][0]
    sch = main.find('schematic')

    counts = {}
    for el in sch:
        cls = el.get('classid')
        if cls not in ('UserCmp', 'Bus'):
            continue
        d = el.get('defn') or 'bus'
        pl = el.find('paramlist')
        if pl is None:
            continue
        counts[d] = counts.get(d, 0) + 1

        if cls == 'Bus':
            setp(pl, 'BaseKV', lambda o: with_unit(o, VNEW))

        elif d == 'master:xfmr-3p2w':
            setp(pl, 'f', lambda o: with_unit(o, FNEW))
            setp(pl, 'V1', lambda o: with_unit(o, VNEW))
            setp(pl, 'V2', lambda o: with_unit(o, VNEW))
            setp(pl, 'Tmva', lambda o: with_unit(o, SMVA))

        elif d == 'master:source3':
            setp(pl, 'F', lambda o: with_unit(o, FNEW))
            setp(pl, 'F0', lambda o: with_unit(o, FNEW))
            setp(pl, 'Vm', lambda o: with_unit(o, VNEW))
            setp(pl, 'Vbase', lambda o: with_unit(o, VNEW))
            setp(pl, 'MVA', lambda o: with_unit(o, SMVA))
            setp(pl, 'Es', lambda o: with_unit(o, num(o) * R))
            setp(pl, 'Z1', lambda o: with_unit(o, num(o) * ZSCALE))
            setp(pl, 'R1s', lambda o: with_unit(o, num(o) * ZSCALE))
            setp(pl, 'R1p', lambda o: with_unit(o, num(o) * ZSCALE))
            setp(pl, 'R0s', lambda o: with_unit(o, num(o) * ZSCALE))
            setp(pl, 'R0p', lambda o: with_unit(o, num(o) * ZSCALE))
            setp(pl, 'L1p', lambda o: with_unit(o, num(o) * ZSCALE))
            setp(pl, 'L0p', lambda o: with_unit(o, num(o) * ZSCALE))
            setp(pl, 'L0s', lambda o: with_unit(o, num(o) * ZSCALE))

        elif d == 'master:fixed_load':
            setp(pl, 'PO', lambda o: with_unit(o, num(o) * K))
            setp(pl, 'QO', lambda o: with_unit(o, num(o) * K))
            setp(pl, 'VBO', lambda o: with_unit(o, VPH))
            setp(pl, 'FR', lambda o: with_unit(o, FNEW))

        elif d == 'master:capacitor':
            # keep Mvar the same in pu: C' = C * k * (Vold/Vnew)^2 * (fold/fnew)
            setp(pl, 'C', lambda o: with_unit(o, num(o) * K * (VOLD / VNEW) ** 2 * (60.0 / FNEW)))

        elif d == 'master:multimeter':
            setp(pl, 'S', lambda o: with_unit(o, SMVA))
            setp(pl, 'BaseV', lambda o: with_unit(o, VNEW))
            setp(pl, 'Freq', lambda o: with_unit(o, FNEW))

    # --- line models: keep the per-unit network, rebase VR/MVA ---
    nline = 0
    for d in defs:
        if not (d.get('name') or '').startswith('TLine_'):
            continue
        s = d.find('schematic')
        if s is None:
            continue
        for el in s:
            if el.get('defn') != 'master:Line_ManualYZ':
                continue
            pl = el.find('paramlist')
            setp(pl, 'VR', lambda o: with_unit(o, VNEW))
            setp(pl, 'VR2', lambda o: with_unit(o, VNEW))
            setp(pl, 'MVA', lambda o: with_unit(o, SMVA))
            setp(pl, 'MVA2', lambda o: with_unit(o, SMVA))
            nline += 1

    log("components:", counts)
    log("line models updated:", nline)
    tree.write(path, encoding='utf-8', xml_declaration=True)
    log("written", path)


if not EDIT_ONLY:
    import mhi.pscad as p
    app = p.connect()
    pr = app.project('Spanish_grid_model')
    log("save + unload")
    pr.save()
    pr.unload()
    time.sleep(2)

edit(PSCX)

if not EDIT_ONLY:
    log("reload")
    app.load(PSCX)
    time.sleep(3)
    pr = app.project('Spanish_grid_model')
    ps = pr.parameters()
    log("PlotType", ps['PlotType'], "T", ps['time_duration'], "sample", ps['sample_step'])
