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
        html_content = await page.content()
        await browser.close()
        return html_content

@app.route("/scrape", methods=["GET"])
def scrape_endpoint():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL مطلوب"}), 400
    try:
        html_content = asyncio.run(scrape_product(url))
        return jsonify({"contents": html_content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
