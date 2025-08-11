import sqlite3

def get_account_id(user_id, db_path='bank.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT account_id FROM accounts WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_balance(card_number: str = None, user_id: int = None, db_path='bank.db') -> float:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if card_number:
            cursor.execute("SELECT balance FROM accounts WHERE card_number = ?", (card_number,))
        elif user_id:
            cursor.execute("SELECT balance FROM accounts WHERE user_id = ?", (user_id,))
        else:
            raise ValueError("Either card_number or user_id must be provided.")

        result = cursor.fetchone()
        if result:
            return float(result[0])
        else:
            return 0.0

    except Exception as e:
        print(f"Error: {e}")
        return 0.0

    finally:
        conn.close()
        
