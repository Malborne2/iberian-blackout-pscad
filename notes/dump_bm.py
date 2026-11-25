"""Dump all visible rows of the PSCAD Build Messages grid, paging with the scrollbar."""
import sys, time
import uiautomation as auto

auto.uiautomation.TIME_OUT_SECOND = 1.5

pane = auto.ControlFromHandle(200048)
table = None
for ctrl, depth in auto.WalkControl(pane, maxDepth=6):
    if ctrl.ControlTypeName == 'TableControl':
        table = ctrl
        break
if table is None:
    print('no table')
    sys.exit(1)

scroll = table.GetFirstChildControl()  # ScrollBarControl
pagedown = None
for c in scroll.GetChildren():
    if c.Name == 'Page down':
        pagedown = c

rows = []
seen = set()
COLS = ('Type', 'Link', 'Component', 'Namespace', 'Description')


def read_page():
    out = []
    for row in table.GetChildren():
        if not row.Name.startswith('Row '):
            continue
        cells = {}
        for cell in row.GetChildren():
            parts = cell.Name.rsplit(' ', 1)
            val = None
            try:
                val = cell.GetValuePattern().Value
            except Exception:
                val = None
            cells[parts[0]] = val if val else cell.Name
        if cells:
            out.append(cells)
    return out


for page in range(60):
    pg = read_page()
    new = 0
    for c in pg:
        key = tuple(c.get(k, '') for k in COLS)
        if key in seen:
            continue
        seen.add(key)
        rows.append(c)
        new += 1
    if new == 0:
        break
    if pagedown is None:
        break
    pagedown.Click(simulateMove=False)
    time.sleep(0.35)

print('TOTAL', len(rows))
for c in rows:
    print('|'.join(str(c.get(k, ''))[:100] for k in COLS))
