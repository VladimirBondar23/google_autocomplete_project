import sqlite3
from datetime import datetime
from typing import Optional

DB_NAME = "autocomplete_history.db"

def init_db(db_path: str = DB_NAME):
    pass

def add_user(conn: sqlite3.Connection, username: str):
    pass

def add_message(
    conn: sqlite3.Connection,
    username: str,
    message: str,
    role: str = "user",
    ts_utc: Optional[str] = None,
):
    pass

def get_history(conn: sqlite3.Connection, username: str):
    pass