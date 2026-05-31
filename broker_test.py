import os
from playwright.async_api import async_playwright

FOREX_USERNAME = os.getenv("FOREX_USERNAME")
FOREX_PASSWORD = os.getenv("FOREX_PASSWORD")
FOREX_LOGIN_URL = os.getenv("FOREX_LOGIN_URL", "https://www.forex.com/en-us/login/")

async def test_forex_login():
    if not FOREX_USERNAME or not FOREX_PASSWORD:
        return {
            "ok": False,
            "stage": "env",
            "error": "Missing FOREX_USERNAME or FOREX_PASSWORD"
        }

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        page = await browser.new_page()

        try:
            await page.goto(FOREX_LOGIN_URL, wait_until="domcontentloaded", timeout=60000)

            title = await page.title()

            await browser.close()

            return {
                "ok": True,
                "stage": "page_loaded",
                "title": title,
                "note": "FOREX.com login page loaded. No login submitted yet."
            }

        except Exception as e:
            await browser.close()
            return {
                "ok": False,
                "stage": "browser",
                "error": str(e)
            }
