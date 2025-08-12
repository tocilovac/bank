# deposit.py
import sqlite3
from datetime import datetime

def deposit(conn, account_id, amount):
    if amount <= 0:
        return "Deposit amount must be positive."

    cursor = conn.cursor()

    # Update balance
    cursor.execute("""
        UPDATE accounts
        SET balance = balance + ?
        WHERE account_id = ?
    """, (amount, account_id))

    if cursor.rowcount == 0:
        return "Account not found."

    # Log transaction
    cursor.execute("""
        INSERT INTO transactions (account_id, type, amount, timestamp)
        VALUES (?, 'deposit', ?, ?)
    """, (account_id, amount, datetime.now().isoformat(timespec="seconds")))

    conn.commit()
    return f"Deposited {amount:.2f} successfully."
