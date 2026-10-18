"""
پی‌دی‌اف ایمیجر (PDF Imager) v1.0
تبدیل حرفه‌ای PDF به تصویر — تکی و دسته‌ای.

- موتور رندر : PyMuPDF (fitz)
- ذخیره‌سازی  : Pillow
- رابط کاربری: PySide6 (Qt)
- خروجی       : WEBP / JPG / PNG / TIFF / BMP، و در صورت نیاز ZIP یا CBZ

اجرا:
    pip install -r requirements.txt
    python pdf_imager.py

Developer: ARVETHRON — https://github.com/arvethron
"""

import os
import re
import sys
import time
import zipfile
import traceback
from dataclasses import dataclass, field
from typing import List, Optional

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover
    fitz = None

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

from PySide6.QtCore import Qt, QThread, Signal, QPoint, QTimer, QSettings, QUrl
from PySide6.QtGui import QColor, QPainter, QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QLineEdit, QComboBox, QCheckBox, QFileDialog,
    QMessageBox, QProgressBar, QStackedWidget, QSpinBox, QTextEdit, QFrame,
    QSizePolicy, QButtonGroup, QScrollArea,
)

APP_ID = "PDFImager"
APP_VER = "v1.0"
DEVELOPER = "ARVETHRON"
GITHUB_URL = "https://github.com/arvethron"
TELEGRAM_URL = "https://t.me/ARVETHRON"

# ----------------------------------------------------------------------------
# زبان و ترجمه
# ----------------------------------------------------------------------------
LANG = "fa"  # "fa" یا "en"؛ در main از تنظیمات ذخیره‌شده خوانده می‌شود

FONTS = {
    "fa": "'Vazirmatn', 'Vazir', 'Segoe UI', 'Tahoma'",
    "en": "'Segoe UI', 'Inter', 'Vazirmatn', 'Tahoma'",
}

FA = {
    "app_name": "پی‌دی‌اف ایمیجر",
    "tip_close": "بستن",
    "tip_max": "بزرگ‌نمایی",
    "tip_min": "کوچک‌نمایی",
    "tip_lang": "تغییر زبان به English",
    "color_cyan": "فیروزه‌ای",
    "color_green": "سبز",
    "color_yellow": "زرد",
    "color_orange": "نارنجی",
    "color_red": "قرمز",
    "color_purple": "بنفش",
    "color_blue": "آبی",
    "tab_work": "🖼  صفحه اصلی",
    "tab_settings": "⚙  تنظیمات",
    "tab_about": "ℹ  درباره ما",

    # میز کار
    "src_empty": "منبع فایل‌های PDF",
    "src_many": "{n} فایل PDF انتخاب شد (حالت دسته‌ای)",
    "tip_pick_file": "انتخاب فایل PDF (تکی یا چندتایی)",
    "tip_pick_dir": "انتخاب پوشه (حالت دسته‌ای)",
    "fmt_title": "فرمت خروجی  🖼",
    "stitch_off": "☰  تک‌صفحه‌ای",
    "stitch_on": "☰  چسباندن صفحات",
    "gray_off": "✳  رنگی",
    "gray_on": "✳  سیاه‌وسفید",
    "btn_cbz": "📦  خروجی CBZ",
    "btn_folder_pdf": "🗂  پوشه‌ی هر PDF",
    "btn_zip": "🗜  فشرده‌سازی ZIP",
    "state_ready": "آماده برای شروع",
    "state_running": "در حال پردازش...",
    "state_stopping": "در حال توقف...",
    "state_done": "پایان — موفق: {ok} | ناموفق: {fail}",
    "progress_page": "{name} • صفحه {page}",
    "btn_start": "🚀  شروع عملیات",
    "btn_stop": "⛔  توقف",
    "log_done": "■ تمام شد. خروجی در: {out}",

    # پیام‌ها و گفتگوها
    "warn_empty_title": "خالی",
    "warn_empty_body": "در این پوشه فایل PDF پیدا نشد.",
    "warn_nofile_title": "فایلی انتخاب نشده",
    "warn_nofile_body": "اول فایل PDF یا پوشه را انتخاب کنید.",
    "err_lib_title": "کتابخانه ناقص",
    "err_lib_body": "نصب کنید:\n\npip install pymupdf pillow",
    "dlg_pick_pdf": "انتخاب فایل PDF",
    "dlg_pick_dir": "انتخاب پوشه حاوی PDF",
    "dlg_out": "پوشه خروجی",
    "filter_pdf": "فایل‌های PDF (*.pdf)",

    # گزارش عملیات (ترد پردازش)
    "w_no_lib": "✖ کتابخانه‌های لازم نصب نیست: pip install pymupdf pillow",
    "w_open_err": "✖ باز نشد: {file} — {err}",
    "w_start": "▶ {file} — صفحات {a} تا {b}",
    "w_zip_done": "✔ ساخته شد: {file} ({n} تصویر)",
    "w_saved": "✔ {n} تصویر ذخیره شد → {dir}",
    "w_file_err": "✖ خطا در {file}: {err}",

    # تنظیمات
    "lbl_out": "پوشه خروجی  📂",
    "btn_choose": "انتخاب",
    "ph_out": "پیش‌فرض: کنار فایل‌های ورودی",
    "sec_naming": "نام‌گذاری",
    "lbl_pattern": "الگوی نام‌گذاری  🏷",
    "row_file": "فایل",
    "row_folder": "پوشه",
    "ph_folder": "{name}  یا  Vol {n}",
    "hint_pattern": "از {name} برای نام خودِ PDF و از {n} برای شماره استفاده کن — مثلاً با نوشتن «Vol {n}» در پوشه، خروجی می‌شود «Vol 001»، «Vol 002» و ....",
    "start_num": "شماره شروع",
    "digits": "تعداد ارقام",
    "continuous": "شماره صفحه‌ی داخل فایل بین همه‌ی PDFها پیوسته باشد",
    "preview": "پیش‌نمایش فایل: {file}   —   پوشه: {folder}",
    "sec_render": "رندر",
    "dpi_title": "رزولوشن رندر  🔎",
    "sec_range": "بازه صفحات",
    "from_title": "از صفحه (۰=اول)",
    "to_title": "تا صفحه (۰=آخر)",
    "sec_help": "راهنما",
    "tip_1": "• اگر ZIP یا CBZ روشن باشد، پوشه‌بندی نادیده گرفته می‌شود و فقط آرشیو با نام الگوی پوشه ساخته می‌شود.",
    "tip_2": "• WEBP و JPG فایل کوچک‌تری می‌سازند؛ PNG و TIFF بدون افت کیفیت‌اند.",
    "tip_3": "• فایل یا پوشه را می‌توانی مستقیم داخل پنجره Drag & Drop کنی.",
    "tip_4": "• رزولوشن بالاتر یعنی جزئیات بیشتر و حجم فایل بیشتر.",

    # درباره
    "about_desc": "تبدیل حرفه‌ای PDF به تصویر — تکی و دسته‌ای",
    "about_engine": "موتور رندر: PyMuPDF  |  ذخیره‌سازی: Pillow",
    "about_formats": "فرمت‌ها: WEBP / JPG / PNG / TIFF / BMP",
    "about_outputs": "خروجی‌ها: تصاویر جدا، ZIP، CBZ",
    "about_dev": "توسعه‌دهنده",
    "btn_github": "🐙  گیت‌هاب",
    "btn_telegram": "✈  کانال تلگرام",
}

