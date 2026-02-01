import ctypes
import ctypes.wintypes
import threading
import time
import tkinter as tk
from tkinter import ttk
import pyperclip
import requests
import json
import os
import traceback
import pykakasi
import pystray
from PIL import Image, ImageDraw


CONFIG_FILE = "config.json"

default_config = {
    "enabled": True,
    "target_lang": "ru",
    "romaji": True
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            return json.load(open(CONFIG_FILE, "r", encoding="utf-8"))
        except:
            pass
    return default_config.copy()

def save_config():
    json.dump(config, open(CONFIG_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

config = load_config()


HOTKEY_MOD = 0x0002 | 0x0001 | 0x0004  
HOTKEY_VK = 0x51   # Q
HOTKEY_ID = 1

user32 = ctypes.windll.user32



try:
    kks = pykakasi.kakasi()
except:
    kks = None

def japanese_to_romaji(text):
    if not kks:
        return ""
    return " ".join(i["hepburn"] for i in kks.convert(text))



def translate_text(text):
    try:
        r = requests.get(
            "https://translate.googleapis.com/translate_a/single",
            params={
                "client": "gtx",
                "sl": "auto",
                "tl": config["target_lang"],
                "dt": "t",
                "q": text
            },
            timeout=8
        )
        return "".join(i[0] for i in r.json()[0] if i[0])
    except:
        return " Ошибка перевода"



def get_selected_text():
    old = pyperclip.paste()
    pyperclip.copy("")
    time.sleep(0.05)

 
    user32.keybd_event(0x12, 0, 2, 0)
    user32.keybd_event(0x10, 0, 2, 0)
    time.sleep(0.02)


    user32.keybd_event(0x11, 0, 0, 0)
    user32.keybd_event(0x43, 0, 0, 0)
    user32.keybd_event(0x43, 0, 2, 0)
    user32.keybd_event(0x11, 0, 2, 0)

    time.sleep(0.25)
    text = pyperclip.paste()
    pyperclip.copy(old)
    return text.strip()



def show_window(text):
    win = tk.Toplevel()
    win.title("Mini Translator")
    win.geometry("420x300")
    win.attributes("-topmost", True)

    tk.Label(win, text="Original:", fg="gray").pack(pady=(8,0))
    tk.Label(win, text=text, wraplength=380).pack()

    tr = translate_text(text)
    tk.Label(win, text="Translation:", font=("Arial",10,"bold")).pack(pady=(10,0))
    tk.Label(win, text=tr, fg="blue", wraplength=380).pack()

    if config["romaji"]:
        if any("\u3040" <= c <= "\u30ff" or "\u4e00" <= c <= "\u9fff" for c in text):
            romaji = japanese_to_romaji(text)
            if romaji:
                tk.Label(win, text="Romaji:", fg="green").pack(pady=(10,0))
                tk.Label(win, text=romaji, wraplength=380).pack()

    ttk.Button(win, text="OK", command=win.destroy).pack(pady=12)



def on_hotkey():
    if not config["enabled"]:
        return
    try:
        text = get_selected_text()
        if text:
            root.after(0, lambda: show_window(text))
    except:
        traceback.print_exc()

def hotkey_loop():
    if not user32.RegisterHotKey(None, HOTKEY_ID, HOTKEY_MOD, HOTKEY_VK):
        print("Failed to register hotkey")
        return

    msg = ctypes.wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        if msg.message == 0x0312:
            on_hotkey()



root = tk.Tk()
root.title("Mini Translator Settings")
root.geometry("320x260")

enabled_var = tk.BooleanVar(value=config["enabled"])
romaji_var = tk.BooleanVar(value=config["romaji"])
lang_var = tk.StringVar(value=config["target_lang"])

ttk.Checkbutton(root, text="Enable translator", variable=enabled_var).pack(anchor="w", pady=6, padx=10)
ttk.Checkbutton(root, text="Show Romaji (JP)", variable=romaji_var).pack(anchor="w", pady=6, padx=10)

ttk.Label(root, text="Target language:").pack(anchor="w", padx=10)
ttk.Combobox(root, textvariable=lang_var, values=["ru","en","ua","ja","de","fr","es"], width=10).pack(anchor="w", padx=10)

def save_settings():
    config["enabled"] = enabled_var.get()
    config["romaji"] = romaji_var.get()
    config["target_lang"] = lang_var.get()
    save_config()

ttk.Button(root, text="Save", command=save_settings).pack(pady=12)



def create_image():
    img = Image.new("RGB", (64,64), "black")
    d = ImageDraw.Draw(img)
    d.rectangle((8,8,56,56), fill="white")
    d.text((18,18), "T", fill="black")
    return img

def show_settings(icon=None, item=None):
    root.after(0, root.deiconify)

def quit_app(icon, item):
    icon.stop()
    root.after(0, root.destroy)

tray_icon = pystray.Icon(
    "MiniTranslator",
    create_image(),
    "Mini Translator",
    menu=pystray.Menu(
        pystray.MenuItem("Settings", show_settings),
        pystray.MenuItem("Exit", quit_app)
    )
)

def hide_window():
    save_settings()
    root.withdraw()

root.protocol("WM_DELETE_WINDOW", hide_window)

threading.Thread(target=tray_icon.run, daemon=True).start()
threading.Thread(target=hotkey_loop, daemon=True).start()

root.mainloop()
