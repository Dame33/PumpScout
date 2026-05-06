<div align="center">

# Thanks for checking out PumpScout!

**Toronto's gas price tracker providing live prices, tomorrow's prediction, and a 7-day history, all on your iPhone.**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat-square&logo=fastapi&logoColor=white)
![Swift](https://img.shields.io/badge/Swift-5.9+-FA7343?style=flat-square&logo=swift&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-scraper-2EAD33?style=flat-square&logo=playwright&logoColor=white)

</div>

---

## PumpScout
PumpScout is a Toronto GTA gas price tracker made up of two parts:
- A **Python / FastAPI backend** that scrapes live gas price data from [CityNews Toronto](https://toronto.citynews.ca/toronto-gta-gas-prices/), stores it in a local SQLite database, and serves it through a clean REST API.
- A **native iOS app (Swift)** that calls the backend and displays the current price, tomorrow's predicted price, a buy/don't-buy recommendation, and a 7-day price history.

Every time you hit refresh, the backend uses **Playwright** to render the CityNews page in a headless Chromium browser (needed because the gas data is JavaScript-rendered), parses the prediction and history table with **BeautifulSoup**, and upserts the results into SQLite.

---

## Current Features

- Live price of Toronto average gas price in cents/litre
- Tomorrow's prediction from CityNews's forecast section
- Buy signal based on today's price compared to  7-day average 
- 7-day price trend for the past week
- Persistent storage, SQLite database with upsert logic so re-scraping never creates duplicates
---

## Tech Stack
| Layer | Tech |
|---|---|
| Backend framework | FastAPI |
| Scraping | Playwright (headless Chromium) + BeautifulSoup4 |
| Database | SQLite3 (via Python stdlib) |
| Data validation | Pydantic |
| HTTP client | httpx |
| Frontend | SwiftUI (iOS) |
---

## Project Structure

```
PumpScout/
├── backend/
│   └── app/
│       ├── main.py        # FastAPI app, routes, startup
│       ├── config.py      # URL and DB path constants
│       ├── database.py    # SQLite connection and schema init
│       ├── scraper.py     # Playwright fetch + BeautifulSoup parse entry point
│       ├── models.py      # HTML parsing logic (prediction + history table)
│       ├── services.py    # Business logic, DB queries, summary builder
│       └── schemas.py     # Pydantic response models
└── frontend/
    └── PumpScout/         # Xcode project (Swift / SwiftUI)
```
---

## Backend Setup
### Prerequisites
- Python 3.11+
- pip

### 1. Clone the repo

```bash
git clone https://github.com/Dame33/PumpScout.git
cd PumpScout/backend
```

### 2. Create and activate a virtual environment

```bash
# Create the venv
python3 -m venv venv

# Activate it — macOS/Linux
source venv/bin/activate

# Activate it — Windows
venv\Scripts\activate
```
You should see (venv) in your terminal prompt.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright browsers
Playwright needs to download a Chromium binary the first time:

```bash
playwright install chromium
```

### 5. Run the server
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.
---

## API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/refresh` | Scrape CityNews and upsert latest data into DB |
| `GET` | `/summary` | Get current price, prediction, buy signal, and 7-day history |
| `GET` | `/history` | Get the raw last 7 days of price snapshots |

### Example: refresh then fetch summary
```bash
# 1. Scrape latest data
curl -X POST http://127.0.0.1:8000/refresh

# 2. Get the summary
curl http://127.0.0.1:8000/summary
```

### Example `/summary` response

```json
{
  "currentPriceCents": 163.9,
  "tomorrowPredictedPrice": 161.0,
  "updatedAt": "2025-05-01T14:32:00+00:00",
  "sevenDayHistory": [
    { "dateLabel": "April 25, 2025", "price": 159.4 },
    ...
  ],
  "buyMessage": "Good buy! Price below weekly average",
  "background": "green",
  "source": "https://toronto.citynews.ca/toronto-gta-gas-prices/"
}
```

---

## iOS App Setup

1. Open `frontend/PumpScout/PumpScout.xcodeproj` in Xcode.
2. Make sure the backend is running locally (see above).
3. Update the base URL in the app to point to your machine's local IP (you can find this by running ipconfig in your terminal), if running on a physical device, or keep `http://127.0.0.1:8000` for the simulator.
4. Build and run on your simulator or device.

---

## Data Source

Gas prices are scraped from **[CityNews Toronto — GTA Gas Prices](https://toronto.citynews.ca/toronto-gta-gas-prices/)**.

> This project is for personal/educational use. Scraping frequency should be kept reasonable out of respect for the source.

---

## License

MIT
