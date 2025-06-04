# codex-deneme

## Trendyol Review Image Downloader

This repository includes a Python script `download_trendyol_images.py` that downloads user photo review images from Trendyol product pages. The scraper opens the page with Playwright, enables the **Fotoğraflı Değerlendirme** filter and then queries Trendyol's review API page by page to collect every high‑resolution image URL.

### Requirements
- Python 3.9+
- `playwright`
- `playwright-stealth`
- `requests`
- (optional) `pyinstaller` for generating an executable

Install dependencies and browsers:

```bash
pip install playwright playwright-stealth requests
playwright install chromium
```

### Usage
Run the script with a product URL:

```bash
python download_trendyol_images.py
```

The script saves images under `D:/Images` (on Windows). On Linux/macOS this path will be created as a directory literally named `D:` with a subfolder `Images`.
If any review API call fails or returns invalid JSON, the script skips that page and continues so a single bad response doesn't stop the entire download.

### Building a Windows Executable
You can turn the script into a standalone `.exe` using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile download_trendyol_images.py
```

The resulting executable will appear under `dist/`.

