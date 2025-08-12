import sqlite3
import os
from typing import Optional

DB_NAME = "bank.db"

class Session:
    current_user_id: Optional[int] = None

# One shared instance, imported everywhere
session = Session()

# Session file to store logged-in user between runs
SESSION_FILE = "session.txt"

def save_session(user_id):
    with open(SESSION_FILE, "w") as f:
        f.write(str(user_id))

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return None
    return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT UNIQUE NOT NULL,
            password  TEXT NOT NULL
        )
    """)

    # Accounts
    c.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            balance      REAL NOT NULL DEFAULT 0.0,
            account_type TEXT NOT NULL,
            card_number  TEXT UNIQUE,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # Transactions
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            txn_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            type       TEXT NOT NULL,
            amount     REAL NOT NULL,
            timestamp  TEXT NOT NULL,
            FOREIGN KEY(account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

def register_user(username: str, password: str):
    if not username or not password:
        return False, "Username and password are required."

    conn = get_connection()
    c = conn.cursor()

    # Reject duplicates
    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return False, "Username already exists."

    # Create user
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    user_id = c.lastrowid

    # Create default checking account
    c.execute(
        "INSERT INTO accounts (user_id, balance, account_type) VALUES (?, ?, 'checking')",
        (user_id, 0.0)
    )

    conn.commit()
    conn.close()

    # Auto-login for this run and save session
    session.current_user_id = user_id
    save_session(user_id)

    return True, f"Registration successful. Logged in as {username}."

def login_user(username: str, password: str):
    if not username or not password:
        return False, "Username and password are required."

    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT user_id FROM users WHERE username = ? AND password = ?",
        (username, password)
    )
    row = c.fetchone()
    conn.close()

    if row:
        session.current_user_id = row[0]
        save_session(row[0])
        return True, "Logged in."
    return False, "Incorrect username or password."

def logout_user():
    session.current_user_id = None
    clear_session()
    return "Logged out."

def is_logged_in() -> bool:
    return session.current_user_id is not None

def get_logged_in_user():
    return session.current_user_id

def get_username(user_id: int) -> str | None:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None
