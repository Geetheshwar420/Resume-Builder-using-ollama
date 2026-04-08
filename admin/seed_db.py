import sqlite3
import bcrypt
import os

# --- Configuration ---
DB_PATH = "data/resume_builder.db"

# Default Admin Details (from Global Rules)
ADMIN_USER = "geethu"
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "@Geethu2024")

def seed_database():
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Database {DB_PATH} not found. Run init_db.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Seed Super Admin
    cursor.execute("SELECT * FROM users WHERE username = ?", (ADMIN_USER,))
    if not cursor.fetchone():
        hashed = bcrypt.hashpw(ADMIN_PASS.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                       (ADMIN_USER, hashed, 'admin'))
        print(f"✅ Admin user '{ADMIN_USER}' seeded successfully.")
    else:
        print(f"ℹ️ Admin user '{ADMIN_USER}' already exists.")

    # 2. Add Test Login Details (Optional - for user reference)
    print("\n--- SEED DATA ---")
    print(f"ADMIN_USERNAME: {ADMIN_USER}")
    print(f"ADMIN_PASSWORD: {ADMIN_PASS}")
    print("-----------------\n")

    conn.commit()
    conn.close()
    print("🚀 Seeding complete.")

if __name__ == "__main__":
    seed_database()
