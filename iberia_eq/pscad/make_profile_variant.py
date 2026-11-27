r"""Make a run-speed profiling variant of a v2 case (S30 sec 23). Timing only: the variants are NOT valid models.

usage: python iberia_eq\pscad\make_profile_variant.py --src C:\PSCAD_work\smk_e --dst C:\PSCAD_work\prf_i --freeze-loads
       python iberia_eq\pscad\make_profile_variant.py --src ... --dst ... --disable v2:RES_Plant
  --freeze-loads     every v2:varrlc0 branch gets its constant start-up value X0 as R or L (no signal): the network
                     matrix no longer changes every time step. Measures the refactorisation cost of the
                     exponential / LFDD / rooftop-PV loads.
  --disable DEFN     sets disable="true" on every instance of DEFN on Main (e.g. v2:RES_Plant: the switching plants).
  --disable-pgb PFX  also disables the recorders (master:pgb) whose Name starts with PFX (T_: the plant trip
                     channels, which float once the plants are disabled).
  --tie0 PFX         adds a constant 0 source to every Main datalabel name starting with PFX (T_: the plant trip
                     signals read by the logic), placed right of the diagram.
Only the .pscx is copied (the case is rebuilt by run_v2.py).
"""
import argparse, os, re

ap = argparse.ArgumentParser(); ap.add_argument("--src", required=True); ap.add_argument("--dst", required=True)
ap.add_argument("--freeze-loads", action="store_true"); ap.add_argument("--disable", action="append", default=[]); ap.add_argument("--disable-pgb", action="append", default=[])
ap.add_argument("--tie0", action="append", default=[]); a = ap.parse_args()
t = open(os.path.join(a.src, "v2.pscx"), encoding="utf-8").read(); n = {}

def freeze(m):
    blk = m.group(0); x0 = re.search(r'<param name="X0" value="([^"]*)"', blk).group(1)
    rlc = re.search(r'<param name="RLC" value="([^"]*)"', blk).group(1)
    key = "R" if rlc == "0" else "L"
    n["frozen"] = n.get("frozen", 0) + 1
    return re.sub(rf'(<param name="{key}" value=")[^"]*(")', rf"\g<1>{x0}\g<2>", blk)
if a.freeze_loads:
    t = re.sub(r'<User [^>]*defn="v2:varrlc0".*?</User>', freeze, t, flags=re.S)
for d in a.disable:
    t, k = re.subn(rf'(<User [^>]*defn="{re.escape(d)}"[^>]*?)disable="false"', r'\1disable="true"', t); n[d] = k
def pgb_off(m):
    blk = m.group(0); nm = re.search(r'<param name="Name" value="([^"]*)"', blk)
    if nm and any(nm.group(1).startswith(p) for p in a.disable_pgb):
        n["pgb off"] = n.get("pgb off", 0) + 1; return blk.replace('disable="false"', 'disable="true"', 1)
    return blk
if a.disable_pgb:
    t = re.sub(r'<User [^>]*defn="master:pgb".*?</User>', pgb_off, t, flags=re.S)
if a.tie0:
    i0 = t.index('<Definition', t.index('name="Main"') - 400); s0 = t.index("<schematic", i0); s1 = t.index("</schematic>", s0)
    main = t[s0:s1]
    names = sorted({x for x in re.findall(r'defn="master:datalabel".*?<param name="Name" value="([^"]*)"', main, re.S)
                    if any(x.startswith(p) for p in a.tie0)})
    xmax = max(int(x) for x in re.findall(r'<User [^>]* x="(\d+)"', main)) + 360
    add = ""
    for k, nm in enumerate(names):
        y = 360 + 54 * k
        add += (f'<User classid="UserCmp" id="{1900000000 + 2 * k}" name="master:const" x="{xmax}" y="{y}" w="76" h="22" z="-1" orient="0" defn="master:const" link="-1" disable="false"><paramlist name="" link="-1" crc="0"><param name="Name" value="" /><param name="Value" value="0.0" /><param name="Dim" value="1" /></paramlist></User>'
                f'<User classid="UserCmp" id="{1900000001 + 2 * k}" name="master:datalabel" x="{xmax + 36}" y="{y}" w="34" h="23" z="-1" orient="0" defn="master:datalabel" link="-1" disable="false"><paramlist name="" link="-1" crc="0"><param name="Name" value="{nm}" /></paramlist></User>')
    t = t[:s1] + add + t[s1:]; n["tied to 0"] = len(names)
os.makedirs(a.dst, exist_ok=True)
open(os.path.join(a.dst, "v2.pscx"), "w", encoding="utf-8").write(t)
print(f"{a.dst}: {n}")
