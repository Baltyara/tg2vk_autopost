import os
import sqlite3
from typing import Optional, Tuple


DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "queue.db"))


def _conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS queue (
            tg_message_id INTEGER PRIMARY KEY,
            file_path TEXT NOT NULL,
            caption TEXT,
            status TEXT NOT NULL DEFAULT 'pending'
        )
        """
    )
    return conn


def enqueue_if_missing(tg_message_id: int, file_path: str, caption: str) -> None:
    with _conn() as c:
        cur = c.execute("SELECT 1 FROM queue WHERE tg_message_id=?", (tg_message_id,))
        if cur.fetchone():
            return
        c.execute(
            "INSERT INTO queue (tg_message_id, file_path, caption, status) VALUES (?, ?, ?, 'pending')",
            (tg_message_id, file_path, caption),
        )


def fetch_next_pending() -> Optional[Tuple[int, str, str]]:
    with _conn() as c:
        cur = c.execute(
            "SELECT tg_message_id, file_path, caption FROM queue WHERE status='pending' ORDER BY tg_message_id ASC LIMIT 1"
        )
        row = cur.fetchone()
        if not row:
            return None
        return int(row[0]), str(row[1]), str(row[2])


def mark_done(tg_message_id: int) -> None:
    with _conn() as c:
        c.execute("UPDATE queue SET status='done' WHERE tg_message_id=?", (tg_message_id,))


