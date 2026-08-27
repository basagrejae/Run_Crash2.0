import sqlite3

conn = sqlite3.connect("cash_posting.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password BLOB NOT NULL,
    role TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Users table created.")