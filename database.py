import sqlite3

DB_NAME = "cash_posting.db"

def create_database():

    conn = sqlite3.connect(DB_NAME)

    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS detail_table (
        id INTEGER PRIMARY KEY,
        pas_system TEXT,
        deposit_date TEXT,
        entry_type TEXT,
        amount REAL,
        batch_number TEXT,
        note TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS batch_table (
        id INTEGER PRIMARY KEY,
        batch_name TEXT,
        net_payments REAL,
        net_ups REAL,
        totals REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS batch_status (
        batch_id INTEGER PRIMARY KEY,
        status TEXT,
        created_by TEXT,
        approved_by TEXT,
        date_created TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY,
        username TEXT,
        action TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()