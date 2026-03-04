from flask import Flask, request, jsonify
import asyncio
from playwright.async_api import async_playwright

app = Flask(__name__)

async def scrape_product(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width":1280,"height":800}
        )
        page = await context.new_page()
        await page.goto(url, timeout=60000)

        product_name, price, image_url = None, None, None

        # Amazon selectors
        if "amazon." in url:
            await page.wait_for_selector("#productTitle", timeout=60000)
            product_name = await page.text_content("#productTitle")

            await page.wait_for_selector(".a-price .a-offscreen", timeout=60000)
            price = await page.text_content(".a-price .a-offscreen")

            await page.wait_for_selector("#landingImage", timeout=60000)
            image_url = await page.get_attribute("#landingImage", "src")

        # AliExpress selectors
        elif "aliexpress." in url:
            await page.wait_for_selector(".product-title-text", timeout=60000)
            product_name = await page.text_content(".product-title-text")

            await page.wait_for_selector(".product-price-value", timeout=60000)
            price = await page.text_content(".product-price-value")

            await page.wait_for_selector(".product-main-image img", timeout=60000)
            image_url = await page.get_attribute(".product-main-image img", "src")

        # Noon selectors
        elif "noon." in url:
            await page.wait_for_selector(".product-title", timeout=60000)
            product_name = await page.text_content(".product-title")

            await page.wait_for_selector(".selling-price", timeout=60000)
            price = await page.text_content(".selling-price")

            await page.wait_for_selector(".primary-image img", timeout=60000)
            image_url = await page.get_attribute(".primary-image img", "src")

        await browser.close()
        return {
            "name": product_name,
            "price": price,
            "image": image_url
        }

@app.route("/scrape", methods=["GET"])
def scrape_endpoint():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL مطلوب"}), 400
    try:
        product_data = asyncio.run(scrape_product(url))
        return jsonify(product_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
