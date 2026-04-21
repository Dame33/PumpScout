from pydantic import BaseModel

class DailyGas(BaseModel):
    dateLabel: str
    price: float #track in cents

class GasSummary(BaseModel):
    currentPrice: float
    tomorrowPredictedPrice: float
    updatedAt: str
    sevenDayHistory: list[DailyGas]
    buyMessage: str
    background: str
    source:str

class RefreshResponse(BaseModel):
    scrapedAt: str
    currentPrice: float
    tomorrowPredictedPrice: float
    insertedDays: int
    source: str