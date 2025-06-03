import asyncio
import os
import requests
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

SAVE_DIR = "D:/Images"


async def fetch_review_images(url):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        await stealth_async(page)
        await page.goto(url, timeout=60000)

        # activate photo reviews tab if available
        try:
            await page.get_by_text("Fotoğraflı Değerlendirme", exact=False).click()
            await page.wait_for_timeout(2000)
        except Exception:
            pass

        # click "Daha fazla g\xC3\xB6ster" buttons if present
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

        # scroll to bottom to trigger lazy loading
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)

        # read image list from global state
        state = await page.evaluate("window.__REVIEW_APP_INITIAL_STATE__")
        urls = []
        try:
            imgs = state["ratingAndReviewResponse"]["ratingAndReview"]["imageSummary"]
            for item in imgs:
                url = item.get("mediaFile", {}).get("url")
                if url:
                    urls.append(url)
        except Exception as e:
            print(f"Failed to parse imageSummary: {e}")

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
