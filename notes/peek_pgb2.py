import re
s = open(r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx', encoding='utf-8', errors='replace').read()
for i in [12384650, 12393571, 21024707, 22473925, 22832269]:
    print('=====', i)
    print(s[max(0, i - 500):i + 300].replace('\n', ' | ')[:900])
