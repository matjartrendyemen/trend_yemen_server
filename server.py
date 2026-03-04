from flask import Flask, request, jsonify
import asyncio
from playwright.async_api import async_playwright

app = Flask(__name__)

async def scrape_product(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url, timeout=60000)

        product_name, price, image_url = None, None, None

        # Amazon selectors
        if "amazon." in url:
            product_name = await page.text_content("#productTitle")
            price = await page.text_content(".a-price .a-offscreen")
            image_url = await page.get_attribute("#landingImage", "src")

        # AliExpress selectors
        elif "aliexpress." in url:
            product_name = await page.text_content(".product-title-text")
            price = await page.text_content(".product-price-value")
            image_url = await page.get_attribute(".product-main-image img", "src")

        # Noon selectors
        elif "noon." in url:
            product_name = await page.text_content(".product-title")
            price = await page.text_content(".selling-price")
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
