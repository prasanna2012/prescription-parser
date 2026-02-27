import sqlite3
import hashlib

DB_NAME = "users.db"

# --- Create tables ---
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    file_name TEXT,
    extracted_text TEXT,
    simplified_text TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()
conn.close()

# --- Password hashing ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- User functions ---
def add_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user is not None

# --- History functions ---
def save_history(username, file_name, extracted_text, simplified_text):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO history (username, file_name, extracted_text, simplified_text) VALUES (?, ?, ?, ?)",
        (username, file_name, extracted_text, simplified_text)
    )
    conn.commit()
    conn.close()

def get_user_history(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT file_name, extracted_text, simplified_text, timestamp FROM history WHERE username=? ORDER BY timestamp DESC",
        (username,)
    )
    rows = c.fetchall()
    conn.close()
    history = []
    for row in rows:
        history.append({
            "file_name": row[0],
            "extracted_text": row[1],
            "simplified_text": row[2],
            "timestamp": row[3]
        })
    return history