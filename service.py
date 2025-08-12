# service.py
import sqlite3

def get_account_id(user_id, db_path='bank.db'):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute("SELECT account_id FROM accounts WHERE user_id = ? AND account_type = 'checking'", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_balance(card_number: str = None, user_id: int = None, db_path='bank.db') -> float:
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        if card_number:
            # Requires accounts.card_number column (created in auth.init_db)
            cursor.execute("SELECT balance FROM accounts WHERE card_number = ?", (card_number,))
        elif user_id:
            cursor.execute("SELECT balance FROM accounts WHERE user_id = ? AND account_type = 'checking'", (user_id,))
        else:
            raise ValueError("Either card_number or user_id must be provided.")

        result = cursor.fetchone()
        return float(result[0]) if result else 0.0

    except Exception as e:
        print(f"Error: {e}")
        return 0.0

    finally:
        try:
            conn.close()
        except Exception:
            pass
