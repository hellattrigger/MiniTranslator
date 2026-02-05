import ctypes
import ctypes.wintypes
import threading
import time
import pyperclip
import requests
import pykakasi
import config

user32 = ctypes.windll.user32

HOTKEY_ID = 1
MOD_ALT = 0x0001
MOD_CTRL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000  

_callback = None
_loop_thread_id = None 

try:
    kks = pykakasi.kakasi()
except:
    kks = None

def japanese_to_romaji(text):
    if not kks: return ""
    try:
        return " ".join(i["hepburn"] for i in kks.convert(text))
    except:
        return ""

def is_japanese(text):
    return any("\u3040" <= c <= "\u30ff" or "\u4e00" <= c <= "\u9fff" for c in text)

def translate_text(text, target="ru"):
    try:
        r = requests.get(
            "https://translate.googleapis.com/translate_a/single",
            params={"client": "gtx", "sl": "auto", "tl": target, "dt": "t", "q": text},
            timeout=2
        )
        r.raise_for_status()
        return "".join(i[0] for i in r.json()[0] if i[0])
    except Exception as e:
        print(f"Translation error: {e}")
        return "Error"


def get_selected_text():
    old_clipboard = pyperclip.paste()
    pyperclip.copy("")
    

    for vk in [0x12, 0x11, 0x10]:
        user32.keybd_event(vk, 0, 2, 0) 
    time.sleep(0.05)

 
    user32.keybd_event(0x11, 0, 0, 0) 
    user32.keybd_event(0x43, 0, 0, 0) 
    user32.keybd_event(0x43, 0, 2, 0) 
    user32.keybd_event(0x11, 0, 2, 0) 

    time.sleep(0.08)
    selected_text = pyperclip.paste()

    pyperclip.copy(old_clipboard)
    
    result = selected_text.strip()
    if not result:
        print("WARNING: No text selected")
        return None
    return result

def register_hotkey_from_text(hotkey_text):
    try:
        parts = hotkey_text.lower().split("+")
        mods = MOD_NOREPEAT
        if "ctrl" in parts: mods |= MOD_CTRL
        if "alt" in parts: mods |= MOD_ALT
        if "shift" in parts: mods |= MOD_SHIFT
        
        key_part = parts[-1].upper()
        key_code = ord(key_part) if len(key_part) == 1 else 0x51 

        
        user32.UnregisterHotKey(None, HOTKEY_ID)
        time.sleep(0.05) 
        
        ok = user32.RegisterHotKey(None, HOTKEY_ID, mods, key_code)
        
        if ok:
            print(f"OK: Hotkey registered — {hotkey_text}")
        else:
            print(f"ERROR: Hotkey busy or invalid — {hotkey_text}")
        
        return ok
    except Exception as e:
        print(f" FATAL HOTKEY ERROR: {e}")
        return False

def start_engine(cb, initial_hotkey=None):
    global _callback
    _callback = cb
    
    if not initial_hotkey:
        cfg = config.load_config()
        initial_hotkey = cfg.get("hotkey", "Ctrl+Alt+Shift+Q")
        
    thread = threading.Thread(target=lambda: _loop(initial_hotkey), daemon=True)
    thread.start()
    return True 

def _loop(hotkey_text):
    global _loop_thread_id
    _loop_thread_id = threading.get_ident()
    
    msg = ctypes.wintypes.MSG()
    if not register_hotkey_from_text(hotkey_text):
        return

    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        if msg.message == 0x0312: 
            _on_hotkey()
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))
    
    user32.UnregisterHotKey(None, HOTKEY_ID)
    print("🧵 Thread loop finished")

def _on_hotkey():
    text = get_selected_text()
    if text and _callback:
        _callback(text)

def stop_engine():
    global _loop_thread_id
    try:
        user32.UnregisterHotKey(None, HOTKEY_ID)
        if _loop_thread_id:
            user32.PostThreadMessageW(_loop_thread_id, 0x0012, 0, 0)
            _loop_thread_id = None
        print("Hotkey engine stopped")
    except Exception as e:
        print(f"Stop error: {e}")