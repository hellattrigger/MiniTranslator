import sys
import os
import threading
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget, QScrollArea, 
    QDialog, QSystemTrayIcon, QMenu, QStyle, QMessageBox,
    QGraphicsOpacityEffect  
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QRect, QUrl, QSharedMemory, QEasingCurve
from PySide6.QtGui import QIcon, QFont, QPixmap, QDesktopServices

import core
import config
import autostart
from state import AppState 
from settings_panel import SettingsPanel 
import os
import sys

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))




def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


ICON_PNG = resource_path(os.path.join("assets", "icon.png"))
ICON_ICO = resource_path(os.path.join("assets", "icon.ico"))
ABOUT_IMG = resource_path(os.path.join("assets", "about.png"))


def load_stylesheet(theme_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "themes", f"{theme_name}.qss")

    print(f"DEBUG: Loading theme: {path}")

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    print("DEBUG: Theme file not found!")
    return ""


def show_error(parent, title, message):
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Critical)
    box.setWindowTitle(title)
    box.setText(message)
    box.setStyleSheet(
        "QLabel { color: white; } "
        "QMessageBox { background-color: #0f0f14; }"
    )
    box.exec()



# POPUP 


class TranslatePopup(QDialog):
    def __init__(self, translated, extra="", theme="dark", parent_app=None):
        super().__init__(None)
        self.parent_app = parent_app 
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(380)
        
        self._drag_pos = None

        themes = {
            "light":  {"bg": "#ffffff", "border": "#0071e3", "text": "#1d1d1f", "extra": "#515154", "btn": "#f5f5f7"},
            "purple": {"bg": "#fcfaff", "border": "#ff85c0", "text": "#4a3a63", "extra": "#9b86bd", "btn": "#f4ebff"},
            "dark":   {"bg": "#0f0f14", "border": "#6a4bff", "text": "#00ffcc", "extra": "#9fa3ff", "btn": "#1a1a1a"}
        }
        c = themes.get(theme, themes["dark"])

        self.setStyleSheet(f"QDialog {{ background-color: {c['bg']}; border: 2px solid {c['border']}; border-radius: 12px; }}")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 40, 15)
        
        # close
        self.close_btn = QPushButton("✕", self)
        self.close_btn.setFixedSize(26, 26)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{ background: {c['btn']}; color: {c['border']}; border: none; border-radius: 6px; font-weight: bold; }}
            QPushButton:hover {{ background: #ff5555; color: white; }}
        """)
        self.close_btn.clicked.connect(self.close)

        # text trans.
        self.res_lbl = QLabel(translated)
        self.res_lbl.setWordWrap(True)
        self.res_lbl.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {c['text']}; border: none; background: transparent;")
        self.main_layout.addWidget(self.res_lbl)

        # romaji
        if extra:
            self.ex_lbl = QLabel(extra)
            self.ex_lbl.setWordWrap(True)
            self.ex_lbl.setStyleSheet(f"color: {c['extra']}; font-style: italic; border: none; background: transparent;")
            self.main_layout.addWidget(self.ex_lbl)
        
        self.adjustSize()

        # poz
        if self.parent_app and "popup_x" in self.parent_app.cfg:
            self.move(self.parent_app.cfg["popup_x"], self.parent_app.cfg["popup_y"])
        else:
            
            screen_geo = QApplication.primaryScreen().geometry()
            self.move(screen_geo.center() - self.rect().center())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self._drag_pos:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        
        if event.button() == Qt.LeftButton and self.parent_app:
            new_pos = self.pos()
            self.parent_app.state.set("popup_x", new_pos.x())
            self.parent_app.state.set("popup_y", new_pos.y())
        self._drag_pos = None
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.close_btn.move(self.width() - 32, 8)



#histor

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QApplication
)
from PySide6.QtCore import Qt, Signal

class HistoryPage(QWidget):
    delete_requested = Signal(int)
    clear_all_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        #warning
        self.warning_box = QFrame()
        self.warning_box.setObjectName("SmartWarning")
        self.warning_box.setFixedHeight(55)
        self.warning_box.setGraphicsEffect(QGraphicsOpacityEffect())

        warn_l = QHBoxLayout(self.warning_box)
        self.warn_text = QLabel("")
        self.warn_clear_btn = QPushButton("ОЧИСТИТЬ")
        self.warn_clear_btn.setCursor(Qt.PointingHandCursor)
        self.warn_clear_btn.clicked.connect(
            lambda: self.clear_all_requested.emit()
        )

        warn_l.addWidget(QLabel("⚠️"))
        warn_l.addWidget(self.warn_text)
        warn_l.addStretch()
        warn_l.addWidget(self.warn_clear_btn)

        self.layout.addWidget(self.warning_box)
        self.warning_box.hide()

        header = QHBoxLayout()
        self.title_label = QLabel("HISTORY")
        self.clear_all_btn = QPushButton("CLEAR ALL")
        self.clear_all_btn.clicked.connect(
            lambda: self.clear_all_requested.emit()
        )

        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.clear_all_btn)
        self.layout.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignTop)

        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)

    def render_history(self, history_data, cfg=None):
        from config import tr
        t = lambda key: tr(cfg, key) if cfg else key

        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        theme = cfg.get("theme", "dark") if cfg else "dark"
        
        # palitr
        if theme == "light":
            src_c, dst_c = "#555", "#0071e3"
            accent = "#0071e3"   
            danger = "#ff3b30"   
            card_bg = "#f5f5f7"
        elif theme == "purple":
            src_c, dst_c = "#9b86bd", "#d4448c"
            accent = "#d4448c"  
            danger = "#ff85c0"  
            card_bg = "#f4ebff"
        else: # Dark
            src_c, dst_c = "#ccc", "#00ffcc"
            accent = "#6a4bff"  
            danger = "#ff5555"   
            card_bg = "#1a1a24"

        # clear all new
        self.clear_all_btn.setText(t("clear_all").upper())
        self.clear_all_btn.setStyleSheet(f"""
            QPushButton {{
                color: {danger}; border: 1px solid {danger}; 
                border-radius: 4px; padding: 4px 8px; font-weight: bold; background: transparent;
            }}
            QPushButton:hover {{ background: {danger}; color: white; }}
        """)

# 4. waring panel thm
        if theme == "light":

            w_bg, w_brd, w_txt = "rgba(0, 113, 227, 15)", "rgba(0, 113, 227, 60)", "#0071e3"
        elif theme == "purple":

            w_bg, w_brd, w_txt = "rgba(212, 68, 140, 15)", "rgba(212, 68, 140, 60)", "#d4448c"
        else:

            w_bg, w_brd, w_txt = "rgba(255, 85, 85, 12)", "rgba(255, 85, 85, 50)", "#ff9999"

        if len(history_data) > 50:
            self.warning_box.show()
            self.warn_text.setText(t("history_too_long"))

            self.warning_box.setStyleSheet(f"""
                QFrame#SmartWarning {{
                    background-color: {w_bg};
                    border: 1px solid {w_brd};
                    border-radius: 12px;
                }}
                QLabel {{
                    color: {w_txt};
                    font-size: 13px;
                    font-weight: 500;
                    background: transparent;
                    border: none;
                }}
            """)

            self.warn_clear_btn.setText(t("clear_all").upper())
            self.warn_clear_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {w_txt};
                    color: white;
                    border-radius: 7px;
                    padding: 4px 14px;
                    font-weight: bold;
                    font-size: 11px;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {w_brd}; /* Эффект затухания при наведении */
                }}
            """)
        else:
            self.warning_box.hide()

        for i, item in enumerate(history_data):
            card = QFrame()
            card.setStyleSheet(f"background-color: {card_bg}; border-radius: 10px; margin-bottom: 5px;")
            card_layout = QVBoxLayout(card)
            
            src_lbl = QLabel(item["src"])
            src_lbl.setWordWrap(True)
            src_lbl.setStyleSheet(f"color: {src_c}; font-size: 14px; background: transparent; border: none;")
            
            dst_lbl = QLabel(item["dst"])
            dst_lbl.setWordWrap(True)
            dst_lbl.setStyleSheet(f"color: {dst_c}; font-weight: bold; font-size: 15px; background: transparent; border: none;")
            
            card_layout.addWidget(src_lbl)
            card_layout.addWidget(dst_lbl)

            btns_row = QHBoxLayout()
            btns_row.addStretch()

            copy_btn = QPushButton(t("copy") if cfg else "КОПИРОВАТЬ")
            copy_btn.setCursor(Qt.PointingHandCursor)
            copy_btn.setStyleSheet(f"""
                QPushButton {{
                    color: {accent}; border: 1px solid {accent}; border-radius: 5px; padding: 4px 10px; background: transparent;
                }}
                QPushButton:hover {{ background: {accent}; color: white; }}
            """)
            copy_btn.clicked.connect(lambda ch, text=item["dst"]: QApplication.clipboard().setText(text))

            del_btn = QPushButton(t("delete") if cfg else "УДАЛИТЬ")
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setStyleSheet(f"""
                QPushButton {{
                    color: {danger}; border: 1px solid {danger}; border-radius: 5px; padding: 4px 10px; background: transparent;
                }}
                QPushButton:hover {{ background: {danger}; color: white; }}
            """)
            del_btn.clicked.connect(lambda ch, idx=i: self.delete_requested.emit(idx))
            
            btns_row.addWidget(copy_btn)
            btns_row.addWidget(del_btn)
            card_layout.addLayout(btns_row)
            
            self.container_layout.addWidget(card)


