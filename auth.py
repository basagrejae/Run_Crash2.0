import sqlite3
import bcrypt

DB = "cash_posting.db"

def add_user(username,password,role):

    conn = sqlite3.connect(DB)

    hashed = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )

    conn.execute("""
    INSERT INTO users
    (username,password,role)
    VALUES (?,?,?)
    """,(
        username,
        hashed,
        role
    ))

    conn.commit()
    conn.close()

def login(username,password):

    conn = sqlite3.connect(DB)

    cur = conn.cursor()

    cur.execute("""
    SELECT password, role
    FROM users
    WHERE username=?
    """,(username,))

    user = cur.fetchone()

    conn.close()

    if user:

        saved_pw = user[0]

        if bcrypt.checkpw(
            password.encode(),
            saved_pw
        ):
            return user[1]

    return None