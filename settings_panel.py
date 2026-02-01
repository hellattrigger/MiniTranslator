from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QTimer, QEvent
from config import tr

class SettingsPanel(QWidget):
    def __init__(self, cfg, on_setting_changed):
        super().__init__()
        self.cfg = cfg
        self.on_setting_changed = on_setting_changed

        
        self.lang_codes = {"en": "English", "ru": "Русский", "uk": "Українська", "ja": "日本語"}
        self.theme_codes = {"dark": "Dark", "light": "Light", "purple": "Purple"}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)

        self.lbl_title = QLabel(tr(cfg, "settings"))
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #6a4bff; margin-bottom: 5px;")
        layout.addWidget(self.lbl_title)

        self.lbl_target = QLabel(tr(cfg, "target_language"))
        layout.addWidget(self.lbl_target)
        self.target = QComboBox()
        self.target.addItems(["English", "Русский", "Українська", "日本語"]) # Добавил пункт
        self.target.setCurrentText(self.lang_codes.get(cfg["target_lang"], "English"))
        layout.addWidget(self.target)

        self.lbl_ui = QLabel(tr(cfg, "ui_language"))
        layout.addWidget(self.lbl_ui)
        self.ui = QComboBox()
        self.ui.addItems(["English", "Русский", "Українська", "日本語"]) # Добавил пункт
        self.ui.setCurrentText(self.lang_codes.get(cfg["ui_lang"], "English"))
        layout.addWidget(self.ui)

        self.lbl_theme = QLabel(tr(cfg, "theme"))
        layout.addWidget(self.lbl_theme)
        self.theme = QComboBox()
        self.theme.addItems(["Dark", "Light", "Purple"])
        self.theme.setCurrentText(self.theme_codes.get(cfg["theme"], "Dark"))
        layout.addWidget(self.theme)

        self.lbl_hotkey = QLabel(tr(cfg, "hotkey"))
        layout.addWidget(self.lbl_hotkey)
        
        self.hotkey_btn = QPushButton(cfg.get("hotkey", "Ctrl+Alt+Shift+Q"))
        self.hotkey_btn.setMinimumHeight(45)
        self.hotkey_btn.setCursor(Qt.PointingHandCursor)
        self.hotkey_btn.setStyleSheet("font-weight: bold; border: 1px dashed #6a4bff;")
        self.hotkey_btn.clicked.connect(self.start_capture)
        layout.addWidget(self.hotkey_btn)

        options_layout = QHBoxLayout()
        self.romaji = QCheckBox(tr(cfg, "show_romaji"))
        self.romaji.setChecked(cfg.get("romaji", True))
        self.autostart = QCheckBox(tr(cfg, "autostart"))
        self.autostart.setChecked(cfg.get("autostart", False))
        options_layout.addWidget(self.romaji)
        options_layout.addWidget(self.autostart)
        layout.addLayout(options_layout)

        layout.addSpacing(10)
        self.save_btn = QPushButton(tr(cfg, "save"))
        self.save_btn.setObjectName("AccentBtn") 
        self.save_btn.setMinimumHeight(45)
        self.save_btn.clicked.connect(self.apply)
        layout.addWidget(self.save_btn)

        layout.addStretch()

    def start_capture(self):
        
        self.hotkey_btn.setText("Press combination...")
        self.hotkey_btn.setStyleSheet("font-weight: bold; border: 2px solid #00ffcc; color: #00ffcc;")
        self.grabKeyboard()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
            return
        mods = []
        if event.modifiers() & Qt.ControlModifier: mods.append("Ctrl")
        if event.modifiers() & Qt.AltModifier: mods.append("Alt")
        if event.modifiers() & Qt.ShiftModifier: mods.append("Shift")
        
        key = event.text().upper()
        if not key: key = event.key() 

        combo = "+".join(mods + [key]) if mods else key
        self.hotkey_btn.setText(combo)
        self.hotkey_btn.setStyleSheet("font-weight: bold; border: 1px dashed #6a4bff;")
        self.releaseKeyboard()

    def retranslate(self, cfg):
        self.cfg = cfg
        
        self.lbl_title.setText(tr(cfg, "settings"))
        self.lbl_target.setText(tr(cfg, "target_language"))
        self.lbl_ui.setText(tr(cfg, "ui_language"))
        self.lbl_theme.setText(tr(cfg, "theme"))
        self.lbl_hotkey.setText(tr(cfg, "hotkey"))

        self.romaji.setText(tr(cfg, "show_romaji"))
        self.autostart.setText(tr(cfg, "autostart"))
        
        
        self.save_btn.setText(tr(cfg, "save"))

    def apply(self):
        
        lang_map = {"English": "en", "Русский": "ru", "Українська": "uk", "日本語": "ja"}
        theme_map = {"Dark": "dark", "Light": "light", "Purple": "purple"}

        self.on_setting_changed("target_lang", lang_map[self.target.currentText()])
        self.on_setting_changed("ui_lang", lang_map[self.ui.currentText()])
        self.on_setting_changed("theme", theme_map[self.theme.currentText()])
        self.on_setting_changed("hotkey", self.hotkey_btn.text())
        self.on_setting_changed("romaji", self.romaji.isChecked())
        self.on_setting_changed("autostart", self.autostart.isChecked())
        
        self.save_btn.setText("✓ SUCCESS")
        QTimer.singleShot(2000, lambda: self.save_btn.setText(tr(self.cfg, "save")))