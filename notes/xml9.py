import re
s = open(r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx', encoding='utf-8', errors='replace').read()
for m in re.finditer('PlotType', s):
    i = m.start()
    print('=====', i)
    print(s[max(0, i - 250):i + 500])
