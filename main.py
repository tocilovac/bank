from auth import register_user, login_user, logout_user, is_logged_in, get_logged_in_user
from service import get_balance, get_account_id
from deposit import deposit
from withdraw import withdraw
import sqlite3

def show_menu():
    print("\nWelcome to Terminal Banking")
    print("--------------------------------")
    print("1. Register")
    print("2. Login")
    print("3. Check Balance")
    print("4. Deposit")
    print("5. Withdraw")
    print("6. Logout")
    print("7. Exit")

while True:
    show_menu()
    choice = input("Choose an option (1-7): ").strip()

    if choice == '1':
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        success, message = register_user(username, password)
        print(message)

    elif choice == '2':
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        success, message = login_user(username, password)
        print(message)

    elif choice == '3':
        if is_logged_in():
            user_id = get_logged_in_user()
            balance = get_balance(user_id=user_id)
            print(f"Your balance is: ${balance:.2f}")
        else:
            print("You must log in first.")

    elif choice == '4':
        if is_logged_in():
            user_id = get_logged_in_user()
            account_id = get_account_id(user_id)
            if account_id is None:
                print("No account found for this user.")
            else:
                try:
                    amount = float(input("Enter deposit amount: "))
                    conn = sqlite3.connect('bank.db')
                    message = deposit(conn, account_id, amount)
                    conn.close()
                    print(message)
                except ValueError:
                    print("Invalid amount.")
        else:
            print("You must log in first.")

    elif choice == '5':
        if is_logged_in():
            user_id = get_logged_in_user()
            account_id = get_account_id(user_id)
            if account_id is None:
                print("No account found for this user.")
            else:
                try:
                    amount = float(input("Enter withdrawal amount: "))
                    conn = sqlite3.connect('bank.db')
                    message = withdraw(conn, account_id, amount)
                    conn.close()
                    print(message)
                except ValueError:
                    print("Invalid amount.")
        else:
            print("You must log in first.")

    elif choice == '6':
        if is_logged_in():
            print(logout_user())
        else:
            print("No user is currently logged in.")

    elif choice == '7':
        print("Goodbye!")
        break

    else:
        print("Invalid choice. Please enter a number between 1 and 7.")
