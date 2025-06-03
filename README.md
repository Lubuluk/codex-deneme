# codex-deneme

## Trendyol Review Image Downloader

This repository includes a Python script `download_trendyol_images.py` that downloads user photo review images from Trendyol product pages. The script navigates with Playwright and activates the **Fotoğraflı Değerlendirme** filter before extracting the high‑resolution photo URLs from the page’s review state.

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

### Building a Windows Executable
You can turn the script into a standalone `.exe` using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile download_trendyol_images.py
```

The resulting executable will appear under `dist/`.

