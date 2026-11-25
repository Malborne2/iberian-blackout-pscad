"""Compare the canvas 'size' parameter between this project and PSCAD's examples."""
import re, glob, os

pat = re.compile(r'<schematic classid="(UserCanvas|RowCanvas)">\s*<paramlist>\s*'
                 r'<param name="show_grid" value="(\d+)" />\s*'
                 r'<param name="size" value="(\d+)" />')

files = [r'C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD'
         r'\Spanish_netowrk_model\Spanish_grid_model.pscx']
files += glob.glob(r'C:\Users\Public\Documents\PSCAD\5.1.0\Examples\**\*.pscx', recursive=True)

for p in files:
    try:
        s = open(p, encoding='utf-8', errors='replace').read()
    except Exception:
        continue
    m = pat.search(s)
    if m:
        print('%-6s size=%-2s %s' % (m.group(1), m.group(3), os.path.basename(p)))
