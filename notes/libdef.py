"""Search master.pslx for a component name and print surroundings."""
import sys

path = r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx'
s = open(path, encoding='utf-8', errors='replace').read()
name = sys.argv[1] if len(sys.argv) > 1 else 'xfmr-3p2w'
span = int(sys.argv[2]) if len(sys.argv) > 2 else 1200
hits = []
start = 0
while True:
    i = s.find(name, start)
    if i < 0:
        break
    hits.append(i)
    start = i + 1
print('hits', len(hits), hits[:20])
for i in hits[:3]:
    print('=' * 30, i)
    print(s[max(0, i - span): i + span])
