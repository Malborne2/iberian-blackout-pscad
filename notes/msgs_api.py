"""Try every message-access API on the project and print what each returns."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

app, pr = ptools.ensure_loaded()
for name in ('list_messages', 'messages'):
    try:
        f = getattr(pr, name)
        v = f()
        print('===', name, type(v), len(v) if hasattr(v, '__len__') else '')
        if hasattr(v, '__iter__') and not isinstance(v, str):
            for m in list(v)[:40]:
                print('   ', m)
    except Exception as e:
        print('===', name, 'ERR', type(e).__name__, e)