class MiniTranslatorApp(QWidget):
    translate_req_signal = Signal(str)
    show_result_signal = Signal(str, str, str)

    def __init__(self):
        super().__init__()

        self.state = AppState()
        self.cfg = self.state.cfg

        self.setWindowTitle("Mini Translator")
        self.resize(900, 600)

        self.build_ui()

        self.state.on_change(self.apply_all)
        self.translate_req_signal.connect(self._process_translation)
        self.show_result_signal.connect(self._on_display_result)

        # hotkei engine
        core.start_engine(self.on_hotkey, self.cfg.get("hotkey", "Ctrl+Alt+Shift+Q"))

        self.apply_all(self.cfg)

    def build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0,0,0,0)

        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setObjectName("Sidebar")

        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(10, 30, 10, 10)

        self.btn_status = QPushButton()
        self.btn_history = QPushButton()
        self.btn_settings = QPushButton()

        for b in [self.btn_status, self.btn_history, self.btn_settings]:
            b.setFixedHeight(45)
            b.setCursor(Qt.PointingHandCursor)
            b.setObjectName("SideBtn")
            b.setCheckable(True) 
            side_layout.addWidget(b)

        side_layout.addStretch()

        self.btn_hide = QPushButton("Hide to Tray")
        self.btn_hide.clicked.connect(self.hide)
        side_layout.addWidget(self.btn_hide)

        root.addWidget(sidebar)

        self.pages = QStackedWidget()

        # Statusssssssssss page
        status_page = QWidget()
        status_layout = QVBoxLayout(status_page)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setTextFormat(Qt.RichText)

        info_btns_layout = QVBoxLayout()
        info_btns_layout.setSpacing(10)

        self.about_btn = QPushButton("About")
        self.about_btn.setFixedSize(140, 40)
        self.about_btn.setCursor(Qt.PointingHandCursor)
        self.about_btn.clicked.connect(self.show_about_panel)
        self.about_btn.setObjectName("AccentBtn")

        self.guide_btn = QPushButton("Guide")
        self.guide_btn.setFixedSize(100, 30)
        self.guide_btn.setCursor(Qt.PointingHandCursor)
        self.guide_btn.clicked.connect(self.show_guide)
        self.guide_btn.setObjectName("AccentBtn")

        info_btns_layout.addWidget(self.about_btn, alignment=Qt.AlignCenter)
        info_btns_layout.addWidget(self.guide_btn, alignment=Qt.AlignCenter)

