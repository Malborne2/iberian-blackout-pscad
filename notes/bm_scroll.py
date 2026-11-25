"""Scroll the PSCAD Build Messages grid to the bottom and screenshot it."""
import ctypes, os, time
import uiautomation as auto

auto.uiautomation.TIME_OUT_SECOND = 2.0
HERE = os.path.dirname(os.path.abspath(__file__))
pane = auto.ControlFromHandle(200048)
table = None
for ctrl, depth in auto.WalkControl(pane, maxDepth=6):
    if ctrl.ControlTypeName == 'TableControl':
        table = ctrl
        break
print('table', table is not None)
if table:
    table.SetFocus()
    time.sleep(0.3)
    auto.SendKeys('{End}', waitTime=0.5)
    auto.SendKeys('{Ctrl}{End}', waitTime=0.5)
    time.sleep(0.5)

import shot_hwnd
w, h = shot_hwnd.shot(200048, os.path.join(HERE, 'bm_bottom.bmp'))
print('shot', w, h)
