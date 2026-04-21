from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import CITYNEWS_URL
from app.database import init_db
from app.schemas import RefreshResponse, GasSummary
from app.scraper import scrape_citynews
from app.services import build_summary, get_last_seven_days, upsert_history_rows

app = FastAPI(title="Toronto Gas Backend", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "message": "Toronto Gas Backend is running.",
        "source": CITYNEWS_URL,
        "mode": "toronto-only",
    }


@app.post("/refresh", response_model=RefreshResponse)
async def refresh_data() -> RefreshResponse:
    scraped_at = datetime.now(timezone.utc).isoformat()

    try:
        result = await scrape_citynews()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch CityNews page: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to parse CityNews page: {exc}") from exc

    prediction = result["prediction"]
    history = result["history"]
    count = upsert_history_rows(history, prediction, scraped_at)

    return RefreshResponse(
    scrapedAt=scraped_at,
    currentPrice=prediction["current_price_cents"],
    tomorrowPredictedPrice=prediction["tomorrow_predicted_price_cents"], 
    insertedDays=count,
    source=CITYNEWS_URL,
    )


@app.get("/summary", response_model=GasSummary)
def get_summary() -> GasSummary:
    return build_summary()


@app.get("/history")
def get_history() -> dict[str, Any]:
    rows = get_last_seven_days()
    return {
        "history": [
            {
                "dateLabel": row["date_label"],
                "priceCents": float(row["price_cents"]),
                "predictedTomorrowPriceCents": row["predicted_tomorrow_cents"],
                "scrapedAt": row["scraped_at"],
            }
            for row in rows
        ],
        "source": CITYNEWS_URL,
    }