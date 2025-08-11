import sqlite3

DB_name = 'bank.db'
current_user_id = None

def register_user(username, password):
    conn = sqlite3.connect(DB_name)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists."

    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    user_id = cursor.lastrowid  # Get the newly created user's ID

    # Create account with initial balance
    cursor.execute("INSERT INTO accounts (user_id, balance) VALUES (?, ?)", (user_id, 0.0))

    conn.commit()
    conn.close()
    return True, "Registration successful."

def login_user(username, password):
    global current_user_id
    conn = sqlite3.connect(DB_name)
    cursor = conn.cursor()

    cursor.execute("select user_id from users where username = ? and password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()

    if result:
        current_user_id = result[0]
        return True, f"loggin in as {username}."
    else:
        return False, "incorrect username or password."

def logout_user():
    global current_user_id
    current_user_id = None
    return "youve been logged out."

def is_logged_in():
    return current_user_id is not None

def get_logged_in_user():
    return current_user_id


