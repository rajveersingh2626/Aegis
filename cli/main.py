
import sys
import getpass
from core.db import initialize_db_and_connect
from core.auth import db_register_user, db_login_user
from cli.menu import display_main_entry_menu, display_dashboard_menu
from cli.commands import (
    view_access_logs,
    link_new_resource,
    view_linked_resources,
    access_linked_resource,
    delete_linked_resource,
    change_user_password,
    delete_user_account,
    view_all_users,
    admin_reset_user_password
)

from colorama import Fore, Style


def run_dashboard(user):
    while True:
        display_dashboard_menu(user['role'])
        choice = input(Fore.YELLOW + f"Enter choice ({user['role']}): " + Style.RESET_ALL)

        if choice == '1':
            link_new_resource(user)
        elif choice == '2':
            view_linked_resources(user)
        elif choice == '3':
            access_linked_resource(user)
        elif choice == '4':
            change_user_password(user)

        elif choice in ('5', '6', '7'):
            if user['role'] == 'admin':
                if choice == '5':
                    view_all_users()
                elif choice == '6':
                    view_access_logs()
                elif choice == '7':
                    admin_reset_user_password(user)
            else:
                print(Fore.RED + "Invalid choice or insufficient permissions." + Style.RESET_ALL)

        elif choice == '9':
            print(Fore.GREEN + f"\n[!] Session closed. Goodbye, {user['username']}." + Style.RESET_ALL)
            break

        else:
            print(Fore.RED + "Invalid choice or insufficient permissions." + Style.RESET_ALL)


def handle_register():
    print(Fore.CYAN + "\n--- NEW USER REGISTRATION ---" + Style.RESET_ALL)
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    result = db_register_user(username, password)

    if result is True:
        print(Fore.GREEN + f"Registration successful! Welcome, {username}." + Style.RESET_ALL)
    elif result == "EXISTS":
        print(Fore.RED + "Username already exists! Please try another." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Registration failed due to a system error." + Style.RESET_ALL)

def handle_login():
    user = db_login_user(
        input("Username: "),
        getpass.getpass("Password: ")
    )
    if user:
        print(Fore.GREEN + f"Login successful. Token: {user['token'][:8]}..." + Style.RESET_ALL)
        run_dashboard(user)
        pass
    else:
        print(Fore.RED + "Invalid credentials. Access denied." + Style.RESET_ALL)


def main():
    print("\n[!] Initializing Aegis System...")

    conn = initialize_db_and_connect()
    if conn is None:
        print("\n[CRITICAL] Could not connect to the database. Exiting.")
        sys.exit(1)

    conn.close()

    print(Fore.GREEN + "[+] System Ready." + Style.RESET_ALL)

    while True:
        display_main_entry_menu()
        choice = input(Fore.YELLOW + "Enter choice: " + Style.RESET_ALL)

        if choice == '1':
            handle_login()
        elif choice == '2':
            handle_register()
        elif choice == '3':
            print(Fore.GREEN + "\nGoodbye. Aegis shutting down." + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "Invalid option. Please choose 1, 2, or 3." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
