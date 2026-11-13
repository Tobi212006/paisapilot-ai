import os
import sqlite3
from pathlib import Path

def db_path() -> str:
    return os.getenv("DATABASE_PATH", str(Path(__file__).resolve().parents[1] / "paisa_pilot.db"))

def connect():
    connection = sqlite3.connect(db_path())
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    Path(db_path()).parent.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS transactions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          description TEXT NOT NULL,
          amount REAL NOT NULL CHECK(amount > 0),
          category TEXT NOT NULL,
          occurred_on TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS goals (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL,
          target_amount REAL NOT NULL CHECK(target_amount > 0),
          saved_amount REAL NOT NULL DEFAULT 0 CHECK(saved_amount >= 0),
          target_date TEXT
        );
        CREATE TABLE IF NOT EXISTS invoices (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          customer_label TEXT NOT NULL,
          taxable_amount REAL NOT NULL CHECK(taxable_amount >= 0),
          gst_rate REAL NOT NULL CHECK(gst_rate >= 0 AND gst_rate <= 100),
          total_amount REAL NOT NULL,
          status TEXT NOT NULL DEFAULT 'draft',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)
        count = db.execute("SELECT COUNT(*) AS n FROM transactions").fetchone()["n"]
        if count == 0:
            db.executemany(
                "INSERT INTO transactions(description,amount,category,occurred_on) VALUES(?,?,?,?)",
                [
                    ("Monthly groceries", 2850, "Food", "2026-11-02"),
                    ("Local transport", 920, "Transport", "2026-11-04"),
                    ("Mobile recharge", 399, "Bills", "2026-11-06"),
                    ("Course materials", 1250, "Education", "2026-11-08"),
                    ("Cafe", 460, "Food", "2026-11-10"),
                ],
            )
