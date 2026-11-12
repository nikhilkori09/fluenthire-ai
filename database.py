import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "interview_coach.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            role TEXT,
            question TEXT,
            readiness_score INTEGER,
            formality_score INTEGER,
            clarity_score INTEGER,
            star_score INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_session(role, question, readiness, formality, clarity, star):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("""
        INSERT INTO sessions (timestamp, role, question, readiness_score, formality_score, clarity_score, star_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ts, role, question, readiness, formality, clarity, star))
    conn.commit()
    conn.close()

def get_all_sessions():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM sessions ORDER BY id DESC", conn)
    conn.close()
    return df