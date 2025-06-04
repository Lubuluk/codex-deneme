# codex-deneme

## Trendyol Review Image Downloader

This repository includes a Python script `download_trendyol_images.py` that downloads user photo review images from Trendyol product pages. The scraper opens the page with Playwright, enables the **Fotoğraflı Değerlendirme** filter and then opens the **Tümü** gallery to display every photo review. It repeatedly clicks the **Daha fazla göster** button while scrolling inside the gallery dialog until no new images load. During the process it listens for the page's own review API requests and parses their JSON payloads so every high‑resolution photo is saved without performing direct blocked requests.

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
If a network call fails or returns invalid JSON, the script ignores it so one bad response doesn't stop the entire download.

### Building a Windows Executable
You can turn the script into a standalone `.exe` using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile download_trendyol_images.py
```

The resulting executable will appear under `dist/`.

