import sqlite3
from datetime import datetime
from typing import Optional

DB_NAME = "autocomplete_history.db"

def init_db(db_path: str = DB_NAME):
    """
    Create/open the SQLite DB and ensure the user_history table exists.
    Returns an open sqlite3.Connection (commit happens inside the function).
    """
    conn = sqlite3.connect(db_path, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_history (
            username TEXT PRIMARY KEY COLLATE NOCASE,
            history  TEXT NOT NULL DEFAULT ''
        );
    """)
    conn.commit()
    return conn

def add_user(conn: sqlite3.Connection, username: str):
    """
     Insert a user row if it doesn't exist yet.
     """
    conn.execute("INSERT OR IGNORE INTO user_history (username) VALUES (?);", (username,))
    conn.commit()

def add_message(
    conn: sqlite3.Connection,
    username: str,
    message: str,
    role: str = "user",
    ts_utc: Optional[str] = None,
):
    """
    Append a single line to the user's history string.
    Line format (good for LLM prompts): "[YYYY-MM-DD HH:MM:SS] role: message"
    - Creates the user row on-the-fly if it's missing.
    """
    if ts_utc is None:
        ts_utc = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts_utc}] {role}: {message}\n"

    cur = conn.execute("SELECT history FROM user_history WHERE username=?;", (username,))
    row = cur.fetchone()

    if row is None:
        conn.execute(
            "INSERT INTO user_history (username, history) VALUES (?, ?);",
            (username, line),
        )
    else:
        new_hist = (row[0] or "") + line
        conn.execute(
            "UPDATE user_history SET history=? WHERE username=?;",
            (new_hist, username),
        )
    conn.commit()

def get_history(conn: sqlite3.Connection, username: str) -> str:
    cur = conn.execute("SELECT history FROM user_history WHERE username=?;", (username,))
    row = cur.fetchone()
    return row[0] if row else ""

if __name__ == "__main__":
    conn = init_db()                       # creates autocomplete_history.db (if missing)
    add_user(conn, "alice")                # safe if already exists
    add_message(conn, "alice", "hell")     # user typed 'hell'
    add_message(conn, "alice", "hello world")
    print(get_history(conn, "alice"))
    conn.close()