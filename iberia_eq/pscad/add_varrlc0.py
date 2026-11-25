r"""Add the definition v2:varrlc0 to a v2 .pscx (S30 sec 9): master:varrlc with a start-up value X0.

usage: python iberia_eq\pscad\add_varrlc0.py --pscx C:\PSCAD_work\v2sld\v2.pscx   (project must not be loaded)

Why: the exponential-load signals (meter -> realpole -> x^y -> gain) are computed in DSOUT, after the network solution,
while varrlc reads its R/L in DSDYN. At t = 0 the signal storage is still 0, so every exponential load branch is a
zero-ohm short to ground. In parallel with the SyncUnit start-up sources this aborts EMTDC ("Short circuited or
parallel ideal voltage source ... SCTEST", run sld_health12). varrlc0 is the library varrlc copied unchanged except:
  - new Constant parameter X0 (the branch's load-flow R [ohm] or L [H]);
  - the R and L inputs are passed as MERGE(X0, R, R <= 0): X0 whenever the signal is not yet positive.
Same branches, same node count, no extra page.
"""
import argparse, copy
import xml.etree.ElementTree as ET

ap = argparse.ArgumentParser(); ap.add_argument("--pscx", required=True); a = ap.parse_args()
lib = ET.parse(r"C:\Program Files (x86)\PSCAD\5.1.0\master.pslx").getroot()
d = copy.deepcopy([x for x in lib.iter("Definition") if x.get("name") == "varrlc"][0])
d.set("name", "varrlc0"); d.set("id", "1200000901"); d.set("crc", "0"); d.set("group", "")
cat = d.find("form/category")
x0 = ET.fromstring('<parameter type="Real" name="X0" desc="Start-up value of R [ohm] or L [H] (used while the input &lt;= 0)" '
                   'content_type="Constant" min="0" max="1E+308" unit="" group="" helpmode="Append" animate="false">'
                   '<value>1.0</value><cond type="Enable">true</cond><help /></parameter>')
cat.append(x0)
n = 0
for seg in d.iter("segment"):
    if seg.get("name") == "Dsdyn":
        old = seg.text
        seg.text = old.replace("{~ $R, $E)} {~ $L, $E)}", "{~ MERGE($X0,$R,$R .LE. 0.0), $E)} {~ MERGE($X0,$L,$L .LE. 0.0), $E)}")
        n = old.count("{~ $R, $E)} {~ $L, $E)}")
assert n >= 3, f"Dsdyn CASE lines not found ({n})"
tree = ET.parse(a.pscx); root = tree.getroot(); defs = root.find("definitions")
for old in [x for x in defs if x.get("name") == "varrlc0"]: defs.remove(old)
defs.append(d)
open(a.pscx, "w", encoding="utf-8").write(ET.tostring(root, encoding="unicode"))
print(f"varrlc0 added to {a.pscx} ({n} CASE lines patched)")
