import asyncio
import os
import re
import requests
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

SAVE_DIR = "D:/Images"

async def collect_image_urls(page):
    image_urls = set()
    # images in img tags
    imgs = await page.query_selector_all("img")
    for img in imgs:
        for attr in ["src", "data-src", "data-srcset", "srcset"]:
            val = await img.get_attribute(attr)
            if not val:
                continue
            if attr.endswith("set"):
                for part in val.split(','):
                    url = part.strip().split(' ')[0]
                    if url:
                        if url.startswith('//'):
                            url = 'https:' + url
                        image_urls.add(url)
            else:
                url = val
                if url.startswith('//'):
                    url = 'https:' + url
                image_urls.add(url)
    # background-image styles
    divs = await page.query_selector_all("[style*='background-image']")
    for div in divs:
        style = await div.get_attribute("style")
        if style:
            m = re.search(r"background-image\s*:\s*url\(['\"]?(.*?)['\"]?\)", style)
            if m:
                url = m.group(1)
                if url.startswith('//'):
                    url = 'https:' + url
                image_urls.add(url)
    return list(image_urls)

async def fetch_review_images(url):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        await stealth_async(page)
        await page.goto(url, timeout=60000)
        # click Fotoğraflı Değerlendirme tab if present
        try:
            await page.get_by_text("Fotoğraflı Değerlendirme", exact=False).click()
            await page.wait_for_timeout(2000)
        except Exception:
            pass
        # load more reviews
        while True:
            try:
                btn = page.get_by_text("Daha fazla göster", exact=False)
                if await btn.is_visible():
                    await btn.click()
                    await page.wait_for_timeout(2000)
                else:
                    break
            except Exception:
                break
        # ensure lazy images loaded
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
        urls = await collect_image_urls(page)
        await browser.close()
    os.makedirs(SAVE_DIR, exist_ok=True)
    for i, img_url in enumerate(urls):
        try:
            resp = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"})
            ext = img_url.split('.')[-1].split('?')[0]
            if len(ext) > 4:
                ext = 'jpg'
            path = os.path.join(SAVE_DIR, f"image_{i}.{ext}")
            with open(path, 'wb') as f:
                f.write(resp.content)
            print(f"Saved {path}")
        except Exception as e:
            print(f"Failed {img_url}: {e}")

if __name__ == "__main__":
    url = "https://www.trendyol.com/rissoli/rissoli-kadin-siyah-gold-yuzuk-detayli-gunluk-sandalet-p-927370327/yorumlar"
    asyncio.run(fetch_review_images(url))
