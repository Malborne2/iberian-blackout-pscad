import re
s = open(r'C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model\Spanish_grid_model.pscx', encoding='utf-8').read()
i = s.find('"Settings"')
print(s[max(0, i - 200):i + 1500])
