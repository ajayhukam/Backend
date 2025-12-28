import sqlite3
from datetime import datetime

def init_db(db_path: str):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        message_id TEXT PRIMARY KEY,
        from_msisdn TEXT NOT NULL,
        to_msisdn TEXT NOT NULL,
        ts TEXT NOT NULL,
        text TEXT,
        created_at TEXT NOT NULL
    )
    """)
    conn.commit()
    return conn

def insert_message(conn, m):
    try:
        conn.execute(
            "INSERT INTO messages VALUES (?,?,?,?,?,?)",
            (
                m.message_id,
                m.from_msisdn,
                m.to_msisdn,
                m.ts,
                m.text,
                datetime.utcnow().isoformat() + "Z",
            ),
        )
        conn.commit()
        return "created"
    except sqlite3.IntegrityError:
        return "duplicate"
