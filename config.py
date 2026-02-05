import json
import os
import os
import sys

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "enabled": True,
    "target_lang": "en", 
    "ui_lang": "en",     
    "romaji": True,
    "theme": "dark",
    "hotkey": "Ctrl+Alt+Shift+Q",
    "autostart": False
}

TRANSLATIONS = {
    "en": {
        "status": "Status", "history": "History", "settings": "Settings",
        "history_too_long": "History is overloaded. If the app feels slow, try clearing it.",
        "hide_tray": "Minimize to tray", "target_language": "Target language",
        "ui_language": "Interface language", "theme": "Theme",
        "show_romaji": "Show romaji", "hotkey": "Global hotkey",
        "autostart": "Run at Windows startup", "save": "Save and apply",
        "ready": "Ready", "open": "Open", "hide": "Hide", "exit": "Exit",
        "support_desc": "If the translator helps you, you can support the developer with a small donation.",
        "error_hotkey_title": "Hotkey Error",
        "error_hotkey_msg": "Your chosen hotkey is already in use.\nPlease select a different shortcut in Settings.",
        "copy": "COPY", "delete": "DELETE", "clear_all": "CLEAR ALL", "history_empty": "History is empty",
        "ok": "OK", "privacy_policy": "Privacy Policy",
        "guide_title": "User Guide",
        "guide_1": "1. <b>Select</b> any text with your mouse.",
        "guide_2": "2. Press <b>{}</b> shortcut.",
        "press_key": "Press {}",
        "guide_3": "3. The translation will appear on top of all apps.",
        "privacy_full": "<h2>Privacy Policy</h2><p>Mini Translator is <b>completely free</b> and non-commercial. If you paid for this program, you have been scammed.</p><p><b>1. Data:</b> All your settings and translation history are stored locally on your device. The developer does not collect, sell, or transfer your data to third parties.</p><p><b>2. Translation:</b> The text you translate is processed only for translation purposes and is not saved by the developer anywhere.</p><p><b>3. Liability:</b> The application is provided 'AS IS'. The developer is not responsible for any malfunctions, errors, or system issues.</p><p><b>4. Safety:</b> If you downloaded the program from unofficial sources, the developer is not responsible for viruses or malicious code.</p><p>By using the app, you accept these terms.</p>"
    },
    "ru": {
        "status": "Статус", "history": "История", "settings": "Настройки",
        "history_too_long": "История перегружена. Если приложение подтормаживает — очистите её.",
        "hide_tray": "Свернуть в трей", "target_language": "Язык перевода",
        "ui_language": "Язык интерфейса", "theme": "Тема",
        "support_desc": "Если переводчик вам помогает, вы можете поддержать разработчика небольшим донатом.",
        "show_romaji": "Показывать ромадзи", "hotkey": "Горячая клавиша",
        "autostart": "Запуск при старте Windows", "save": "Сохранить",
        "ready": "Готово", "open": "Открыть", "hide": "Скрыть", "exit": "Выход",
        "error_hotkey_title": "Ошибка горячей клавиши",
        "error_hotkey_msg": "Эта комбинация уже занята в системе.\nПожалуйста, выберите другую в Настройках.",
        "copy": "КОПИРОВАТЬ", "delete": "УДАЛИТЬ", "clear_all": "ОЧИСТИТЬ ВСЁ", "history_empty": "История пуста",
        "ok": "ОК", "privacy_policy": "Политика конфиденциальности",
        "guide_title": "Инструкция",
        "press_key": "Нажмите {}",
        "guide_1": "1. <b>Выделите</b> любой текст мышкой.",
        "guide_2": "2. Нажмите комбинацию <b>{}</b>.",
        "guide_3": "3. Перевод появится в окне поверх всех программ.",
        "privacy_full": "<h2>Политика конфиденциальности</h2><p>Приложение Mini Translator является <b>полностью бесплатным</b> и некоммерческим. Если вы заплатили за эту программу, вас обманули.</p><p><b>1. Данные:</b> Все ваши настройки и история переводов хранятся локально на вашем устройстве. Разработчик не собирает, не продаёт и не передаёт ваши данные третьим лицам.</p><p><b>2. Перевод:</b> Текст, который вы переводите, обрабатывается только для работы перевода и нигде не сохраняется разработчиком.</p><p><b>3. Ответственность:</b> Приложение предоставляется «как есть» (AS IS). Разработчик не несёт ответственности за возможные сбои, ошибки или проблемы в системе.</p><p><b>4. Безопасность:</b> Если вы скачали программу из неофициальных источников, разработчик не отвечает за возможные вирусы или вредоносный код.</p><p>Используя приложение, вы принимаете эти условия.</p>"
    },
    "uk": {
        "status": "Статус", "history": "Історія", "settings": "Налаштування",
        "history_too_long": "Історія перевантажена. Якщо додаток працює повільно — очистіть її.",
        "hide_tray": "Згорнути в трей", "target_language": "Мова перекладу",
        "ui_language": "Мова інтерфейсу", "theme": "Тема",
        "show_romaji": "Показувати ромадзі", "hotkey": "Гаряча клавіша",
        "support_desc": "Якщо перекладач вам допомагає, ви можете підтримати розробника невеликим донатом.",
        "autostart": "Запуск при старті Windows", "save": "Зберегти",
        "ready": "Готово", "open": "Відкрити", "hide": "Приховати", "exit": "Вихід",
        "error_hotkey_title": "Помилка клавіш",
        "error_hotkey_msg": "Ця комбінація вже зайнята.\nБудь ласка, виберіть іншу в Налаштуваннях.",
        "copy": "КОПІЮВАТІ", "delete": "ВИДАЛИТИ", "clear_all": "ОЧИСТИТИ ВСЕ", "history_empty": "Історія порожня",
        "ok": "ОК", "privacy_policy": "Політика конфіденційності",
        "guide_title": "Інструкція",
        "press_key": "Натисніть {}",
        "guide_1": "1. <b>Виділіть</b> будь-який текст мишкою.",
        "guide_2": "2. Натисніть комбінацію <b>{}</b>.",
        "guide_3": "3. Переклад з'явіться у вікні поверх усіх програм.",
        "privacy_full": "<h2>Політика конфіденційності</h2><p>Додаток Mini Translator є <b>повністю безкоштовним</b> і некомерційним. Якщо ви заплатили за цю програму, вас ошукали.</p><p><b>1. Дані:</b> Всі ваші налаштування та історія перекладів зберігаються локально на вашому пристрої. Розробник не збирає, не продає і не передає ваші дані третім особам.</p><p><b>2. Переклад:</b> Текст, який ви перекладаєте, обробляється тільки для роботи перекладу і ніде не зберігається розробником.</p><p><b>3. Відповідальність:</b> Додаток надається «як є» (AS IS). Розробник не несе відповідальності за можливі збої, помилки або проблеми в системе.</p><p><b>4. Безпека:</b> Якщо ви завантажили програму з неофіційних джерел, розробник не відповідає за можливі віруси або шкідливий код.</p><p>Використовуючи додаток, ви приймаєте ці умови.</p>"
    },
    "ja": {
        "status": "ステータス", "history": "履歴", "settings": "設定",
        "history_too_long": "履歴が多すぎます。動作が重い場合は削除してください。",
        "hide_tray": "トレイに最小化", "target_language": "翻訳言語",
        "ui_language": "表示言語", "theme": "テーマ",
        "show_romaji": "ローマ字表示", "hotkey": "ショートカットキー",
        "autostart": "Windows起動時に開始", "save": "保存",
        "ready": "準備完了", "open": "開く", "hide": "隠す", "exit": "終了",
        "error_hotkey_title": "ショートカットエラー",
        "support_desc": "このアプリがお役に立てば、開発者をサポートしていただけると嬉しいです。",
        "error_hotkey_msg": "このキーは既に使用されています。\n設定で別のキーを選択してください。",
        "copy": "コピー", "delete": "削除", "clear_all": "すべて消去", "history_empty": "履歴はありません",
        "ok": "OK", "privacy_policy": "プライバシーポリシー",
        "guide_title": "ユーザーガイド",
        "press_key": "{} を押してください",
        "guide_1": "1. マウスでテキストを<b>選択</b>します。",
        "guide_2": "2. ショートカットキー <b>{}</b> を押します。",
        "guide_3": "3. 翻訳結果がすべてのアプリの上に表示されます。",
        "privacy_full": "<h2>プライバシーポリシー</h2><p>Mini Translatorは<b>完全に無料</b>の非営利アプリです。このプログラムにお金を支払った場合、あなたは詐欺に遭った可能性があります。</p><p><b>1. データ:</b> 設定と翻訳履歴はすべてデバイスにローカルに保存されます。開発者がデータを収集、販売、または第三者に譲渡することはありません。</p><p><b>2. 翻訳:</b> 翻訳するテキストは翻訳処理のみに使用され、開発者によって保存されることはありません。</p><p><b>3. 免責事項:</b> アプリは「現状のまま」提供されます。開発者は、不具合やシステムの問題について一切の責任を負いません。</p><p><b>4. セキュリティ:</b> 非公式なソースからダウンロードされた場合、ウイルスや不正なコードについて開発者は責任を負いません。</p><p>アプリを使用することで、これらの条件に同意したことになります。</p>"
    }
}

CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

def load_config():
    
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)

                for key, val in DEFAULT_CONFIG.items():
                    if key not in cfg: cfg[key] = val
                return cfg
        except: pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
  
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def tr(cfg, key):
    ui_lang = cfg.get("ui_lang", "en")
    lang_dict = TRANSLATIONS.get(ui_lang, TRANSLATIONS["en"])
    return lang_dict.get(key, key)