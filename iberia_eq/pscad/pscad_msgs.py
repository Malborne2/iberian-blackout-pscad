r"""Dump the build messages and the EMTDC run output of a running PSCAD instance (S30 error capture).

usage: python iberia_eq\pscad\pscad_msgs.py <port> [project]
Find the port with `netstat -ano | grep LISTEN` (127.0.0.1:<port> of the Pscad.exe pid).
Prints every message (status, component, text) and the tail of the run output; changes nothing.
"""
import sys
import mhi.pscad

port = int(sys.argv[1]); name = sys.argv[2] if len(sys.argv) > 2 else "v2"
p = mhi.pscad.connect(port=port)
print("projects:", [pr.get("name", pr) if isinstance(pr, dict) else pr for pr in p.projects()])
prj = p.project(name)
for m in prj.messages():
    print(f"[{getattr(m, 'status', '?')}] {getattr(m, 'scope', '')} {getattr(m, 'name', '')} "
          f"{getattr(m, 'component', '')} :: {getattr(m, 'text', m)}")
print("---- run output (tail) ----")
print((prj.output() or "")[-4000:])
