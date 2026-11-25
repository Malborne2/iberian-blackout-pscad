import uiautomation as auto
auto.uiautomation.TIME_OUT_SECOND = 1.5

pane = auto.ControlFromHandle(200048)
table = None
for ctrl, depth in auto.WalkControl(pane, maxDepth=6):
    if ctrl.ControlTypeName == 'TableControl':
        table = ctrl
        break

rows = [r for r in table.GetChildren() if r.Name.startswith('Row ')]
cell = rows[1].GetChildren()[4]
print('cell', cell.Name)
try:
    print('patterns', cell.GetSupportedPatterns())
except Exception as e:
    print('patterns err', e)
for pat in ('GetValuePattern', 'GetLegacyIAccessiblePattern', 'GetTextPattern',
            'GetGridItemPattern', 'GetTableItemPattern'):
    try:
        po = getattr(cell, pat)()
        print(pat, 'OK')
        for attr in ('Value', 'Name', 'Value', 'Help', 'Description', 'DefaultAction'):
            if hasattr(po, attr):
                print('   ', attr, repr(getattr(po, attr)))
    except Exception as e:
        print(pat, 'ERR', e)
