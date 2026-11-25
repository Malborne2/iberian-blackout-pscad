import ctypes, ctypes.wintypes as wt, time, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shot_hwnd import shot

user32 = ctypes.WinDLL('user32', use_last_error=True)

HWND_TOOLBAR = 134572
HWND_PANE = 134554


def click(hwnd, x, y):
    lp = (y << 16) | (x & 0xFFFF)
    user32.PostMessageW(hwnd, 0x0200, 0, lp)          # WM_MOUSEMOVE
    user32.PostMessageW(hwnd, 0x0201, 1, lp)          # WM_LBUTTONDOWN
    time.sleep(0.05)
    user32.PostMessageW(hwnd, 0x0202, 0, lp)          # WM_LBUTTONUP
    time.sleep(0.6)


name = sys.argv[1] if len(sys.argv) > 1 else 'errors'
x = int(sys.argv[2]) if len(sys.argv) > 2 else 30
y = int(sys.argv[3]) if len(sys.argv) > 3 else 10
click(HWND_TOOLBAR, x, y)
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'buildmsg_' + name + '.png')
print(shot(HWND_PANE, p))
