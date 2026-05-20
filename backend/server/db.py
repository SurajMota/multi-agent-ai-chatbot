# backend/server/db.py

import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), "chat_logs.db")


# -----------------------------
# CREATE TABLE IF NOT EXISTS
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            message_count INTEGER,
            transcript TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# GET DB CONNECTION
# -----------------------------
def get_conn():
    return sqlite3.connect(DB_PATH)


# Initialize database when imported
init_db()
