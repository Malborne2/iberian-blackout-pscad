r"""Which definition parameters can be changed for a run that starts from a snapshot? (static, from generated Fortran)

A snapshot stores the whole EMTDC storage (STORF/STORI ...) written by the *_Begin routines and by the states; on a
snapshot start that storage is restored. So a parameter that is only used in `<Def>Dyn_Begin` (component set-up:
machine data, load PO/QO, AVR reference ...) is FROZEN at its snapshot value; a parameter that the per-step body of
`<Def>Dyn` uses in its own code or passes to a per-step call is LIVE (takes effect from the snapshot).
Evidence: S27 r6 (H changed, run bit-identical) and the load PO literal found inside ib6f_07.snp.

usage: python stage12/snap_live.py <build folder> [Definition ...]   (default: SyncUnit RES_Plant)
Output per parameter: LIVE lines (first two uses) or FROZEN. "LIVE?" = passed to a master routine in the per-step
body whose own handling is not visible (check one such case by a 0.3 s smoke run before relying on it).
"""
import os, re, sys

fold = sys.argv[1]; defs = sys.argv[2:] or ["SyncUnit", "RES_Plant"]
for d in defs:
    src = re.sub(r"&\s*\n\s*&", "", open(os.path.join(fold, f"{d}.f"), encoding="latin-1").read())   # join continuation lines
    m = re.search(rf"SUBROUTINE {d}Dyn\((.*?)\)", src, flags=re.S)
    args = [a.strip() for a in re.sub(r"[&\n]", " ", m.group(1)).split(",")]
    body = src[m.end():src.find(f"SUBROUTINE {d}Dyn_Begin")]
    body = body[body.find("! Electrical Node Lookup") if "! Electrical Node Lookup" in body else 0:]
    lines = [l for l in body.split("\n") if not l.lstrip().startswith("!")]
    print(f"## {d}Dyn ({len(args)} args)")
    for a in args:
        use = [l.strip() for l in lines if re.search(rf"(?<![A-Za-z0-9_]){re.escape(a)}(?![A-Za-z0-9_])", l, flags=re.I)
               and not re.match(r"\s*(REAL|INTEGER|LOGICAL|CHARACTER|INCLUDE)", l, flags=re.I)
               and not re.match(r"\s*(STO[FI]\(IST\w+ *\+ *\d+\) *= *\w+|\w+ *= *STO[FI]\(IST\w+ *\+ *\d+\))\s*$", l, flags=re.I)]
        if not use:
            print(f"  {a:10s} FROZEN (only in {d}Dyn_Begin)")
        else:
            tag = "LIVE?" if all(re.match(r"\s*(&|CALL\s+(E_|COMPONENT|SMACH|EXCAC|LOAD|.*_EXE))", u, flags=re.I) for u in use) else "LIVE"
            print(f"  {a:10s} {tag:6s} {' | '.join(u[:90] for u in use[:2])}")
