import sqlite3

from fastapi import HTTPException

from app.config import CITYNEWS_URL
from app.database import get_db
from app.models import buy_message
from app.schemas import DailyGas, GasSummary

def upsert_history_rows(history: list[dict], prediction: dict, scraped_at: str)-> int:
    connection = get_db()
    upsertted = 0

    try:
        for index, item in enumerate(history):
            predicted_tomorrow =prediction["tomorrow_predicted_price_cents"] if index == 0 else None
            predicted_direction = prediction.get("predicted_direction") if index == 0 else None

            connection.execute(
                """
                INSERT INTO toronto_gas_snapshots(
                    day_key,
                    date_label,
                    price_cents,
                    change_cents,
                    predicted_tomorrow_cents,
                    predicted_direction,
                    source,
                    scraped_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(day_key) DO UPDATE SET
                    date_label = excluded.date_label,
                    price_cents = excluded.price_cents,
                    change_cents = excluded.change_cents,
                    predicted_tomorrow_cents = COALESCE(
                        excluded.predicted_tomorrow_cents,
                        toronto_gas_snapshots.predicted_tomorrow_cents
                    ),
                    predicted_direction = COALESCE(
                        excluded.predicted_direction,
                        toronto_gas_snapshots.predicted_direction
                    ),
                    source = excluded.source,
                    scraped_at = excluded.scraped_at
                """,
                (
                    item["day_key"],
                    item["date_label"],
                    item["price_cents"],
                    item["change_cents"],
                    predicted_tomorrow,
                    predicted_direction,
                    CITYNEWS_URL,
                    scraped_at,
                ),
            )
            upsertted += 1

        connection.commit()
    finally:
        connection.close()

    return upsertted

def get_last_seven_days() ->list[sqlite3.Row]:
    connection = get_db()
    try:
        rows = connection.execute(
            """
            SELECT day_key, date_label, price_cents, predicted_tomorrow_cents, scraped_at
            FROM toronto_gas_snapshots
            ORDER BY day_key DESC
            LIMIT 7
            """
        ).fetchall()

    finally:
        connection.close()
    return list(reversed(rows))

def build_summary() -> GasSummary:
    rows = get_last_seven_days()
    if not rows:
        raise HTTPException (status_code=404, detail="No Toronto gas data found.")
    latest = rows[-1]
    current_price = float(latest["price_cents"])

    seven_day_history = [
        DailyGas(dateLabel=row["date_label"], priceCents=float(row["price_cents"]))
        for row in rows
    ]

    seven_day_average = sum(point.priceCents for point in seven_day_history) / len(seven_day_history)
    buy_message, background = buy_message(current_price, seven_day_average)

    tomorrow_predicted = latest["predicted_tomorrow_cents"]
    if tomorrow_predicted is None:
        tomorrow_predicted = current_price

    return GasSummary(
        currentPriceCents=round(current_price, 1),
        tomorrowPredictedPriceCents=round(float(tomorrow_predicted), 1),
        updatedAt=str(latest["scraped_at"]),
        sevenDayHistory=seven_day_history,
        buyMessage=buy_message,
        background=background,
        source=CITYNEWS_URL,
    )