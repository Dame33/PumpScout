import sqlite3

from app.config import DB_PATH

#sets up sqlite3 

def get_db() -> sqlite3.Connection: 
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection 

def init_db()-> None:
    connection = get_db()
    connection.execute( 
        """
        CREATE TABLE IF NOT EXISTS toronto_gas_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_key TEXT NOT NULL UNIQUE,
            date_label TEXT NOT NULL,
            price_cents REAL NOT NULL,
            change_cents REAL,
            predicted_tomorrow_cents REAL,
            predicted_direction TEXT,
            source TEXT NOT NULL,
            scraped_at TEXT NOT NULL
        )
        """
    )
    connection.commit()
    connection.close