r"""S26: scan an EMTDC executable for its command-line option strings (to learn the snapshot-start switch).

usage: python stage12\exe_opts.py <exe>
"""
import re, sys

data = open(sys.argv[1], "rb").read()
found = set()
for m in re.finditer(rb"-([a-z][a-z0-9_]{1,14})\b", data):
    found.add(m.group(0).decode())
for s in sorted(found):
    print(s)
