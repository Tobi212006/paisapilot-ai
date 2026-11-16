import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from .money import paise

def db_path() -> str:
    return os.getenv("DATABASE_PATH", str(Path(__file__).resolve().parents[1] / "paisa_pilot.db"))

@contextmanager
def connect():
    connection = sqlite3.connect(db_path(), timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA busy_timeout=15000")
    try:
        with connection:
            yield connection
    finally:
        connection.close()

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
        # Keep existing local records in the demo workspace during migration.
        for table in ("transactions", "goals", "invoices"):
            columns = {r["name"] for r in db.execute(f"PRAGMA table_info({table})")}
            if "owner_id" not in columns:
                db.execute(f"ALTER TABLE {table} ADD COLUMN owner_id TEXT NOT NULL DEFAULT 'demo'")
        if "direction" not in {r["name"] for r in db.execute("PRAGMA table_info(transactions)")}:
            db.execute("ALTER TABLE transactions ADD COLUMN direction TEXT NOT NULL DEFAULT 'expense'")
        db.execute("CREATE INDEX IF NOT EXISTS transactions_owner ON transactions(owner_id)")
        db.execute("CREATE INDEX IF NOT EXISTS goals_owner ON goals(owner_id)")
        db.execute("CREATE INDEX IF NOT EXISTS invoices_owner ON invoices(owner_id)")
        db.execute("CREATE TABLE IF NOT EXISTS app_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        count = db.execute("SELECT COUNT(*) AS n FROM transactions").fetchone()["n"]
        seeded = db.execute("SELECT value FROM app_meta WHERE key='demo_seeded'").fetchone()
        if count == 0 and not seeded:
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
        db.execute("INSERT OR IGNORE INTO app_meta(key,value) VALUES('demo_seeded','1')")
        for table, pairs in {"transactions": [("amount", "amount_paise")], "goals": [("target_amount", "target_paise"), ("saved_amount", "saved_paise")], "invoices": [("taxable_amount", "taxable_paise"), ("total_amount", "total_paise")]}.items():
            columns = {r["name"] for r in db.execute(f"PRAGMA table_info({table})")}
            for old, new in pairs:
                if new not in columns:
                    db.execute(f"ALTER TABLE {table} ADD COLUMN {new} INTEGER")
                for row in db.execute(f"SELECT id,{old} value FROM {table} WHERE {new} IS NULL").fetchall():
                    db.execute(f"UPDATE {table} SET {new}=? WHERE id=?", (paise(row["value"]), row["id"]))
        columns = {r['name'] for r in db.execute('PRAGMA table_info(transactions)')}
        for name, kind in [('batch_id', 'TEXT'), ('archived_at', 'TEXT')]:
            if name not in columns:
                db.execute(f'ALTER TABLE transactions ADD COLUMN {name} {kind}')
        db.executescript('''
        CREATE TABLE IF NOT EXISTS budgets (
          owner_id TEXT NOT NULL, month TEXT NOT NULL, category TEXT NOT NULL,
          limit_paise INTEGER NOT NULL CHECK(limit_paise > 0),
          PRIMARY KEY(owner_id,month,category));
        CREATE TABLE IF NOT EXISTS import_batches (
          id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, label TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, undone INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS goal_movements (
          id INTEGER PRIMARY KEY, goal_id INTEGER NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
          owner_id TEXT NOT NULL, amount_paise INTEGER NOT NULL, note TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE INDEX IF NOT EXISTS transactions_owner_month ON transactions(owner_id,occurred_on,archived_at);
        ''')
        db.execute("INSERT OR REPLACE INTO app_meta(key,value) VALUES('schema_version','3')")
