"""Select-all + copy the PSCAD Build Messages grid and read the clipboard."""
import sys, time, ctypes
import uiautomation as auto

user32 = ctypes.WinDLL('user32', use_last_error=True)


def clipboard_text():
    user32.OpenClipboard(0)
    try:
        h = user32.GetClipboardData(13)  # CF_UNICODETEXT
        if not h:
            return ''
        p = ctypes.windll.kernel32.GlobalLock(h)
        try:
            return ctypes.wstring_at(p)
        finally:
            ctypes.windll.kernel32.GlobalUnlock(h)
    finally:
        user32.CloseClipboard()


pane = auto.ControlFromHandle(200048)
table = None
for ctrl, depth in auto.WalkControl(pane, maxDepth=6):
    if ctrl.ControlTypeName == 'TableControl':
        table = ctrl
        break

rows = [r for r in table.GetChildren() if r.Name.startswith('Row ')]
print('rows visible', len(rows))
rows[1].Click(simulateMove=False)
time.sleep(0.3)
table.SetFocus()
time.sleep(0.2)
auto.SendKeys('{Ctrl}a', waitTime=0.3)
auto.SendKeys('{Ctrl}c', waitTime=0.5)
txt = clipboard_text()
print('---- clipboard', len(txt))
print(txt[:8000])