# (GitHub + Copyright + Privacy
        bottom_row = QHBoxLayout()
        
        self.github_link = QLabel()
        self.github_link.setOpenExternalLinks(True)
        self.github_link.setCursor(Qt.PointingHandCursor)
        gh_url = "https://github.com/hellattrigger/MiniTranslator"
        self.github_link.setText(f'<a href="{gh_url}" style="text-decoration: none; color: #666;">GitHub</a>')
        self.github_link.setStyleSheet("QLabel { color: #666; font-size: 11px; background: transparent; } QLabel:hover { text-decoration: underline; }")

        self.copyright = QLabel("© 2026 • hellattrigger")
        self.copyright.setStyleSheet("color: #666; font-size: 11px; background: transparent;")

        self.privacy_btn = QPushButton("Privacy & Terms")
        self.privacy_btn.setCursor(Qt.PointingHandCursor)
        self.privacy_btn.clicked.connect(self.show_privacy)
        self.privacy_btn.setStyleSheet("QPushButton { background: transparent; color: #666; border: none; font-size: 11px; text-decoration: underline; } QPushButton:hover { color: #888; }")

        bottom_row.addStretch()
        bottom_row.addWidget(self.github_link)
        bottom_row.addSpacing(20)
        bottom_row.addWidget(self.copyright)
        bottom_row.addSpacing(20)
        bottom_row.addWidget(self.privacy_btn)
        bottom_row.addStretch()

        status_layout.addStretch()
        status_layout.addWidget(self.status_label)
        status_layout.addSpacing(20)
        status_layout.addLayout(info_btns_layout)
        status_layout.addStretch()
        status_layout.addLayout(bottom_row)

        self.page_history = HistoryPage()

        self.page_history.delete_requested.connect(self._delete_history_item)
        self.page_history.clear_all_requested.connect(self._clear_history)

        self.page_settings = SettingsPanel(self.cfg, self.state.set)

        self.pages.addWidget(status_page)
        self.pages.addWidget(self.page_history)
        self.pages.addWidget(self.page_settings)

        root.addWidget(self.pages)

        self.btn_status.clicked.connect(lambda: self.switch_page(0))
        self.btn_history.clicked.connect(lambda: self.switch_page(1))
        self.btn_settings.clicked.connect(lambda: self.switch_page(2))

    # logic

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)
        self.btn_status.setChecked(index == 0)
        self.btn_history.setChecked(index == 1)
        self.btn_settings.setChecked(index == 2)
        if index == 1:
            self.page_history.render_history(self.state.history, self.cfg)

    def on_hotkey(self, text):
        if text: self.translate_req_signal.emit(text)

    def _process_translation(self, text):
        def worker():
            try:
                dst = core.translate_text(text, self.cfg.get("target_lang", "ru"))
                extra = core.japanese_to_romaji(text) if (self.cfg.get("romaji") and core.is_japanese(text)) else ""
                self.show_result_signal.emit(text, dst, extra)
            except: pass
        threading.Thread(target=worker, daemon=True).start()

    def _on_display_result(self, src, dst, extra):
        from app import TranslatePopup 
        self.popup = TranslatePopup(dst, extra, self.cfg.get("theme", "dark"), self)
        self.popup.show()
        self.state.add_history_item(src, dst, extra)

    def apply_all(self, cfg):
        self.cfg = cfg

        from app import load_stylesheet
        self.setStyleSheet(load_stylesheet(cfg.get("theme", "dark")))

        from config import tr
        t = lambda key: tr(self.cfg, key)
        self.btn_status.setText(t("status"))
        self.btn_history.setText(t("history"))
        self.btn_settings.setText(t("settings"))
        self.status_label.setText(f"<h1>{t('ready')}</h1><p>{t('press_key').format(self.cfg.get('hotkey', ''))}</p>")

    def _delete_history_item(self, index):
        self.state.delete_history_item(index)
        self.page_history.render_history(self.state.history, self.cfg)

    def _clear_history(self):
        self.state.clear_all_history()
        self.page_history.render_history([], self.cfg)

    def show_about_panel(self): pass
    def show_guide(self): pass
    def show_privacy(self): pass

    #guide
    def show_guide(self):
        from config import tr
        t = lambda key: tr(self.cfg, key)
        
        theme = self.cfg.get("theme", "dark")
        hotkey = self.cfg.get("hotkey", "Ctrl+Alt+Shift+Q")

        #colors
        if theme == "light":
            accent, text_c, line_c = "#0071e3", "#1d1d1f", "#d2d2d7"
            bg_c = "#ffffff"
        elif theme == "purple":
            accent, text_c, line_c = "#d4448c", "#4a3a63", "#ff85c0"
            bg_c = "#fcfaff"
        else:
            accent, text_c, line_c = "#6a4bff", "#e6e6ff", "#2a2a3a"
            bg_c = "#0f0f14"


        guide_html = f"""
        <h2 style='color: {accent}; text-align: center;'>{t('guide_title')}</h2>
        <hr color='{line_c}'>
        <div style='color: {text_c}; font-size: 14px; line-height: 150%;'>
            <p>{t('guide_1')}</p>
            <p>{t('guide_2').format(hotkey)}</p>
            <p>{t('guide_3')}</p>
        </div>
        """

        dialog = QDialog(self)
        dialog.setWindowTitle(t("guide_title"))
        dialog.setMinimumSize(400, 260)
        
        
        dialog.setStyleSheet(f"background-color: {bg_c}; border-radius: 12px;")

        v_layout = QVBoxLayout(dialog)
        v_layout.setContentsMargins(25, 20, 25, 20)

        lbl = QLabel(guide_html)
        lbl.setWordWrap(True)
        lbl.setTextFormat(Qt.RichText)
        lbl.setStyleSheet("background: transparent; border: none;")
        v_layout.addWidget(lbl)
        
        #ОК
        btn = QPushButton(t("ok"))
        btn.setFixedSize(110, 35)
        btn.setCursor(Qt.PointingHandCursor)
        
       
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent};
                color: white;
                border-radius: 17px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {accent}cc;
            }}
        """)
        
        btn.clicked.connect(dialog.close)
        v_layout.addWidget(btn, alignment=Qt.AlignCenter)
        
        dialog.exec()
#about
    def show_about_panel(self):
        theme = self.cfg.get("theme", "dark")
        if theme == "light":
            accent, text_c, bg_card, border_c = "#0071e3", "#1d1d1f", "#ffffff", "#d2d2d7"
        elif theme == "purple":
            accent, text_c, bg_card, border_c = "#d4448c", "#4a3a63", "#fcfaff", "#ff85c0"
        else:
            accent, text_c, bg_card, border_c = "#6a4bff", "#e6e6ff", "#12121a", "#6a4bff"

        about_page = QWidget()
        layout = QVBoxLayout(about_page)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setFixedSize(320, 480) 
        card.setStyleSheet(f"QFrame {{ background-color: {bg_card}; border: 2px solid {border_c}; border-radius: 20px; }}")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(8)

       
        img_label = QLabel()
        pix = QPixmap(ABOUT_IMG)
        if not pix.isNull():
            img_label.setPixmap(pix.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        img_label.setStyleSheet("border: none; background: transparent;")
        card_layout.addWidget(img_label, alignment=Qt.AlignCenter)

        name_label = QLabel(f"<span style='color: {text_c};'>Created by:</span> "
                            f"<span style='color: {accent}; font-weight: bold;'>hellattrigger</span>")
        name_label.setStyleSheet("font-size: 16px; border: none; background: transparent; margin-top: 5px;")
        name_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(name_label)

        
        contact_title = QLabel("Get in touch via Telegram:")
        contact_title.setStyleSheet("color: gray; font-size: 11px; border: none; background: transparent; margin-top: 12px;")
        contact_title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(contact_title)

        tg_link = QLabel(f"<a href='https://t.me/ribyuhkii' style='color: {accent}; text-decoration: none;'>@ribyuhkii</a>")
        tg_link.setOpenExternalLinks(True)
        tg_link.setStyleSheet("font-size: 15px; font-weight: 600; border: none; background: transparent;")
        tg_link.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(tg_link)

        card_layout.addStretch()

        
        donate_btn = QPushButton("☕ Support me")
        donate_btn.setCursor(Qt.PointingHandCursor)
        donate_btn.setFixedSize(160, 38)
        donate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {accent};
                border: 2px solid {accent};
                border-radius: 19px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {accent};
                color: white;
            }}
        """)
        donate_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://donatello.to/hellattrigger")))
        card_layout.addWidget(donate_btn, alignment=Qt.AlignCenter)

        # BACK
        back_btn = QPushButton("BACK")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setFixedSize(160, 38)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent};
                color: white;
                border-radius: 19px;
                font-weight: bold;
                font-size: 12px;
                border: none;
                margin-top: 5px;
            }}
            QPushButton:hover {{
                background-color: {"#ffb3d9" if theme == "purple" else ("#005bb5" if theme == "light" else "#563acc")};
            }}
        """)
        back_btn.clicked.connect(lambda: self.switch_page(0))
        card_layout.addWidget(back_btn, alignment=Qt.AlignCenter)

        layout.addWidget(card)
        idx = self.pages.addWidget(about_page)
        self.pages.setCurrentIndex(idx)

    def show_privacy(self):
        from config import tr
        t = lambda key: tr(self.cfg, key)
        
        theme = self.cfg.get("theme", "dark")
        # color2
        accent = "#0071e3" if theme == "light" else ("#d4448c" if theme == "purple" else "#6a4bff")
        text_c = "#1d1d1f" if theme == "light" else ("#4a3a63" if theme == "purple" else "#e6e6ff")
        bg_c = "#ffffff" if theme == "light" else ("#fcfaff" if theme == "purple" else "#0f0f14")

        dialog = QDialog(self)
        dialog.setWindowTitle(t("privacy_policy"))
        dialog.setMinimumSize(450, 450)
        dialog.setStyleSheet(f"background-color: {bg_c}; border-radius: 12px;")

        v_layout = QVBoxLayout(dialog)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)

        lbl = QLabel(t("privacy_full")) 
        lbl.setWordWrap(True)
        lbl.setTextFormat(Qt.RichText) 
        lbl.setStyleSheet(f"color: {text_c}; font-size: 13px; line-height: 140%;")
        
        content_layout.addWidget(lbl)
        scroll.setWidget(content)
        v_layout.addWidget(scroll)

        
        btn = QPushButton(t("ok"))
        btn.setFixedSize(120, 35)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"background-color: {accent}; color: white; border-radius: 17px; font-weight: bold; border: none;")
        btn.clicked.connect(dialog.close)
        
        v_layout.addWidget(btn, alignment=Qt.AlignCenter)
        dialog.exec()


    def switch_page(self, index):
        if self.pages.currentIndex() == index:
            return

        
        self.fade_effect = QGraphicsOpacityEffect(self.pages)
        self.pages.setGraphicsEffect(self.fade_effect)

        
        self.fade_anim = QPropertyAnimation(self.fade_effect, b"opacity")
        self.fade_anim.setDuration(250)           
        self.fade_anim.setStartValue(0.0)         
        self.fade_anim.setEndValue(1.0)          
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad) 

        
        self.pages.setCurrentIndex(index)
        self.fade_anim.start()

      
        buttons = [self.btn_status, self.btn_history, self.btn_settings]
        for i, btn in enumerate(buttons):
            btn.setChecked(i == index)

    
    def _delete_history_item(self, index):
        self.state.delete_history_item(index)
        self.page_history.render_history(
            self.state.history, self.cfg
        )

    def _clear_history(self):
        self.state.clear_all_history()
        self.page_history.render_history(
            self.state.history, self.cfg
        )

    # CORE
    def force_restart_app(self):
        os.execl(sys.executable, sys.executable, *sys.argv)

    def apply_all(self, cfg):
        self.cfg = cfg
        core.stop_engine()
        import time
        time.sleep(0.1)
        core.start_engine(self.on_hotkey, cfg.get("hotkey", "Ctrl+Alt+Shift+Q"))
        try: autostart.set_autostart(cfg.get("autostart", False))
        except: pass

        theme_name = cfg.get("theme", "dark")
        style_data = load_stylesheet(theme_name)

        
        if theme_name == "light":
            accent, hover_bg, border = "#0071e3", "#eef7ff", "#0071e3"
        elif theme_name == "purple":
            
            accent, hover_bg, border = "#ff85c0", "#f9f0ff", "#ff85c0"
            style_data = """
                QWidget { background-color: #fcfaff; color: #4a3a63; border: none; }
                QFrame#Sidebar { background-color: #f4ebff; border: none; }
                QLabel { background: transparent; border: none; }
            """ 
        else:
            accent, hover_bg, border = None, None, None

        if accent:
            style_data += f"""
                QPushButton#SideBtn {{
                    background-color: transparent;
                    color: {accent};
                    border: 2px solid {border};
                    border-radius: 12px;
                    margin: 5px;
                    font-weight: bold;
                }}
                QPushButton#SideBtn:hover {{ background-color: {hover_bg}; }}
                QPushButton#SideBtn:checked {{ background-color: {accent}; color: white; border: none; }}
                QPushButton#AccentBtn {{
                    background-color: {accent};
                    color: white;
                    border-radius: 18px;
                    font-weight: bold;
                    border: none;
                }}
                /* Убираем рамки у полей настроек */
                QComboBox, QLineEdit {{ border: 1px solid {border}22; border-radius: 8px; padding: 5px; }}
            """

        if style_data:
            self.setStyleSheet(style_data)
        self.retranslate_ui()

    def retranslate_ui(self):
        from config import tr
        t = lambda key: tr(self.cfg, key)

        self.btn_status.setText(t("status"))
        self.btn_history.setText(t("history"))
        self.btn_settings.setText(t("settings"))
        self.btn_hide.setText(t("hide_tray"))

        if hasattr(self, "page_settings"):
            self.page_settings.retranslate(self.cfg)

        theme = self.cfg.get("theme", "dark")
        if theme == "light":
            accent = "#0071e3"
        elif theme == "purple":
            accent = "#d4448c" 
        else:
            accent = "#6a4bff"
            
        #(READY / PRESS KEY)
        hotkey = self.cfg.get("hotkey", "Ctrl+Alt+Q")
        ready_text = t("ready").upper()
        press_text = t("press_key").format(hotkey)
        
        self.status_label.setText(
            f"<div style='text-align: center; color: {accent};'>"
            f"<div style='font-size: 28px; font-weight: 800;'>{ready_text}</div>"
            f"<div style='font-size: 14px; margin-top: 8px; color: #8e82a8;'>{press_text}</div>"
            f"</div>"
        )

        if hasattr(self, "page_history"):
            self.page_history.render_history(self.state.history, self.cfg)

    def on_hotkey(self, text):
        if text:
            self.translate_req_signal.emit(text)

    def _process_translation(self, text):
        def worker():
            try:
                dst = core.translate_text(
                    text,
                    self.state.cfg["target_lang"]
                )

                extra = ""
                if (
                    self.state.cfg.get("romaji", True)
                    and core.is_japanese(text)
                ):
                    extra = core.japanese_to_romaji(text)

                self.show_result_signal.emit(
                    text, dst, extra
                )
            except Exception as e:
                print("Translate error:", e)

        threading.Thread(
            target=worker, daemon=True
        ).start()

    def _on_display_result(self, src, dst, extra):
        theme = self.cfg.get("theme", "dark")

        self.popup = TranslatePopup(
            dst, extra, theme, self
        )
        self.popup.show()

        self.state.add_history_item(src, dst, extra)
        self.page_history.render_history(self.state.history, self.cfg)




if __name__ == "__main__":
    app = QApplication(sys.argv)

    shared = QSharedMemory("MiniTranslatorSingleton")
    if not shared.create(1):
        sys.exit(0)

    if os.path.exists(ICON_ICO):
        app.setWindowIcon(QIcon(ICON_ICO))

    win = MiniTranslatorApp()
    win.show()

    tray = QSystemTrayIcon(app)
    if os.path.exists(ICON_ICO):
        tray.setIcon(QIcon(ICON_ICO))
    else:
        tray.setIcon(
            app.style().standardIcon(
                QStyle.SP_ComputerIcon
            )
        )

    menu = QMenu()
    menu.addAction("Show", win.showNormal)
    menu.addAction("Restart", win.force_restart_app)
    menu.addSeparator()
    menu.addAction("Exit", app.quit)

    tray.setContextMenu(menu)
    tray.show()

    sys.exit(app.exec())
