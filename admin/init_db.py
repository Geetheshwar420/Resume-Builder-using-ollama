import sqlite3
import bcrypt
import os

# --- Configuration ---
DB_PATH = "data/resume_builder.db"
ADMIN_USER = "geethu"
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "@Geethu2024")

def init_database():
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user' -- 'admin' or 'user'
    )
    """)

    # 2. Create Keys Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        api_key TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()
    print(f"🚀 Database initialized (schema only) at {DB_PATH}")

if __name__ == "__main__":
    init_database()
