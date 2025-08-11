import sqlite3
from datetime import datetime
def withdraw(conn, account_id, amount):
    if amount <= 0:
        return "Withdrawal amount must be positive."

    cursor = conn.cursor()

    # Check current balance
    cursor.execute("""
        SELECT balance FROM accounts WHERE account_id = ?
    """, (account_id,))
    result = cursor.fetchone()

    if not result:
        return "Account not found."

    current_balance = result[0]

    if current_balance < amount:
        return "Insufficient funds."

    # Update account balance
    cursor.execute("""
        UPDATE accounts
        SET balance = balance - ?
        WHERE account_id = ?
    """, (amount, account_id))

    # Log transaction
    cursor.execute("""
        INSERT INTO transactions (account_id, type, amount, timestamp)
        VALUES (?, 'withdrawal', ?, ?)
    """, (account_id, amount, datetime.now()))

    conn.commit()
    return f"Withdrew {amount:.2f} successfully."
