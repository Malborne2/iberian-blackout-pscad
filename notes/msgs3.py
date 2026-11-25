"""Print every build message of a given status (default error) verbatim."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

stat = sys.argv[1] if len(sys.argv) > 1 else 'err'
app, pr = ptools.ensure_loaded()
for m in pr.messages():
    if str(m.status).lower().startswith(stat):
        print('[%s] name=%s link=%s\n   %s' % (m.status, m.name, m.link, m.text))
