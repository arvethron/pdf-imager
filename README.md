# پی‌دی‌اف ایمیجر (PDF Imager)

تبدیل حرفه‌ای PDF به تصویر — تکی و دسته‌ای، با رابط گرافیکی فارسی و انگلیسی.

A desktop app for converting PDF pages into images — single file or batch — with a Persian and English UI.

---

## ویژگی‌ها

- تبدیل یک فایل PDF، چند فایل، یا کل یک پوشه (حالت دسته‌ای، با جست‌وجوی زیرپوشه‌ها)
- خروجی در فرمت‌های **WEBP**، **JPG**، **PNG**، **TIFF** و **BMP**
- تنظیم رزولوشن رندر بر حسب DPI
- حالت **تک‌صفحه‌ای** یا **چسباندن صفحات** در یک تصویر بلند
- حالت **سیاه‌وسفید**
- خروجی به‌صورت یک پوشه‌ی جدا برای هر PDF، یا آرشیو **ZIP** / **CBZ**
- الگوی نام‌گذاری قابل تنظیم برای فایل و پوشه، با شماره شروع و تعداد ارقام دلخواه
- امکان پیوسته نگه داشتن شماره صفحات بین همه‌ی فایل‌ها
- انتخاب بازه‌ی صفحات (از صفحه‌ی X تا صفحه‌ی Y)
- حذف خودکار برچسب‌های ابتدای نام فایل، مثل `[SiteName]-` از نام خروجی
- Drag & Drop فایل یا پوشه روی پنجره
- نوار پیشرفت، زمان سپری‌شده و گزارش لحظه‌ای عملیات
- رابط دوزبانه (فارسی / English) که زبان انتخابی ذخیره می‌شود، و ۷ رنگ تم

## پیش‌نیازها

- Python 3.9 یا جدیدتر
- کتابخانه‌های زیر (در `requirements.txt` آمده‌اند):
  - [PySide6](https://pypi.org/project/PySide6/) — رابط گرافیکی (Qt)
  - [PyMuPDF](https://pypi.org/project/PyMuPDF/) — رندر صفحات PDF
  - [Pillow](https://pypi.org/project/Pillow/) — ذخیره‌ی تصاویر

**فونت پیشنهادی:** برای نمایش بهتر متن فارسی، فونت [Vazirmatn](https://github.com/rastikerdar/vazirmatn) را نصب کنید. در نبود آن، برنامه از Segoe UI یا Tahoma استفاده می‌کند.

## نصب

```bash
git clone https://github.com/arvethron/pdf-imager.git
cd pdf-imager

python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## اجرا

```bash
python pdf_imager.py
```

## راهنمای استفاده

1. **منبع را انتخاب کنید:** با دکمه‌ی 📄 یک یا چند فایل PDF انتخاب کنید، یا با 📁 یک پوشه (حالت دسته‌ای). می‌توانید فایل یا پوشه را مستقیم داخل پنجره رها کنید.
2. **پوشه‌ی خروجی را مشخص کنید:** اگر خالی بماند، خروجی کنار فایل‌های ورودی ساخته می‌شود.
3. **تنظیمات را انجام دهید:** فرمت، DPI، حالت سیاه‌وسفید، چسباندن صفحات، بازه‌ی صفحات و بسته‌بندی ZIP/CBZ.
4. **«شروع عملیات» را بزنید.** در حین پردازش می‌توانید با «توقف» عملیات را متوقف کنید.

> **نکته:** در حالت ZIP یا CBZ، پوشه‌بندی برای هر PDF نادیده گرفته می‌شود و فقط یک آرشیو ساخته می‌شود که نامش از الگوی پوشه گرفته شده است.

**راهنمای رزولوشن:** DPI بالاتر یعنی جزئیات بیشتر و حجم فایل بیشتر. فرمت‌های WEBP و JPG حجم کمتری دارند، و PNG و TIFF بدون افت کیفیت هستند.

## نام‌گذاری خروجی

در تب **تنظیمات** می‌توانید الگوی نام فایل و پوشه را تعیین کنید:

| متغیر | معنی |
|-------|------|
| `{name}` | نام خود فایل PDF (بدون برچسب‌های ابتدایی) |
| `{n}` | شماره‌ی صفحه یا فایل، با تعداد ارقام انتخابی |

**مثال:** اگر الگوی پوشه را `Vol {n}` و شماره‌ی شروع را `1` با ۳ رقم بگذارید، خروجی این می‌شود:

```
Vol 001/
Vol 002/
Vol 003/
```

الگوی پیش‌فرض فایل `{name}_{n}` است، یعنی خروجی مثلاً `MyBook_001.webp`.

## ساختار پروژه

```
pdf-imager/
├── pdf_imager.py      # کد اصلی برنامه
├── requirements.txt   # وابستگی‌ها
├── .gitignore
└── README.md
```

## توسعه‌دهنده

**ARVETHRON**

- GitHub: [github.com/arvethron](https://github.com/arvethron)
- Telegram: [t.me/ARVETHRON](https://t.me/ARVETHRON)

---

## English

**PDF Imager** converts PDF pages into images, either one file at a time or in batch mode. The interface is available in Persian and English; you can switch languages from the top bar, and your choice is remembered.

### Features

- Convert a single PDF, several PDFs, or an entire folder (batch mode, including subfolders)
- Output formats: **WEBP**, **JPG**, **PNG**, **TIFF**, **BMP**
- Adjustable render resolution (DPI)
- **One image per page** or **stitch pages** into one long image
- **Grayscale** mode
- Output as a separate folder per PDF, or as a **ZIP** / **CBZ** archive
- Customizable naming patterns for files and folders, with start number and digit padding
- Optional continuous page numbering across all PDFs
- Page range selection
- Leading bracketed tags in filenames (e.g. `[SiteName]-`) are stripped from the output names
- Drag & drop files or folders onto the window
- Progress bar, elapsed time, and a live log

### Requirements

- Python 3.9+
- `pip install -r requirements.txt` (PySide6, PyMuPDF, Pillow)
- Optional: the [Vazirmatn](https://github.com/rastikerdar/vazirmatn) font for better Persian text rendering

### Installation and usage

```bash
git clone https://github.com/arvethron/pdf-imager.git
cd pdf-imager
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python pdf_imager.py
```

1. Choose PDF file(s) or a folder (or drag and drop them into the window).
2. Set the output folder. If left empty, output goes next to the source files.
3. Adjust format, DPI, grayscale, stitching, page range, and packaging options.
4. Click **Start**. Use **Stop** to cancel a running job.

### Naming

In the **Settings** tab, `{name}` is replaced by the PDF's name and `{n}` by the number. For example, a folder pattern of `Vol {n}` with start number `1` and 3 digits produces `Vol 001`, `Vol 002`, and so on.

### Author

**ARVETHRON**: [GitHub](https://github.com/arvethron) · [Telegram](https://t.me/ARVETHRON)
