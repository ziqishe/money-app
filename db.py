import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "finance.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            category TEXT,
            merchant TEXT,
            note TEXT,
            currency TEXT DEFAULT 'CNY',
            created_at TEXT DEFAULT (datetime('now'))
        )
        """)
        conn.commit()

def insert_txn(date, amount, type_, category="", merchant="", note="", currency="CNY"):
    with get_conn() as conn:
        conn.execute("""
        INSERT INTO transactions(date, amount, type, category, merchant, note, currency)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (date, amount, type_, category, merchant, note, currency))
        conn.commit()

def fetch_txns(date_from=None, date_to=None):
    q = "SELECT id, date, amount, type, category, merchant, note, currency FROM transactions WHERE 1=1"
    params = []
    if date_from:
        q += " AND date >= ?"
        params.append(date_from)
    if date_to:
        q += " AND date <= ?"
        params.append(date_to)
    q += " ORDER BY date DESC, id DESC"
    with get_conn() as conn:
        cur = conn.execute(q, params)
        rows = cur.fetchall()
    return rows

def delete_txn(txn_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))
        conn.commit()
