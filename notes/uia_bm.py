"""Dump the PSCAD Build Messages grid through UI Automation."""
import sys, time
import uiautomation as auto

auto.uiautomation.TIME_OUT_SECOND = 2

root = auto.ControlFromHandle(200048)
if root is None:
    print('no control')
    sys.exit(1)

print('control:', root.ControlTypeName, repr(root.Name))

for ctrl, depth in auto.WalkControl(root, maxDepth=6):
    print('  ' * depth, ctrl.ControlTypeName, repr(ctrl.Name)[:90])
