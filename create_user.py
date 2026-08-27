import sqlite3
import bcrypt

DB = "cash_posting.db"

def create_user(username, password, role):

    conn = sqlite3.connect(DB)

    hashed = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    )

    conn.execute("""
        INSERT INTO users
        (username, password, role)
        VALUES (?, ?, ?)
    """, (
        username,
        hashed,
        role
    ))

    conn.commit()
    conn.close()

    print(f"User {username} created.")

# Create initial users
create_user("admin", "Admin123!", "Admin")
create_user("poster1", "Poster123!", "Poster")
create_user("reviewer1", "Review123!", "Reviewer")