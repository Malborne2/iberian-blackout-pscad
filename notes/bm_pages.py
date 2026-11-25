"""Page through the PSCAD Build Messages grid, screenshotting each page."""
import os, sys, time
import uiautomation as auto
import shot_hwnd

auto.uiautomation.TIME_OUT_SECOND = 2.0
HERE = os.path.dirname(os.path.abspath(__file__))
pages = int(sys.argv[1]) if len(sys.argv) > 1 else 4

pane = auto.ControlFromHandle(200048)
table = None
for ctrl, depth in auto.WalkControl(pane, maxDepth=6):
    if ctrl.ControlTypeName == 'TableControl':
        table = ctrl
        break
table.SetFocus()
auto.SendKeys('{Home}', waitTime=0.4)
time.sleep(0.4)
for i in range(pages):
    w, h = shot_hwnd.shot(200048, os.path.join(HERE, 'bm_p%d.bmp' % i))
    print('page', i, w, h)
    auto.SendKeys('{PgDn}', waitTime=0.4)
    time.sleep(0.4)
