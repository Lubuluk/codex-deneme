import asyncio
import os
from typing import Set

import requests
from playwright.async_api import async_playwright, Page
from playwright_stealth import stealth_async

SAVE_DIR = "D:/Images"


def _extract_from_result(result: dict, collected: Set[str]) -> None:
    for item in result.get("imageSummary", []):
        url = item.get("mediaFile", {}).get("url")
        if url:
            collected.add(url)
    for review in result.get("productReviews", {}).get("content", []):
        for media in review.get("mediaFiles", []):
            url = media.get("url")
            if url:
                collected.add(url)


async def fetch_review_images(url: str) -> None:
    collected: Set[str] = set()

    async def handle_response(resp):
        if "product-reviews" not in resp.url:
            return
        if resp.status != 200:
            print(f"Response {resp.url} -> {resp.status}")
            return
        try:
            data = await resp.json()
        except Exception:
            print(f"Failed to parse JSON from {resp.url}")
            return
        _extract_from_result(data.get("result", {}), collected)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
        context = await browser.new_context(ignore_https_errors=True)
        page: Page = await context.new_page()
        await stealth_async(page)
        page.on("response", handle_response)

        await page.goto(url, timeout=60000)

        try:
            await page.get_by_text("Fotoğraflı Değerlendirme", exact=False).click()
            await page.wait_for_timeout(2000)
        except Exception:
            pass

        prev_count = 0
        stagnant = 0
        for _ in range(50):
            btn = page.locator("text=Daha fazla g\xF6ster")
            if await btn.count() > 0:
                try:
                    await btn.first.click()
                    await page.wait_for_timeout(1500)
                except Exception:
                    pass
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(1000)

            try:
                state = await page.evaluate("window.__REVIEW_APP_INITIAL_STATE__")
                rating = state.get("ratingAndReviewResponse", {}).get("ratingAndReview", {})
                _extract_from_result(rating, collected)
            except Exception:
                pass

            if len(collected) == prev_count:
                stagnant += 1
            else:
                prev_count = len(collected)
                stagnant = 0

            if await btn.count() == 0 and stagnant >= 3:
                break

        await page.wait_for_timeout(3000)
        try:
            state = await page.evaluate("window.__REVIEW_APP_INITIAL_STATE__")
            rating = state.get("ratingAndReviewResponse", {}).get("ratingAndReview", {})
            _extract_from_result(rating, collected)
        except Exception:
            pass

        await browser.close()

    os.makedirs(SAVE_DIR, exist_ok=True)
    print(f"Attempting to download {len(collected)} images")
    for i, img_url in enumerate(sorted(collected)):
        try:
            resp = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"})
            ext = img_url.split(".")[-1].split("?")[0]
            if len(ext) > 4:
                ext = "jpg"
            path = os.path.join(SAVE_DIR, f"image_{i}.{ext}")
            with open(path, "wb") as f:
                f.write(resp.content)
            print(f"Saved {path} ({i + 1}/{len(collected)})")
        except Exception as e:
            print(f"Failed {img_url}: {e}")
    print("Download completed")


if __name__ == "__main__":
    url = "https://www.trendyol.com/rissoli/rissoli-kadin-siyah-gold-yuzuk-detayli-gunluk-sandalet-p-927370327/yorumlar"
    asyncio.run(fetch_review_images(url))
