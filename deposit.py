import sqlite3
from datetime import datetime
def deposit(conn, account_id, amount):
    if amount <= 0:
        return "deposit must be positive."
    
    cursor = conn.cursor()
    
    cursor.execute("""
        update accounts
        set balance = balance + ?
        where account_id = ?
    """, (amount, account_id))
    
    cursor.execute("""
        insert into transactions (account_id, type, amount, timestamp)
        values (?, 'deposit', ?, ?)
    """, (account_id, amount, datetime.now()))
    
    conn.commit()
    return f"deposited {amount:.2f} successfully."