EN = {
    "app_name": "PDF Imager",
    "tip_close": "Close",
    "tip_max": "Maximize",
    "tip_min": "Minimize",
    "tip_lang": "Switch to فارسی",
    "color_cyan": "Cyan",
    "color_green": "Green",
    "color_yellow": "Yellow",
    "color_orange": "Orange",
    "color_red": "Red",
    "color_purple": "Purple",
    "color_blue": "Blue",
    "tab_work": "🖼  Home",
    "tab_settings": "⚙  Settings",
    "tab_about": "ℹ  About",

    # Workspace
    "src_empty": "PDF source files",
    "src_many": "{n} PDF files selected (batch mode)",
    "tip_pick_file": "Choose PDF file(s), single or multiple",
    "tip_pick_dir": "Choose a folder (batch mode)",
    "fmt_title": "Output format  🖼",
    "stitch_off": "☰  One image per page",
    "stitch_on": "☰  Stitch pages",
    "gray_off": "✳  Color",
    "gray_on": "✳  Grayscale",
    "btn_cbz": "📦  CBZ output",
    "btn_folder_pdf": "🗂  Per-PDF folder",
    "btn_zip": "🗜  ZIP archive",
    "state_ready": "Ready to start",
    "state_running": "Processing...",
    "state_stopping": "Stopping...",
    "state_done": "Finished — OK: {ok} | Failed: {fail}",
    "progress_page": "{name} • page {page}",
    "btn_start": "🚀  Start",
    "btn_stop": "⛔  Stop",
    "log_done": "■ Done. Output in: {out}",

    # Messages and dialogs
    "warn_empty_title": "Empty",
    "warn_empty_body": "No PDF files were found in this folder.",
    "warn_nofile_title": "No files selected",
    "warn_nofile_body": "Please choose a PDF file or a folder first.",
    "err_lib_title": "Missing libraries",
    "err_lib_body": "Please install:\n\npip install pymupdf pillow",
    "dlg_pick_pdf": "Choose PDF file",
    "dlg_pick_dir": "Choose a folder containing PDFs",
    "dlg_out": "Output folder",
    "filter_pdf": "PDF Files (*.pdf)",

    # Job log (worker thread)
    "w_no_lib": "✖ Required libraries are missing: pip install pymupdf pillow",
    "w_open_err": "✖ Could not open: {file} — {err}",
    "w_start": "▶ {file} — pages {a} to {b}",
    "w_zip_done": "✔ Created: {file} ({n} images)",
    "w_saved": "✔ {n} images saved → {dir}",
    "w_file_err": "✖ Error in {file}: {err}",

    # Settings
    "lbl_out": "Output folder  📂",
    "btn_choose": "Browse",
    "ph_out": "Default: next to the source files",
    "sec_naming": "Naming",
    "lbl_pattern": "Naming pattern  🏷",
    "row_file": "File",
    "row_folder": "Folder",
    "ph_folder": "{name}  or  Vol {n}",
    "hint_pattern": "Use {name} for the PDF's own name and {n} for the number. For example, writing «Vol {n}» as the folder gives «Vol 001», «Vol 002», and so on.",
    "start_num": "Start number",
    "digits": "Digits",
    "continuous": "Keep page numbers continuous across all PDFs",
    "preview": "Preview — file: {file}   —   folder: {folder}",
    "sec_render": "Rendering",
    "dpi_title": "Render resolution  🔎",
    "sec_range": "Page range",
    "from_title": "From page (0 = first)",
    "to_title": "To page (0 = last)",
    "sec_help": "Help",
    "tip_1": "• If ZIP or CBZ is on, per-PDF folders are ignored and only an archive named by the folder pattern is created.",
    "tip_2": "• WEBP and JPG make smaller files; PNG and TIFF are lossless.",
    "tip_3": "• You can drag a file or folder straight into the window.",
    "tip_4": "• Higher resolution means more detail and a larger file.",

    # About
    "about_desc": "Professional PDF to image conversion — single and batch",
    "about_engine": "Render engine: PyMuPDF  |  Saving: Pillow",
    "about_formats": "Formats: WEBP / JPG / PNG / TIFF / BMP",
    "about_outputs": "Outputs: separate images, ZIP, CBZ",
    "about_dev": "Developer",
    "btn_github": "🐙  GitHub",
    "btn_telegram": "✈  Telegram channel",
}

STRINGS = {"fa": FA, "en": EN}
_BINDINGS = []  # توابعی که متن ویجت‌ها را با زبان فعلی دوباره می‌نویسند


def direction():
    return Qt.RightToLeft if LANG == "fa" else Qt.LeftToRight


def T(key, **kw):
    text = STRINGS[LANG].get(key) or STRINGS["en"].get(key) or key
    return text.format(**kw) if kw else text


def bind(fn):
    """fn را ثبت می‌کند و همین الان اجرا می‌کند؛ با عوض شدن زبان دوباره اجرا می‌شود."""
    _BINDINGS.append(fn)
    fn()
    return fn


def tx(widget, key, method="setText", **kw):
    bind(lambda: getattr(widget, method)(T(key, **kw)))
    return widget


def repolish(w):
    w.style().unpolish(w)
    w.style().polish(w)
    w.update()


# ----------------------------------------------------------------------------
# تم رنگی
# ----------------------------------------------------------------------------
ACCENTS = {
    "cyan":   ("#22c3e6", "#2b7fff"),
    "green":  ("#2bd98a", "#12a6a6"),
    "yellow": ("#f6c945", "#f08a24"),
    "orange": ("#ff9f43", "#ff5e62"),
    "red":    ("#ff5f6d", "#c0392b"),
    "purple": ("#a06bff", "#5b5bff"),
    "blue":   ("#3aa0ff", "#1f5cff"),
}

THEME = {
    "bg": "#070d18",
    "panel": "#0d1524",
    "card": "#111b2e",
    "card2": "#0c1423",
    "border": "#1d2b45",
    "text": "#e7eefb",
    "muted": "#7f90ad",
    "accent": "#22c3e6",
    "accent2": "#2b7fff",
}


