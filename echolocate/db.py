import sqlite3
from pathlib import Path
from datetime import datetime

DB_FILE = Path.home() / '.echolocate' / 'events.db'
DB_FILE.parent.mkdir(parents=True, exist_ok=True)

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT NOT NULL,
    zone TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
"""

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute(SCHEMA)
    return conn

def log_event(item: str, zone: str, ts: datetime):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO events (item, zone, timestamp) VALUES (?, ?, ?)",
            (item, zone, ts.isoformat()),
        )
        conn.commit()

def last_seen(item: str):
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT zone, timestamp FROM events WHERE item=? ORDER BY timestamp DESC LIMIT 1",
            (item,),
        )
        row = cur.fetchone()
        if row:
            zone, ts = row
            dt = datetime.fromisoformat(ts)
            return zone, dt
        return None, None
