import streamlit as st
import sqlite3
import bcrypt
import pandas as pd
import uuid
import os
import time

# --- Configuration ---
DB_PATH = "data/resume_builder.db"

st.set_page_config(page_title="AI Resume Portal", layout="wide", initial_sidebar_state="expanded")

# --- Database Helpers ---
def get_db_connection():
    # Retry logic if file is being initialized
    for _ in range(5):
        if os.path.exists(DB_PATH):
            break
        time.sleep(1)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed_pw):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_pw.encode('utf-8'))

# --- Auth Logic ---
def login_user(username, password):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if user and check_password(password, user["password_hash"]):
        st.session_state["user_id"] = user["id"]
        st.session_state["username"] = user["username"]
        st.session_state["role"] = user["role"]
        st.success(f"Welcome, {username}!")
        return True
    return False

def create_user(username, password):
    conn = get_db_connection()
    try:
        hashed = hash_password(password)
        conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                     (username, hashed, 'user'))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# --- Main Logic ---
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

# Sidebar Logout
if st.session_state["user_id"]:
    st.sidebar.title(f"👤 {st.session_state['username'].title()}")
    st.sidebar.info(f"Role: {st.session_state['role'].upper()}")
    if st.sidebar.button("Logout"):
        st.session_state["user_id"] = None
        st.rerun()

# --- Authentication Pages ---
if not st.session_state["user_id"]:
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    
    with tab1:
        st.header("🔑 Login")
        l_user = st.text_input("Username", key="l_user")
        l_pass = st.text_input("Password", type="password", key="l_pass")
        if st.button("Login"):
            if login_user(l_user, l_pass):
                st.rerun()
            else:
                st.error("Invalid username or password.")
                
    with tab2:
        st.header("✨ Register")
        r_user = st.text_input("New Username", key="r_user")
        r_pass = st.text_input("New Password", type="password", key="r_pass")
        if st.button("Sign Up"):
            if len(r_pass) < 4:
                st.warning("Password must be at least 4 characters.")
            elif create_user(r_user, r_pass):
                st.success("Account created! Please login.")
            else:
                st.error("Username already taken.")

# --- Dashboard ---
else:
    st.title("🛡️ API Key Control Center")
    st.markdown("---")
    
    # 🌟 SUPER ADMIN VIEW
    if st.session_state["role"] == "admin":
        st.subheader("🌐 Global Configuration (Super Admin)")
        conn = get_db_connection()
        
        # 1. User Management
        with st.expander("Manage All Users"):
            users_df = pd.read_sql("SELECT id, username, role FROM users", conn)
            st.table(users_df)
            
        # 2. Key Monitoring
        st.subheader("🔑 Global Keys (All Users)")
        keys_query = """
        SELECT keys.api_key, users.username, keys.description, keys.created_at, keys.id
        FROM keys JOIN users ON keys.user_id = users.id
        """
        all_keys_df = pd.read_sql(keys_query, conn)
        if not all_keys_df.empty:
            st.dataframe(all_keys_df, hide_index=True, use_container_width=True)
            
            # Global Revocation
            st.markdown("### ❌ Emergency Revocation")
            key_to_revoke = st.selectbox("Select Key to Terminate", all_keys_df["api_key"].tolist())
            if st.button("Revoke Key (Global)"):
                conn.execute("DELETE FROM keys WHERE api_key = ?", (key_to_revoke,))
                conn.commit()
                st.success(f"Key {key_to_revoke[:8]}... revoked globally.")
                st.rerun()
        else:
            st.info("No keys found in system.")
        conn.close()
        st.markdown("---")

    # 👤 REGULAR USER VIEW (or also shown to admin for their own keys)
    st.subheader("Your Personal API Keys")
    
    conn = get_db_connection()
    col_gen, col_list = st.columns([1, 2])
    
    with col_gen:
        st.markdown("### Generate New Key")
        key_desc = st.text_input("Application/Device Name", placeholder="e.g., My Laptop")
        if st.button("Generate ✨"):
            if key_desc:
                new_key = str(uuid.uuid4())
                conn.execute("INSERT INTO keys (api_key, user_id, description) VALUES (?, ?, ?)", 
                             (new_key, st.session_state["user_id"], key_desc))
                conn.commit()
                st.success("🎉 New Key Generated!")
                st.code(new_key, language="text")
                st.info("Copy the key above. For security, you can also view it in the section to the right.")
            else:
                st.warning("Please provide a description.")
                
    with col_list:
        st.markdown("### Active Keys")
        my_keys = pd.read_sql("SELECT api_key, description, created_at FROM keys WHERE user_id = ?", 
                              conn, params=(st.session_state["user_id"],))
        
        if not my_keys.empty:
            st.table(my_keys)
            
            # Key Copy Helper
            st.markdown("### 📋 Copy Key")
            key_to_copy = st.selectbox("Select Key to Copy", my_keys["api_key"].tolist(), key="copy_sel")
            st.code(key_to_copy, language="text")

            # Revocation
            st.markdown("### ❌ Revoke Access")
            key_to_del = st.selectbox("Key to Terminate", my_keys["api_key"].tolist(), key="rev_sel")
            if st.button("Revoke Access"):
                conn.execute("DELETE FROM keys WHERE api_key = ? AND user_id = ?", 
                             (key_to_del, st.session_state["user_id"]))
                conn.commit()
                st.success("Key revoked.")
                st.rerun()
        else:
            st.info("No active keys yet.")
            
    conn.close()

if __name__ == "__main__":
    pass