def stylesheet(theme: dict) -> str:
    t = theme
    return f"""
    * {{ font-family: {FONTS[LANG]}; }}
    #root {{ background: {t['bg']}; border: 1px solid {t['border']}; border-radius: 16px; }}
    #titlebar {{ background: #0a1220; border-top-left-radius: 16px; border-top-right-radius: 16px; }}
    QLabel {{ color: {t['text']}; }}
    QLabel#title {{ color: {t['text']}; font-size: 17px; font-weight: 700; }}
    QLabel#logo {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {t['accent2']}, stop:1 {t['accent']});
        border-radius: 12px; font-size: 18px;
    }}
    QLabel#clock {{ color: {t['accent']}; font-size: 14px; font-weight: 700; }}
    QLabel#dot {{ color: {t['accent']}; font-size: 14px; }}
    QLabel#preview {{ color: {t['accent']}; font-size: 12px; font-weight: 700; }}
    QLabel#state {{ color: {t['text']}; font-size: 13px; }}
    QLabel#srcEmpty {{ color: {t['muted']}; font-size: 13px; }}
    QLabel#srcSet {{ color: {t['text']}; font-size: 13px; font-weight: 600; }}
    QLabel#devName {{ color: {t['accent']}; font-size: 20px; font-weight: 800; }}

    #card {{ background: {t['card']}; border: 1px solid {t['border']}; border-radius: 14px; }}
    #cardActive {{ background: {t['card']}; border: 1px solid {t['accent']}; border-radius: 14px; }}
    #inner {{ background: {t['card2']}; border: 1px solid {t['border']}; border-radius: 10px; }}
    #tabbar {{ background: {t['panel']}; border: 1px solid {t['border']}; border-radius: 14px; }}

    QPushButton#tab {{
        background: transparent; color: {t['muted']}; border: none;
        border-radius: 10px; padding: 10px 12px; font-size: 14px; font-weight: 600;
    }}
    QPushButton#tab:hover {{ color: {t['text']}; }}
    QPushButton#tab:checked {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {t['card']}, stop:1 {t['card2']});
        color: {t['text']}; border: 1px solid {t['border']};
    }}

    QPushButton#ghost {{
        background: {t['card2']}; color: {t['text']}; border: 1px solid {t['border']};
        border-radius: 10px; padding: 9px 12px; font-size: 13px;
    }}
    QPushButton#ghost:hover {{ border-color: {t['accent']}; color: {t['accent']}; }}
    QPushButton#ghost:checked {{ border-color: {t['accent']}; color: {t['accent']}; background: rgba(34,195,230,0.08); }}

    QPushButton#icon {{
        background: {t['card2']}; border: 1px solid {t['border']};
        border-radius: 10px; color: {t['text']}; font-size: 15px;
    }}
    QPushButton#icon:hover {{ border-color: {t['accent']}; }}

    QPushButton#lang {{
        background: {t['card']}; color: {t['text']}; border: 1px solid {t['border']};
        border-radius: 8px; padding: 2px 8px; font-size: 11px; font-weight: 700;
    }}
    QPushButton#lang:hover {{ border-color: {t['accent']}; color: {t['accent']}; }}

    QPushButton#primary {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {t['accent2']}, stop:1 {t['accent']});
        color: #04121c; border: none; border-radius: 14px;
        font-size: 16px; font-weight: 800; padding: 15px;
    }}
    QPushButton#primary:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {t['accent']}, stop:1 {t['accent2']}); }}
    QPushButton#primary:disabled {{ background: #1a2236; color: #55637d; }}

    QPushButton#danger {{
        background: rgba(255,95,109,0.12); color: #ff8d95;
        border: 1px solid rgba(255,95,109,0.45); border-radius: 14px;
        font-size: 15px; font-weight: 700; padding: 15px;
    }}
    QPushButton#danger:hover {{ background: rgba(255,95,109,0.2); }}

    QPushButton#win, QPushButton#winClose {{
        background: transparent; border: none; color: {t['muted']}; font-size: 14px; border-radius: 6px;
    }}
    QPushButton#win:hover {{ background: #16203a; color: {t['text']}; }}
    QPushButton#winClose:hover {{ background: #c0392b; color: white; }}

    QLineEdit, QSpinBox, QComboBox {{
        background: transparent; border: none; color: {t['text']};
        font-size: 20px; font-weight: 700; padding: 4px;
    }}
    QLineEdit#path {{ font-size: 13px; font-weight: 500; color: {t['text']}; }}
    QComboBox {{ font-size: 15px; }}
    QComboBox::drop-down {{ border: none; width: 22px; }}
    QComboBox QAbstractItemView {{
        background: {t['card']}; color: {t['text']}; border: 1px solid {t['border']};
        selection-background-color: {t['accent']}; selection-color: #04121c; outline: none; padding: 4px;
    }}
    QSpinBox::up-button, QSpinBox::down-button {{ width: 0px; border: none; }}

    QProgressBar {{
        background: {t['card2']}; border: 1px solid {t['border']}; border-radius: 8px;
    }}
    QProgressBar::chunk {{
        border-radius: 7px;
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {t['accent2']}, stop:1 {t['accent']});
    }}

    QTextEdit {{
        background: {t['card2']}; border: 1px solid {t['border']}; border-radius: 10px;
        color: {t['muted']}; font-size: 12px; padding: 8px;
    }}
    QScrollArea {{ background: transparent; border: none; }}
    QScrollBar:vertical {{ background: transparent; width: 8px; margin: 2px; }}
    QScrollBar::handle:vertical {{ background: {t['border']}; border-radius: 4px; min-height: 30px; }}
    QScrollBar::handle:vertical:hover {{ background: {t['accent']}; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0px; }}
    """


# ----------------------------------------------------------------------------
# ویجت‌های کمکی
# ----------------------------------------------------------------------------
class Toggle(QCheckBox):
    """سوییچ روشن/خاموش استایل‌دار"""

    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(46, 26)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        on = self.isChecked()
        bg = QColor(THEME["accent"]) if on else QColor("#2a3550")
        p.setBrush(bg)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 3, 46, 20, 10, 10)
        p.setBrush(QColor("#ffffff" if on else "#8c9bb8"))
        x = 26 if on else 3
        p.drawEllipse(QPoint(x + 8, 13), 9, 9)
        p.end()


class Card(QFrame):
    def __init__(self, parent=None, active=False):
        super().__init__(parent)
        self.setObjectName("cardActive" if active else "card")

    def set_active(self, active: bool):
        self.setObjectName("cardActive" if active else "card")
        repolish(self)


def label(key, size=12, color=None, bold=False, wrap=False):
    """برچسب متنی؛ key می‌تواند کلید ترجمه یا یک متن ثابت (مثل ایموجی) باشد."""
    lb = QLabel()
    lb.setStyleSheet(f"color:{color or THEME['muted']}; font-size:{size}px; "
                     f"font-weight:{700 if bold else 500};")
    lb.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # در RTL خودکار به راست می‌رود
    lb.setWordWrap(wrap)
    return tx(lb, key)


