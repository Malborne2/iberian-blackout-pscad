import sys, time
import uiautomation as auto

auto.uiautomation.TIME_OUT_SECOND = 1.5

pane = auto.ControlFromHandle(200048)
table = None
for ctrl, depth in auto.WalkControl(pane, maxDepth=6):
    if ctrl.ControlTypeName == 'TableControl':
        table = ctrl
        break

for row in table.GetChildren():
    print('ROW', row.ControlTypeName, repr(row.Name))
    for cell in row.GetChildren():
        print('    CELL', cell.ControlTypeName, repr(cell.Name))
