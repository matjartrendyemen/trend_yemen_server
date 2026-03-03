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

        # استخراج اسم المنتج (عادة في h1)
        product_name = await page.text_content("h1")

        # استخراج السعر (حسب الموقع، مثلاً class="price")
        price = await page.text_content(".price")

        # استخراج رابط الصورة (عادة في img داخل div المنتج)
        image_url = await page.get_attribute("img", "src")

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