def input_box(widget, unit=""):
    """قاب ورودی: خود ورودی کشیده می‌شود و واحد در انتهای قاب قرار می‌گیرد."""
    box = QFrame()
    box.setObjectName("inner")
    il = QHBoxLayout(box)
    il.setContentsMargins(12, 6, 12, 6)
    il.setSpacing(8)
    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    widget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    il.addWidget(widget, 1)
    if unit:
        il.addWidget(label(unit, 11))
    return box


def field_card(title_key, widget, unit="", active=False):
    """کارت ورودی عددی: عنوان بالا، ورودی و واحد پایین"""
    card = Card(active=active)
    lay = QVBoxLayout(card)
    lay.setContentsMargins(14, 12, 14, 14)
    lay.setSpacing(8)
    lay.addWidget(label(title_key, 12))
    lay.addWidget(input_box(widget, unit))
    return card


def section_box(title_key):
    """بخش تنظیمات: یک تیتر بولد و محتوای زیرش (بدون کارت بیرونی تا حاشیه‌ها دوتایی نشوند)."""
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(10)
    lay.addWidget(label(title_key, 14, THEME["text"], True))
    return box, lay


def pattern_row(label_key, placeholder):
    row = QFrame()
    row.setObjectName("inner")
    rl = QHBoxLayout(row)
    rl.setContentsMargins(12, 6, 12, 6)
    rl.setSpacing(10)
    lb = label(label_key, 11)
    lb.setMinimumWidth(56)  # تا ستون «فایل» و «پوشه» هم‌تراز باشند
    ed = QLineEdit()
    ed.setObjectName("path")
    tx(ed, placeholder, "setPlaceholderText")
    rl.addWidget(lb)
    rl.addWidget(ed, 1)
    return row, ed


def ghost(key, checkable=False):
    b = QPushButton()
    b.setObjectName("ghost")
    b.setCheckable(checkable)
    b.setCursor(Qt.PointingHandCursor)
    return tx(b, key)


def flip_button(key_off, key_on):
    """دکمه‌ی روشن/خاموش که متنش با وضعیت عوض می‌شود"""
    b = QPushButton()
    b.setObjectName("ghost")
    b.setCheckable(True)
    b.setCursor(Qt.PointingHandCursor)

    def upd():
        b.setText(T(key_on) if b.isChecked() else T(key_off))

    bind(upd)
    b.toggled.connect(lambda *_: upd())
    return b


def icon_btn(text, tip_key, slot):
    b = QPushButton(text)
    b.setObjectName("icon")
    b.setFixedSize(46, 46)
    b.setCursor(Qt.PointingHandCursor)
    tx(b, tip_key, "setToolTip")
    b.clicked.connect(slot)
    return b


def short(text, n=40):
    return text if len(text) <= n else text[: n - 1] + "…"


# ----------------------------------------------------------------------------
# تنظیمات تبدیل
# ----------------------------------------------------------------------------
@dataclass
class Options:
    files: List[str] = field(default_factory=list)
    out_dir: str = ""
    fmt: str = "WEBP"
    quality: int = 90
    dpi: int = 200
    use_width: bool = True
    width: int = 800
    split_height: int = 0          # 0 = بدون برش
    stitch: bool = False           # دوخت همه صفحات در یک تصویر بلند
    grayscale: bool = False
    zip_out: bool = False
    cbz_out: bool = False
    subfolder: bool = True         # هر PDF در پوشه‌ی خودش
    page_from: int = 0             # 0 = از اول
    page_to: int = 0               # 0 = تا آخر
    # --- نام‌گذاری (الگو با {name} و {n}) ---
    file_pattern: str = "{name}_{n}"
    folder_pattern: str = "{name}"
    pad: int = 3                   # تعداد ارقام شماره: 001 / 0001
    start: int = 1                 # شماره شروع
    continuous: bool = False       # شماره‌ی صفحات پیوسته بین همه فایل‌ها


EXT = {"WEBP": ".webp", "JPG": ".jpg", "PNG": ".png", "TIFF": ".tif", "BMP": ".bmp"}
PIL_FMT = {"WEBP": "WEBP", "JPG": "JPEG", "PNG": "PNG", "TIFF": "TIFF", "BMP": "BMP"}


def clean_doc_name(name: str) -> str:
    """حذف برچسب‌های ابتدای نام فایل، مثل [MangaIsland]-، از نام خروجی."""
    cleaned = re.sub(r"^(?:\s*\[[^\]]+\]\s*[-_ ]*\s*)+", "", name)
    return cleaned.strip() or name


