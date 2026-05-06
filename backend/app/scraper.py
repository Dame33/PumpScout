from typing import Any

import httpx
from playwright.sync_api import sync_playwright
import asyncio


from bs4 import BeautifulSoup

from app.config import CITYNEWS_URL
from app.models import parse_history_table, parse_prediction_section

def _fetch_html_sync() -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-CA",
        )
        page = context.new_page()
        page.goto("https://toronto.citynews.ca/toronto-gta-gas-prices/", wait_until="domcontentloaded") 
        page.wait_for_selector("#gas_price_latest_container", timeout=15000)  # wait for the actual element
        html = page.content()
        browser.close()
        return html
    
    
async def fetch_html() -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_html_sync)
    
async def scrape_citynews() -> dict[str, Any]:
    html = await fetch_html()
    soup = BeautifulSoup(html, "html.parser")

    print("PAGE TITLE:", soup.title.string if soup.title else "No title")
    print("HAS gas_price_latest_container:", soup.select_one("#gas_price_latest_container") is not None)
    print("HAS page-table-body:", soup.select_one("table.page-table-body") is not None)

    prediction = parse_prediction_section(soup)
    history = parse_history_table(soup)

    print("PREDICTION:", prediction)
    print("HISTORY COUNT:", len(history))

    return {
        "prediction": prediction,
        "history": history,
    }