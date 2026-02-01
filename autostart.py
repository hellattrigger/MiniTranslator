import winreg
import sys

APP_NAME = "MiniTrans"

def set_autostart(enable: bool):
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        0, winreg.KEY_ALL_ACCESS
    )

    if enable:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, sys.argv[0])
    else:
        try:
            winreg.DeleteValue(key, APP_NAME)
        except FileNotFoundError:
            pass

    winreg.CloseKey(key)
