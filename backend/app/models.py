from datetime import datetime
import re
from typing import Any

from bs4 import BeautifulSoup

def normalize_text (value: str)-> str:
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()

def buy_message(current:float, seven_day_avg: float)-> tuple[str, str]:
    delta = current - seven_day_avg

    if delta <= -2.0:
        return "Good buy, green"
    if delta >= 2.0:
        return "Bad buy, red"
    return "Not bad, yellow"

def parse_prediction_section(soup: BeautifulSoup) -> dict[str, Any]:
    candidates = [
        "div.gas_price_latest_container",
        "div.gas-prices-section",
        "main",
        "body",
    ]

    latest_container = None
    for selector in candidates:
        latest_container = soup.select_one(selector)
        if latest_container is not None:
            text = normalize_text(latest_container.get_text(" ", strip=True))
            if "average of" in text.lower() and (
                "expected to" in text.lower()
                or "remain unchanged" in text.lower()
                or "holding at" in text.lower()
            ):
                break
            latest_container = None

    if latest_container is None:
        full_text = normalize_text(soup.get_text(" ", strip=True))
        if "average of" not in full_text.lower():
            raise ValueError("Could not find gas prediction text anywhere in page")
        sentence_text = full_text
        change_text = full_text
    else:
        change_box = latest_container.select_one("div.data-box-change")
        change_box = latest_container.select_one("div.data-box-change")
        change_text = normalize_text(change_box.get_text(" ", strip=True)) if change_box else ""
        # Always use the full container text so we get the whole sentence with the price
        sentence_text = normalize_text(latest_container.get_text(" ", strip=True))

    tomorrow_match = re.search(
        r"average of\s+(\d+(?:\.\d+)?)\s*cent",
        sentence_text,
        flags=re.IGNORECASE,
    )
    if tomorrow_match is None:
        raise ValueError(f"Could not parse tomorrow predicted price from: {sentence_text}")

    tomorrow_price = float(tomorrow_match.group(1))

    direction = None
    change_amount = None

    if re.search(r"remain unchanged|holding at", sentence_text, flags=re.IGNORECASE):
        direction = "unchanged"
        change_amount = 0.0
        current_price = tomorrow_price
    else:
        direction_match = re.search(r"expected to (fall|rise)", sentence_text, flags=re.IGNORECASE)
        amount_match = re.search(r"(fall|rise)\s+(\d+(?:\.\d+)?)\s*cent", sentence_text, flags=re.IGNORECASE)

        direction = direction_match.group(1).lower() if direction_match else None
        change_amount = float(amount_match.group(2)) if amount_match else None

        if change_amount is None:
            change_from_box = re.search(r"(\d+(?:\.\d+)?)", change_text)
            if change_from_box:
                change_amount = float(change_from_box.group(1))

        if direction == "fall" and change_amount is not None:
            current_price = tomorrow_price + change_amount
        elif direction == "rise" and change_amount is not None:
            current_price = tomorrow_price - change_amount
        else:
            current_price = tomorrow_price

    return {
        "current_price_cents": round(current_price, 1),
        "tomorrow_predicted_price_cents": round(tomorrow_price, 1),
        "predicted_direction": direction,
        "predicted_change_cents": change_amount,
    }


def parse_history_table(soup: BeautifulSoup)-> list[dict[str,Any]]:
    table = soup.select_one("table.page-table-body")
    if table is None:
        raise ValueError("Could not find historical values table")

    rows = table.select("tbody tr")
    history: list[dict[str, Any]] = []

    for row in rows:
        cols = row.select("td.page-table-column")
        if len(cols) < 3:
            continue

        date_text = normalize_text(cols[0].get_text(" ", strip=True))
        change_text = normalize_text(cols[1].get_text(" ", strip=True))
        price_text = normalize_text(cols[2].get_text(" ", strip=True))

        if not date_text or not price_text:
            continue

        price_match = re.search(r"(\d+(?:\.\d+)?)", price_text)
        if not price_match:
            continue

        change_match = re.search(r"([+\-]?\d+(?:\.\d+)?)", change_text)
        change_value = float(change_match.group(1)) if change_match else 0.0
        price_value = float(price_match.group(1))

        history.append(
            {
                "date_label": date_text,
                "day_key": datetime.strptime(date_text, "%B %d, %Y").strftime("%Y-%m-%d"),
                "change_cents": change_value,
                "price_cents": price_value,
            }
        )

    if not history:
        raise ValueError("No historical table found")

    return history