# ----------------------------------------------------------------------------
# موتور تبدیل (ترد جدا)
# ----------------------------------------------------------------------------
class Worker(QThread):
    progress = Signal(int, int, str, int)  # done, total, name, page
    log = Signal(str)
    done = Signal(int, int, str)           # ok_files, fail_files, out_dir

    def __init__(self, opt: Options):
        super().__init__()
        self.opt = opt
        self._stop = False

    def stop(self):
        self._stop = True

    def _save(self, img, path):
        o = self.opt
        f = PIL_FMT[o.fmt]
        if f in ("JPEG", "BMP") and img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        params = {}
        if f == "JPEG":
            params = dict(quality=o.quality, subsampling=0 if o.quality >= 95 else 2, optimize=True)
        elif f == "WEBP":
            if o.quality >= 100:
                params = dict(lossless=True, quality=100, method=5)
            else:
                params = dict(quality=o.quality, method=5)
        elif f == "PNG":
            params = dict(optimize=True, compress_level=6)
        elif f == "TIFF":
            params = dict(compression="tiff_lzw")
        img.save(path, f, **params)

    def _render(self, page) -> "Image.Image":
        o = self.opt
        if o.use_width and o.width > 0:
            base = page.rect.width or 1
            zoom = o.width / base
        else:
            zoom = o.dpi / 72.0
        zoom = max(0.05, min(zoom, 12.0))
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        if o.use_width and o.width > 0 and img.width != o.width:
            h = max(1, round(img.height * o.width / img.width))
            img = img.resize((o.width, h), Image.LANCZOS)
        if o.grayscale:
            img = img.convert("L").convert("RGB")
        return img

    def _filename(self, doc_name: str, num: int, part: int = 1, parts: int = 1) -> str:
        """ساخت نام فایل خروجی از روی الگو (پلیس‌هولدرهای {name} و {n})"""
        o = self.opt
        core = f"{num:0{max(1, o.pad)}d}"
        try:
            base = o.file_pattern.format(name=doc_name, n=core)
        except (KeyError, IndexError, ValueError):
            base = f"{doc_name}_{core}"
        if parts > 1:
            base += f"_{part}"
        return base + EXT[o.fmt]

    def _folder_name(self, doc_name: str, file_index: int, total_files: int) -> str:
        """ساخت نام پوشه/آرشیو از روی الگو؛ اگر الگو {name} یا {n} نداشته باشد،
        در حالت دسته‌ای نام PDF به انتهایش اضافه می‌شود تا تداخلی پیش نیاید."""
        o = self.opt
        core = f"{o.start + file_index - 1:0{max(1, o.pad)}d}"
        pattern = o.folder_pattern.strip() or "{name}"
        try:
            name = pattern.format(name=doc_name, n=core)
        except (KeyError, IndexError, ValueError):
            name = doc_name
        if total_files > 1 and "{n}" not in pattern and "{name}" not in pattern:
            name = f"{name}_{doc_name}"
        return name

    def _slice(self, img, max_h: int):
        if max_h <= 0 or img.height <= max_h:
            return [img]
        parts, y = [], 0
        while y < img.height:
            h = min(max_h, img.height - y)
            parts.append(img.crop((0, y, img.width, y + h)))
            y += h
        return parts

    def run(self):
        o = self.opt
        if fitz is None or Image is None:
            self.log.emit(T("w_no_lib"))
            self.done.emit(0, len(o.files), o.out_dir)
            return

        # شمارش کل صفحات برای نوار پیشرفت
        total = 0
        counts = {}
        for f in o.files:
            try:
                with fitz.open(f) as d:
                    n = d.page_count
                    a = max(1, o.page_from or 1)
                    b = min(n, o.page_to or n)
                    counts[f] = (a, b)
                    total += max(0, b - a + 1)
            except Exception as e:
                counts[f] = None
                self.log.emit(T("w_open_err", file=os.path.basename(f), err=e))
        total = max(total, 1)

        done_pages, ok, fail = 0, 0, 0
        counter = o.start
        total_files = len(o.files)

        for idx, src in enumerate(o.files, start=1):
            if self._stop:
                break
            name = clean_doc_name(os.path.splitext(os.path.basename(src))[0])
            rng = counts.get(src)
            if rng is None:
                fail += 1
                continue

            folder_name = self._folder_name(name, idx, total_files)
            target = (os.path.join(o.out_dir, folder_name)
                      if (o.subfolder and not (o.zip_out or o.cbz_out)) else o.out_dir)
            tmp_dir = (os.path.join(o.out_dir, f".__{folder_name}__tmp")
                       if (o.zip_out or o.cbz_out) else target)
            os.makedirs(tmp_dir, exist_ok=True)

            made: List[str] = []
            if not o.continuous:
                counter = o.start
            try:
                with fitz.open(src) as doc:
                    a, b = rng
                    self.log.emit(T("w_start", file=os.path.basename(src), a=a, b=b))

                    if o.stitch:
                        imgs = []
                        for i in range(a - 1, b):
                            if self._stop:
                                break
                            imgs.append(self._render(doc[i]))
                            done_pages += 1
                            self.progress.emit(done_pages, total, name, i + 1)
                        if imgs:
                            w = max(im.width for im in imgs)
                            imgs = [im if im.width == w else
                                    im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
                                    for im in imgs]
                            big = Image.new("RGB", (w, sum(im.height for im in imgs)), "white")
                            y = 0
                            for im in imgs:
                                big.paste(im, (0, y))
                                y += im.height
                            for part in self._slice(big, o.split_height):
                                p = os.path.join(tmp_dir, self._filename(name, counter))
                                self._save(part, p)
                                made.append(p)
                                counter += 1
                    else:
                        for i in range(a - 1, b):
                            if self._stop:
                                break
                            img = self._render(doc[i])
                            parts = self._slice(img, o.split_height)
                            for k, part in enumerate(parts, 1):
                                p = os.path.join(tmp_dir, self._filename(name, counter, k, len(parts)))
                                self._save(part, p)
                                made.append(p)
                            counter += 1
                            done_pages += 1
                            self.progress.emit(done_pages, total, name, i + 1)

                # بسته‌بندی
                if made and (o.zip_out or o.cbz_out):
                    ext = ".cbz" if o.cbz_out else ".zip"
                    arc = os.path.join(o.out_dir, folder_name + ext)
                    with zipfile.ZipFile(arc, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
                        for p in sorted(made):
                            z.write(p, os.path.basename(p))
                    for p in made:
                        try:
                            os.remove(p)
                        except OSError:
                            pass
                    try:
                        os.rmdir(tmp_dir)
                    except OSError:
                        pass
                    self.log.emit(T("w_zip_done", file=os.path.basename(arc), n=len(made)))
                else:
                    self.log.emit(T("w_saved", n=len(made), dir=tmp_dir))
                ok += 1
            except Exception as e:
                fail += 1
                self.log.emit(T("w_file_err", file=os.path.basename(src), err=e))
                self.log.emit(traceback.format_exc(limit=2))

        self.done.emit(ok, fail, o.out_dir)


# ----------------------------------------------------------------------------
# نوار عنوان (با کشیدن آن پنجره جابه‌جا می‌شود)
# ----------------------------------------------------------------------------
class TitleBar(QFrame):
    def __init__(self, win):
        super().__init__()
        self._win = win
        self._drag = None

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = e.globalPosition().toPoint() - self._win.frameGeometry().topLeft()
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self._drag is not None and (e.buttons() & Qt.LeftButton) and not self._win.isMaximized():
            self._win.move(e.globalPosition().toPoint() - self._drag)
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        self._drag = None
        super().mouseReleaseEvent(e)


# ----------------------------------------------------------------------------
# پنجره اصلی
# ----------------------------------------------------------------------------
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.files: List[str] = []
        self.out_dir = ""
        self.worker: Optional[Worker] = None
        self.t0 = 0.0
        self._running = False
        self._state = ("state_ready", {})

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setLayoutDirection(direction())
        self.resize(520, 800)
        self.setAcceptDrops(True)
        bind(lambda: self.setWindowTitle(f"{T('app_name')} - {APP_VER}"))

        root = QFrame()
        root.setObjectName("root")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self._titlebar())

        body = QWidget()
        outer.addWidget(body, 1)
        v = QVBoxLayout(body)
        v.setContentsMargins(16, 10, 16, 16)
        v.setSpacing(12)

        v.addWidget(self._tabbar())
        self.stack = QStackedWidget()
        self.stack.addWidget(self._page_work())
        self.stack.addWidget(self._page_settings())
        self.stack.addWidget(self._page_about())
        v.addWidget(self.stack, 1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

        self.apply_theme()

    # -- نوار عنوان ----------------------------------------------------------
    def _titlebar(self):
        bar = TitleBar(self)
        bar.setObjectName("titlebar")
        bar.setFixedHeight(56)
        h = QHBoxLayout(bar)
        h.setContentsMargins(12, 0, 12, 0)
        h.setSpacing(6)

        logo = QLabel("📄")
        logo.setObjectName("logo")
        logo.setFixedSize(36, 36)
        logo.setAlignment(Qt.AlignCenter)
        title = QLabel()
        title.setObjectName("title")
        tx(title, "app_name")
        h.addWidget(logo)
        h.addWidget(title)
        h.addStretch()

        # نقطه‌های تغییر رنگ تم
        self.dots = []
        for key, (c1, _) in ACCENTS.items():
            d = QPushButton()
            d.setFixedSize(14, 14)
            d.setCursor(Qt.PointingHandCursor)
            d.setStyleSheet(f"background:{c1};border:none;border-radius:7px;")
            tx(d, f"color_{key}", "setToolTip")
            d.clicked.connect(lambda _=False, k=key: self.set_accent(k))
            h.addWidget(d)
            self.dots.append(d)

        # دکمه‌ی تغییر زبان
        h.addSpacing(6)
        self.btn_lang = QPushButton()
        self.btn_lang.setObjectName("lang")
        self.btn_lang.setCursor(Qt.PointingHandCursor)
        self.btn_lang.setFixedHeight(24)
        tx(self.btn_lang, "tip_lang", "setToolTip")
        bind(lambda: self.btn_lang.setText("EN" if LANG == "fa" else "فا"))
        self.btn_lang.clicked.connect(self.toggle_lang)
        h.addWidget(self.btn_lang)

        # دکمه‌های پنجره
        h.addSpacing(4)
        mn = QPushButton("—")
        mn.setObjectName("win")
        tx(mn, "tip_min", "setToolTip")
        mx = QPushButton("▢")
        mx.setObjectName("win")
        tx(mx, "tip_max", "setToolTip")
        cl = QPushButton("✕")
        cl.setObjectName("winClose")
        tx(cl, "tip_close", "setToolTip")
        mn.clicked.connect(self.showMinimized)
        mx.clicked.connect(self._toggle_max)
        cl.clicked.connect(self.close)
        for b in (mn, mx, cl):
            b.setFixedSize(28, 28)
            b.setCursor(Qt.PointingHandCursor)
            h.addWidget(b)
        return bar

    def _toggle_max(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # -- تب‌ها ---------------------------------------------------------------
    def _tabbar(self):
        bar = QFrame()
        bar.setObjectName("tabbar")
        h = QHBoxLayout(bar)
        h.setContentsMargins(6, 6, 6, 6)
        h.setSpacing(4)
        self.tabs = QButtonGroup(self)
        for i, key in enumerate(("tab_work", "tab_settings", "tab_about")):
            b = QPushButton()
            b.setObjectName("tab")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            tx(b, key)
            b.clicked.connect(lambda _=False, idx=i: self.stack.setCurrentIndex(idx))
            self.tabs.addButton(b, i)
            h.addWidget(b, 1)
        self.tabs.button(0).setChecked(True)
        return bar

    # -- وضعیت و دکمه‌ی شروع (متن‌ها با زبان عوض می‌شوند) -------------------
    def _set_state(self, key, **kw):
        self._state = (key, kw)
        self._refresh_state()

    def _refresh_state(self):
        key, kw = self._state
        self.lbl_state.setText(T(key, **kw))

    def _refresh_go(self):
        self.btn_go.setText(T("btn_stop") if self._running else T("btn_start"))
        self.btn_go.setObjectName("danger" if self._running else "primary")
        repolish(self.btn_go)

    def _refresh_src(self):
        n = len(self.files)
        if n == 0:
            text, obj = T("src_empty"), "srcEmpty"
            tip = ""
        elif n == 1:
            text, obj = short(os.path.basename(self.files[0])), "srcSet"
            tip = self.files[0]
        else:
            text, obj = T("src_many", n=n), "srcSet"
            tip = ""
        self.lbl_src.setText(text)
        self.lbl_src.setToolTip(tip)
        self.lbl_src.setObjectName(obj)
        repolish(self.lbl_src)

    # -- صفحه میز کار --------------------------------------------------------
    def _page_work(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(12)

        # منبع
        src = Card()
        sl = QHBoxLayout(src)
        sl.setContentsMargins(12, 12, 12, 12)
        sl.setSpacing(8)
        sl.addWidget(icon_btn("📄", "tip_pick_file", self.pick_files))
        sl.addWidget(icon_btn("📁", "tip_pick_dir", self.pick_folder))
        sl.addStretch()
        self.lbl_src = QLabel()
        self.lbl_src.setObjectName("srcEmpty")
        bind(self._refresh_src)
        sl.addWidget(self.lbl_src)
        sl.addWidget(label("📥", 15))
        v.addWidget(src)

        # پوشه خروجی
        out_card = Card()
        ol = QVBoxLayout(out_card)
        ol.setContentsMargins(14, 12, 14, 12)
        ol.setSpacing(8)
        ol.addWidget(label("lbl_out", 12))
        orow = QHBoxLayout()
        orow.setSpacing(8)
        self.ed_out = QLineEdit()
        self.ed_out.setObjectName("path")
        tx(self.ed_out, "ph_out", "setPlaceholderText")
        orow.addWidget(input_box(self.ed_out), 1)
        b_out = ghost("btn_choose")
        b_out.clicked.connect(self.pick_out)
        orow.addWidget(b_out)
        ol.addLayout(orow)
        v.addWidget(out_card)

        # فرمت خروجی
        self.cb_fmt = QComboBox()
        self.cb_fmt.addItems(["WEBP", "JPG", "PNG", "TIFF", "BMP"])
        self.cb_fmt.setCursor(Qt.PointingHandCursor)
        fmt_card = Card()
        fl = QVBoxLayout(fmt_card)
        fl.setContentsMargins(14, 12, 14, 14)
        fl.setSpacing(8)
        fl.addWidget(label("fmt_title", 12))
        fin = QFrame()
        fin.setObjectName("inner")
        fil = QHBoxLayout(fin)
        fil.setContentsMargins(12, 6, 12, 6)
        fil.setSpacing(8)
        self.cb_fmt.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        fil.addWidget(self.cb_fmt, 1)
        self.dot_fmt = QLabel("●")
        self.dot_fmt.setObjectName("dot")
        fil.addWidget(self.dot_fmt)
        fl.addWidget(fin)

        v.addWidget(fmt_card)

        # حالت‌ها
        row3 = QHBoxLayout()
        row3.setSpacing(10)
        self.btn_stitch = flip_button("stitch_off", "stitch_on")
        self.btn_gray = flip_button("gray_off", "gray_on")
        row3.addWidget(self.btn_stitch, 1)
        row3.addWidget(self.btn_gray, 1)
        v.addLayout(row3)

        # بسته‌بندی خروجی
        pack = Card()
        pl = QHBoxLayout(pack)
        pl.setContentsMargins(12, 10, 12, 10)
        pl.setSpacing(6)
        self.btn_cbz = ghost("btn_cbz", True)
        self.btn_pdf_sub = ghost("btn_folder_pdf", True)
        self.btn_pdf_sub.setChecked(True)
        self.btn_zip = ghost("btn_zip", True)
        for b in (self.btn_cbz, self.btn_pdf_sub, self.btn_zip):
            pl.addWidget(b, 1)
        self.btn_zip.toggled.connect(lambda on: on and self.btn_cbz.setChecked(False))
        self.btn_cbz.toggled.connect(lambda on: on and self.btn_zip.setChecked(False))
        v.addWidget(pack)

        # وضعیت و پیشرفت
        st = Card()
        stl = QVBoxLayout(st)
        stl.setContentsMargins(14, 12, 14, 12)
        stl.setSpacing(8)
        top = QHBoxLayout()
        self.lbl_time = QLabel("00:00:00")
        self.lbl_time.setObjectName("clock")
        top.addWidget(self.lbl_time)
        top.addStretch()
        self.lbl_state = QLabel()
        self.lbl_state.setObjectName("state")
        bind(self._refresh_state)
        top.addWidget(self.lbl_state)
        top.addWidget(label("●", 13))
        stl.addLayout(top)
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setFixedHeight(10)
        self.bar.setTextVisible(False)
        stl.addWidget(self.bar)
        v.addWidget(st)

        # گزارش
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(90)
        v.addWidget(self.log, 1)

        # دکمه شروع / توقف
        self.btn_go = QPushButton()
        self.btn_go.setObjectName("primary")
        self.btn_go.setCursor(Qt.PointingHandCursor)
        self.btn_go.clicked.connect(self.start)
        bind(self._refresh_go)
        v.addWidget(self.btn_go)
        return page

    # -- صفحه تنظیمات --------------------------------------------------------
    def _page_settings(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.viewport().setAutoFillBackground(False)  # تا زمینه‌ی روشن پشت صفحه نماند

        page = QWidget()
        scroll.setWidget(page)
        # QScrollArea.setWidget خودش autoFill محتوا را روشن می‌کند و آن را با رنگ روشنِ پالت پر می‌کند.
        # باید همین‌جا خاموش شود، وگرنه زمینه‌ی تیرهٔ پنجره پشت تنظیمات دیده نمی‌شود.
        page.setAutoFillBackground(False)
        v = QVBoxLayout(page)
        v.setContentsMargins(6, 0, 6, 0)
        v.setSpacing(20)

        # ── نام‌گذاری ──
        box, lay = section_box("sec_naming")
        lay.addWidget(label("lbl_pattern", 12))
        row_f, self.ed_file_pattern = pattern_row("row_file", "{name}_{n}")
        self.ed_file_pattern.setText("{name}_{n}")
        row_d, self.ed_folder_pattern = pattern_row("row_folder", "ph_folder")
        self.ed_folder_pattern.setText("{name}")
        lay.addWidget(row_f)
        lay.addWidget(row_d)
        lay.addWidget(label("hint_pattern", 11, wrap=True))

        nrow = QHBoxLayout()
        nrow.setSpacing(10)
        self.sp_start = QSpinBox()
        self.sp_start.setRange(0, 99999)
        self.sp_start.setValue(1)
        self.sp_start.setButtonSymbols(QSpinBox.NoButtons)
        self.sp_pad = QSpinBox()
        self.sp_pad.setRange(1, 6)
        self.sp_pad.setValue(3)
        self.sp_pad.setButtonSymbols(QSpinBox.NoButtons)
        nrow.addWidget(field_card("start_num", self.sp_start), 1)
        nrow.addWidget(field_card("digits", self.sp_pad, "#"), 1)
        lay.addLayout(nrow)

        crow = QHBoxLayout()
        crow.setSpacing(10)
        self.tg_cont = Toggle(False)
        crow.addWidget(self.tg_cont, 0, Qt.AlignTop)
        crow.addWidget(label("continuous", 12, wrap=True), 1)
        lay.addLayout(crow)

        self.lbl_preview = QLabel()
        self.lbl_preview.setObjectName("preview")
        self.lbl_preview.setWordWrap(True)
        self.lbl_preview.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lay.addWidget(self.lbl_preview)

        for w in (self.ed_file_pattern, self.ed_folder_pattern):
            w.textChanged.connect(lambda *_: self._update_preview())
        self.cb_fmt.currentIndexChanged.connect(lambda *_: self._update_preview())
        self.sp_start.valueChanged.connect(lambda *_: self._update_preview())
        self.sp_pad.valueChanged.connect(lambda *_: self._update_preview())
        bind(self._update_preview)
        v.addWidget(box)

        # ── رندر ──
        box, lay = section_box("sec_render")
        self.sp_dpi = QSpinBox()
        self.sp_dpi.setRange(36, 1200)
        self.sp_dpi.setValue(200)
        self.sp_dpi.setButtonSymbols(QSpinBox.NoButtons)
        lay.addWidget(field_card("dpi_title", self.sp_dpi, "DPI"))
        v.addWidget(box)

        # ── بازه صفحات ──
        box, lay = section_box("sec_range")
        rng = QHBoxLayout()
        rng.setSpacing(10)
        self.sp_from = QSpinBox()
        self.sp_from.setRange(0, 99999)
        self.sp_from.setValue(0)
        self.sp_from.setButtonSymbols(QSpinBox.NoButtons)
        self.sp_to = QSpinBox()
        self.sp_to.setRange(0, 99999)
        self.sp_to.setValue(0)
        self.sp_to.setButtonSymbols(QSpinBox.NoButtons)
        rng.addWidget(field_card("from_title", self.sp_from), 1)
        rng.addWidget(field_card("to_title", self.sp_to), 1)
        lay.addLayout(rng)
        v.addWidget(box)

        # ── راهنما ──
        box, lay = section_box("sec_help")
        tip = Card()
        tl = QVBoxLayout(tip)
        tl.setContentsMargins(14, 12, 14, 14)
        tl.setSpacing(6)
        for k in ("tip_1", "tip_2", "tip_3", "tip_4"):
            tl.addWidget(label(k, 12, wrap=True))
        lay.addWidget(tip)
        v.addWidget(box)

        v.addStretch()
        return scroll

    def _update_preview(self):
        num = f"{self.sp_start.value():0{self.sp_pad.value()}d}"
        ext = EXT[self.cb_fmt.currentText()]
        doc = clean_doc_name(os.path.splitext(os.path.basename(self.files[0]))[0]) if self.files else "MyFile"

        fpat = self.ed_file_pattern.text().strip() or "{name}_{n}"
        try:
            fname = fpat.format(name=doc, n=num) + ext
        except (KeyError, IndexError, ValueError):
            fname = f"{doc}_{num}{ext}"

        dpat = self.ed_folder_pattern.text().strip() or "{name}"
        try:
            dname = dpat.format(name=doc, n=num)
        except (KeyError, IndexError, ValueError):
            dname = doc
        if len(self.files) > 1 and "{n}" not in dpat and "{name}" not in dpat:
            dname = f"{dname}_{doc}"

        self.lbl_preview.setText(T("preview", file=fname, folder=dname))

    # -- صفحه درباره ---------------------------------------------------------
    def _page_about(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(12)
        c = Card()
        cl = QVBoxLayout(c)
        cl.setContentsMargins(18, 18, 18, 18)
        cl.setSpacing(10)
        head = QLabel()
        head.setObjectName("title")
        bind(lambda: head.setText(f"{T('app_name')} {APP_VER}"))
        cl.addWidget(head)
        cl.addWidget(label("about_desc", 13, wrap=True))
        cl.addWidget(label("about_engine", 12, wrap=True))
        cl.addWidget(label("about_formats", 12, wrap=True))
        cl.addWidget(label("about_outputs", 12, wrap=True))
        v.addWidget(c)

        # ── توسعه‌دهنده و لینک‌ها ──
        dev = Card()
        dl = QVBoxLayout(dev)
        dl.setContentsMargins(18, 16, 18, 16)
        dl.setSpacing(10)
        dl.addWidget(label("about_dev", 12))
        name = QLabel(DEVELOPER)
        name.setObjectName("devName")
        name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        dl.addWidget(name)
        links = QHBoxLayout()
        links.setSpacing(8)
        for key, url in (("btn_github", GITHUB_URL), ("btn_telegram", TELEGRAM_URL)):
            b = ghost(key)
            b.setToolTip(url)
            b.clicked.connect(lambda _=False, u=url: QDesktopServices.openUrl(QUrl(u)))
            links.addWidget(b, 1)
        dl.addLayout(links)
        v.addWidget(dev)

        v.addStretch()
        return page

    # -- تم و زبان -----------------------------------------------------------
    def set_accent(self, key):
        c1, c2 = ACCENTS[key]
        THEME["accent"], THEME["accent2"] = c1, c2
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(stylesheet(THEME))

    def toggle_lang(self):
        self.set_lang("en" if LANG == "fa" else "fa")

    def set_lang(self, code):
        global LANG
        LANG = code
        QSettings(APP_ID, APP_ID).setValue("lang", code)
        d = direction()
        QApplication.instance().setLayoutDirection(d)
        self.setLayoutDirection(d)
        self.apply_theme()  # فونت هم به زبان جدید عوض می‌شود
        for fn in list(_BINDINGS):
            fn()

    # -- انتخاب فایل ---------------------------------------------------------
    def pick_files(self):
        fs, _ = QFileDialog.getOpenFileNames(self, T("dlg_pick_pdf"), "", T("filter_pdf"))
        if fs:
            self.files = fs
            self._refresh_src()

    def pick_folder(self):
        d = QFileDialog.getExistingDirectory(self, T("dlg_pick_dir"))
        if d:
            fs = []
            for rootd, _, names in os.walk(d):
                fs += [os.path.join(rootd, n) for n in names if n.lower().endswith(".pdf")]
            if not fs:
                QMessageBox.warning(self, T("warn_empty_title"), T("warn_empty_body"))
                return
            self.files = sorted(fs)
            self._refresh_src()

    def pick_out(self):
        d = QFileDialog.getExistingDirectory(self, T("dlg_out"))
        if d:
            self.out_dir = d
            self.ed_out.setText(d)

    # -- Drag & Drop ---------------------------------------------------------
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        fs = []
        for u in e.mimeData().urls():
            p = u.toLocalFile()
            if os.path.isdir(p):
                for rootd, _, names in os.walk(p):
                    fs += [os.path.join(rootd, n) for n in names if n.lower().endswith(".pdf")]
            elif p.lower().endswith(".pdf"):
                fs.append(p)
        if fs:
            self.files = sorted(set(fs))
            self._refresh_src()

    # -- اجرا ----------------------------------------------------------------
    def start(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self._set_state("state_stopping")
            return

        if not self.files:
            QMessageBox.warning(self, T("warn_nofile_title"), T("warn_nofile_body"))
            return
        if fitz is None or Image is None:
            QMessageBox.critical(self, T("err_lib_title"), T("err_lib_body"))
            return

        out = self.ed_out.text().strip() or os.path.dirname(self.files[0])
        os.makedirs(out, exist_ok=True)

        opt = Options(
            files=self.files, out_dir=out,
            fmt=self.cb_fmt.currentText(),
            quality=90,        # کیفیت ثابت برای فرمت‌های lossy
            dpi=self.sp_dpi.value(),
            use_width=False,   # رندر فقط با DPI انجام می‌شود
            width=0,
            split_height=0,    # برش ارتفاعی حذف شده
            stitch=self.btn_stitch.isChecked(),
            grayscale=self.btn_gray.isChecked(),
            zip_out=self.btn_zip.isChecked(),
            cbz_out=self.btn_cbz.isChecked(),
            subfolder=self.btn_pdf_sub.isChecked(),
            page_from=self.sp_from.value(),
            page_to=self.sp_to.value(),
            file_pattern=self.ed_file_pattern.text().strip() or "{name}_{n}",
            folder_pattern=self.ed_folder_pattern.text().strip() or "{name}",
            pad=self.sp_pad.value(),
            start=self.sp_start.value(),
            continuous=self.tg_cont.isChecked(),
        )

        self.log.clear()
        self.bar.setValue(0)
        self.t0 = time.time()
        self.timer.start(500)
        self._running = True
        self._refresh_go()
        self._set_state("state_running")

        self.worker = Worker(opt)
        self.worker.progress.connect(self.on_progress)
        self.worker.log.connect(self.log.append)
        self.worker.done.connect(self.on_done)
        self.worker.start()

    def on_progress(self, done, total, name, page):
        self.bar.setValue(int(done / total * 100))
        self._set_state("progress_page", name=name, page=page)

    def on_done(self, ok, fail, out_dir):
        self.timer.stop()
        self._running = False
        self.bar.setValue(100 if fail == 0 else self.bar.value())
        self._refresh_go()
        self._set_state("state_done", ok=ok, fail=fail)
        self.log.append("\n" + T("log_done", out=out_dir))

    def _tick(self):
        el = int(time.time() - self.t0)
        self.lbl_time.setText(f"{el//3600:02d}:{(el%3600)//60:02d}:{el%60:02d}")

    def closeEvent(self, e):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(5000)
        super().closeEvent(e)


def main():
    global LANG
    app = QApplication(sys.argv)
    app.setApplicationName(APP_ID)
    saved = QSettings(APP_ID, APP_ID).value("lang", "fa")
    LANG = saved if saved in STRINGS else "fa"
    app.setLayoutDirection(direction())
    w = Main()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
