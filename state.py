import json
import os
from datetime import datetime
import config

class AppState:
    def __init__(self):
        self.cfg = config.load_config()
        self.history_file = "history.json"
       
        self.history = self.load_history() 
        self.listeners = []

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
               
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save history error: {e}")

    def add_history_item(self, src, dst, extra=""):
        item = {
            "src": src,
            "dst": dst,
            "extra": extra,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        self.history.insert(0, item)
        self.history = self.history[:100]
        self.save_history()

    def on_change(self, fn):
        self.listeners.append(fn)

    def set(self, key, value):
        self.cfg[key] = value
        config.save_config(self.cfg)
        for fn in self.listeners:
            fn(self.cfg)
    def delete_history_item(self, index):
        """Удаляет один элемент по индексу"""
        if 0 <= index < len(self.history):
            self.history.pop(index)
            self.save_history()

    def clear_all_history(self):
        """Полная очистка"""
        self.history = []
        self.save_history()