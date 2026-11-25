import sys, time
import uiautomation as auto

auto.uiautomation.TIME_OUT_SECOND = 1.5
COLS = ('Type', 'Link', 'Component', 'Namespace', 'Description')


def get_table():
    pane = auto.ControlFromHandle(200048)
    for ctrl, depth in auto.WalkControl(pane, maxDepth=6):
        if ctrl.ControlTypeName == 'TableControl':
            return ctrl
    return None


def read_page(table):
    out = []
    for row in table.GetChildren():
        if not row.Name.startswith('Row '):
            continue
        cells = {}
        for cell in row.GetChildren():
            key = cell.Name.rsplit(' ', 1)[0]
            try:
                val = cell.GetValuePattern().Value
            except Exception:
                val = ''
            cells[key] = val
        out.append(cells)
    return out


def pagedown(table):
    sb = table.GetFirstChildControl()
    for c in sb.GetChildren():
        if c.Name == 'Page down':
            c.Click(simulateMove=False)
            return True
    return False


seen = []
for page in range(40):
    table = get_table()
    rows = read_page(table)
    new = 0
    for r in rows:
        key = tuple(r.get(k, '') for k in COLS)
        if key in seen:
            continue
        seen.append(key)
        new += 1
    print(f'--- page {page}: {len(rows)} rows, {new} new', flush=True)
    if new == 0 or not rows:
        break
    if not pagedown(table):
        break
    time.sleep(0.4)

print('==== TOTAL', len(seen))
for k in seen:
    print(' | '.join(x[:110] for x in k))
