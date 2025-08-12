import sqlite3
import auth
import service
import deposit as deposit_mod
import withdraw as withdraw_mod

def open_db():
    conn = sqlite3.connect(auth.DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def prompt_nonempty(label: str) -> str:
    while True:
        val = input(label).strip()
        if val:
            return val
        print("Value cannot be empty.")

def prompt_amount(label: str) -> float:
    while True:
        raw = input(label).strip()
        try:
            amount = float(raw)
            if amount <= 0:
                print("Amount must be greater than 0.")
                continue
            return amount
        except ValueError:
            print("Please enter a valid number.")

def show_auth_menu():
    print("\n=== Welcome ===")
    print("1) Register")
    print("2) Login")
    print("0) Exit")

def show_user_menu(username: str):
    print(f"\n=== Banking (logged in as {username}) ===")
    print("1) Check balance")
    print("2) Deposit")
    print("3) Withdraw")
    print("4) Transfer")
    print("9) Logout")
    print("0) Exit")

def handle_check_balance():
    user_id = auth.get_logged_in_user()
    if not user_id:
        print("You must login first.")
        return
    bal = service.get_balance(user_id=user_id, db_path=auth.DB_NAME)
    print(f"Current balance: {bal:.2f}")

def handle_deposit():
    user_id = auth.get_logged_in_user()
    if not user_id:
        print("You must login first.")
        return
    amount = prompt_amount("Amount to deposit: ")

    account_id = service.get_account_id(user_id, db_path=auth.DB_NAME)
    if account_id is None:
        print("Account not found.")
        return

    conn = open_db()
    try:
        msg = deposit_mod.deposit(conn, account_id, amount)
        print(msg)
    finally:
        conn.close()

def handle_withdraw():
    user_id = auth.get_logged_in_user()
    if not user_id:
        print("You must login first.")
        return
    amount = prompt_amount("Amount to withdraw: ")

    account_id = service.get_account_id(user_id, db_path=auth.DB_NAME)
    if account_id is None:
        print("Account not found.")
        return

    conn = open_db()
    try:
        msg = withdraw_mod.withdraw(conn, account_id, amount)
        print(msg)
    finally:
        conn.close()

def handle_transfer():
    user_id = auth.get_logged_in_user()
    if not user_id:
        print("You must login first.")
        return

    to_username = prompt_nonempty("Transfer to username: ")
    amount = prompt_amount("Amount to transfer: ")

    # Resolve recipient
    conn = open_db()
    c = conn.cursor()

    c.execute("SELECT user_id FROM users WHERE username = ?", (to_username,))
    row_to = c.fetchone()
    if not row_to:
        conn.close()
        print("Target user does not exist.")
        return
    to_user_id = int(row_to[0])

    if to_user_id == user_id:
        conn.close()
        print("Cannot transfer to the same account.")
        return

    from_account_id = service.get_account_id(user_id, db_path=auth.DB_NAME)
    to_account_id = service.get_account_id(to_user_id, db_path=auth.DB_NAME)
    if from_account_id is None or to_account_id is None:
        conn.close()
        print("One of the accounts was not found.")
        return

    try:
        conn.execute("BEGIN IMMEDIATE")

        # Check balance
        c.execute("SELECT balance FROM accounts WHERE account_id = ?", (from_account_id,))
        row_bal = c.fetchone()
        if not row_bal:
            conn.rollback()
            conn.close()
            print("Your account was not found.")
            return

        balance = float(row_bal[0])
        if amount > balance:
            conn.rollback()
            conn.close()
            print(f"Insufficient funds. Available: {balance:.2f}")
            return

        # Deduct
        c.execute("UPDATE accounts SET balance = balance - ? WHERE account_id = ?", (amount, from_account_id))

        # Credit
        c.execute("UPDATE accounts SET balance = balance + ? WHERE account_id = ?", (amount, to_account_id))

        # Log transactions
        c.execute("""
            INSERT INTO transactions (account_id, type, amount, timestamp)
            VALUES (?, 'transfer_out', ?, datetime('now'))
        """, (from_account_id, amount))
        c.execute("""
            INSERT INTO transactions (account_id, type, amount, timestamp)
            VALUES (?, 'transfer_in', ?, datetime('now'))
        """, (to_account_id, amount))

        conn.commit()
        print(f"Transferred {amount:.2f} to {to_username}.")
    except Exception as e:
        conn.rollback()
        print(f"Transfer failed: {e}")
    finally:
        conn.close()

def main():
    auth.init_db()

    # Load saved session
    saved_user = auth.load_session()
    if saved_user:
        auth.session.current_user_id = saved_user

    while True:
        if not auth.is_logged_in():
            show_auth_menu()
            choice = input("Choose: ").strip()
            if choice == "1":
                username = prompt_nonempty("New username: ")
                password = prompt_nonempty("New password: ")
                ok, msg = auth.register_user(username, password)
                print(msg)
            elif choice == "2":
                username = prompt_nonempty("Username: ")
                password = prompt_nonempty("Password: ")
                ok, msg = auth.login_user(username, password)
                print(msg)
            elif choice == "0":
                print("Goodbye.")
                break
            else:
                print("Invalid choice.")
        else:
            uid = auth.get_logged_in_user()
            uname = auth.get_username(uid) or "user"
            show_user_menu(uname)
            choice = input("Choose: ").strip()

            if choice == "1":
                handle_check_balance()
            elif choice == "2":
                handle_deposit()
            elif choice == "3":
                handle_withdraw()
            elif choice == "4":
                handle_transfer()
            elif choice == "9":
                print(auth.logout_user())
            elif choice == "0":
                print("Goodbye.")
                break
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    main()
