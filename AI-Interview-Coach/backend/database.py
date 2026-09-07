import sqlite3
import pandas as pd
from datetime import datetime
import os

# Ensure the database folder exists
os.makedirs("database", exist_ok=True)
DB_PATH = "database/interviews.db"

def init_db():
    """Creates the SQLite table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS interviews
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  type TEXT,
                  score INTEGER,
                  report TEXT)''')
    conn.commit()
    conn.close()

def save_interview(interview_type, score, report):
    """Saves the completed interview data to SQLite."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO interviews (date, type, score, report) VALUES (?, ?, ?, ?)",
              (current_time, interview_type, score, report))
    conn.commit()
    conn.close()

def get_history():
    """Retrieves all interview records as a Pandas DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM interviews", conn)
    conn.close()
    return df
