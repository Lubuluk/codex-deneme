import asyncio
import os
from typing import Set

import requests
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

SAVE_DIR = "D:/Images"


async def fetch_review_images(url: str) -> None:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        await stealth_async(page)
        await page.goto(url, timeout=60000)

        # enable photo-only reviews
        try:
            await page.get_by_text("Fotoğraflı Değerlendirme", exact=False).click()
            await page.wait_for_timeout(2000)
        except Exception:
            pass

        state = await page.evaluate("window.__REVIEW_APP_INITIAL_STATE__")
        rating = state["ratingAndReviewResponse"]["ratingAndReview"]
        total_pages = rating["productReviews"]["totalPages"]
        product_id = rating["product"]["id"]
        seller_id = rating["product"]["merchant"]["id"]

        collected: Set[str] = set()
        for page_num in range(total_pages):
            params = {
                "sellerId": seller_id,
                "contentId": product_id,
                "page": page_num,
                "order": "DESC",
                "orderBy": "Score",
                "channelId": 1,
            }
            resp = await page.request.get(
                "https://apigw.trendyol.com/discovery-web-websfxsocialreviewrating-santral/product-reviews-detailed",
                params=params,
            )
            data = await resp.json()

            if page_num == 0:
                imgs = data["result"].get("imageSummary", [])
                for item in imgs:
                    url = item.get("mediaFile", {}).get("url")
                    if url:
                        collected.add(url)

            for review in data["result"]["productReviews"].get("content", []):
                for media in review.get("mediaFiles", []):
                    url = media.get("url")
                    if url:
                        collected.add(url)

        await browser.close()

    os.makedirs(SAVE_DIR, exist_ok=True)
    for i, img_url in enumerate(sorted(collected)):
        try:
            resp = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"})
            ext = img_url.split(".")[-1].split("?")[0]
            if len(ext) > 4:
                ext = "jpg"
            path = os.path.join(SAVE_DIR, f"image_{i}.{ext}")
            with open(path, "wb") as f:
                f.write(resp.content)
            print(f"Saved {path}")
        except Exception as e:
            print(f"Failed {img_url}: {e}")

if __name__ == "__main__":
    url = "https://www.trendyol.com/rissoli/rissoli-kadin-siyah-gold-yuzuk-detayli-gunluk-sandalet-p-927370327/yorumlar"
    asyncio.run(fetch_review_images(url))
