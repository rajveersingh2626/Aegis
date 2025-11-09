import os
import getpass
from db_connector import connect_db
from utils.hashing import hash_password, verify_password
from colorama import Fore, Style
from admin_manager import view_all_users, admin_reset_password
from user_manager import change_password 
from user_manager import change_password, delete_account
from admin_manager import view_all_users, admin_reset_password

def display_resource_menu(user_role):
    print(Fore.CYAN + "\n─────────────────────────────────────────────" + Style.RESET_ALL)
    print(f"Welcome, {Fore.YELLOW}{user_role.upper()}!{Style.RESET_ALL} Available Actions:")
    print(Fore.CYAN + "─────────────────────────────────────────────" + Style.RESET_ALL)
    print(f"1. Link a new file (Path Registration)")
    print(f"2. View my files (Index Lookup)")
    print(f"3. Open linked file (Access Resource)")
    print(f"4. Delete a file link")

    if user_role == 'admin':
        print(Fore.RED + "\n--- [ADMIN] ---" + Style.RESET_ALL)
        print("5. View all users (Audit)")
        print("6. Change any user's password")

    print(Fore.CYAN + "─────────────────────────────────────────────" + Style.RESET_ALL)
    print("7. Change your password")
    print("8. Delete account")
    print(Fore.CYAN + "─────────────────────────────────────────────" + Style.RESET_ALL)


def link_new_file(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    file_name = input("Enter descriptive file name: ")
    file_path = input("Enter full file path (e.g., C:\\Users\\...): ")

    use_password = input("Do you want to add a secondary password for this link? (y/n): ").lower()
    file_password_hash = None

    if use_password == 'y':
        file_password = getpass.getpass("Enter file password: ")
        file_password_hash = hash_password(file_password)
        print(Fore.GREEN + "Secondary protection added." + Style.RESET_ALL)

    try:
        cursor.execute(
            "INSERT INTO user_files (user_id, file_name, file_path, file_password_hash) VALUES (%s, %s, %s, %s)",
            (user_id, file_name, file_path, file_password_hash)
        )
        conn.commit()
        print(Fore.GREEN + f"File link '{file_name}' registered successfully." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Database Error: {e}" + Style.RESET_ALL)
    finally:
        cursor.close()
        conn.close()


def view_linked_files(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, file_name, file_password_hash FROM user_files WHERE user_id = %s", (user_id,))
    files = cursor.fetchall()

    if not files:
        print(Fore.YELLOW + "\n[!] No files linked yet." + Style.RESET_ALL)
        return None

    print(Fore.CYAN + "\n─────────────────────────────────────────────" + Style.RESET_ALL)
    print(f"{Fore.CYAN}Your Linked Resources (ID | Name | Protected){Style.RESET_ALL}")
    print(Fore.CYAN + "─────────────────────────────────────────────" + Style.RESET_ALL)

    file_map = {}
    for i, file in enumerate(files):
        is_protected = "🔐" if file[2] else ""
        print(f"{i+1}. {file[1]} {is_protected}")
        file_map[i+1] = file[0]

    print(Fore.CYAN + "─────────────────────────────────────────────" + Style.RESET_ALL)
    return file_map


def open_linked_file(user_id):
    file_map = view_linked_files(user_id)
    if not file_map:
        return

    try:
        choice = int(input("Enter file number to open or '0' to go back: "))
        if choice == 0:
            return

        file_db_id = file_map.get(choice)
        if not file_db_id:
            print(Fore.RED + "Invalid selection." + Style.RESET_ALL)
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT file_name, file_path, file_password_hash FROM user_files WHERE id = %s",
            (file_db_id,)
        )
        file_record = cursor.fetchone()

        file_path = file_record[1]
        file_hash = file_record[2]

        if file_hash:
            entered_password = getpass.getpass(Fore.YELLOW + "Resource protected. Enter file password: " + Style.RESET_ALL)
            if not verify_password(entered_password, file_hash):
                print(Fore.RED + "Secondary password mismatch. Access denied." + Style.RESET_ALL)
                return

        print(Fore.GREEN + f"Access granted. Attempting to open '{file_record[0]}'..." + Style.RESET_ALL)

        if os.name == 'nt': # Windows
            os.startfile(file_path)
        elif os.uname().sysname == 'Darwin': # macOS
            os.system(f'open "{file_path}"')
        else: # Linux
            os.system(f'xdg-open "{file_path}"')

    except ValueError:
        print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)
    except FileNotFoundError:
        print(Fore.RED + f"File not found at path: {file_path}. The link may be outdated." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"An unexpected error occurred: {e}" + Style.RESET_ALL)
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()



def delete_file_link(user_id):
    file_map = view_linked_files(user_id)
    if not file_map:
        return

    conn = None
    cursor = None

    try:
        choice = int(input(Fore.YELLOW + "Enter file number to DELETE link or '0' to go back: " + Style.RESET_ALL))
        if choice == 0:
            return

        file_db_id = file_map.get(choice)
        if not file_db_id:
            print(Fore.RED + "Invalid selection." + Style.RESET_ALL)
            return

        # Confirmation step
        confirm = input(f"!!! WARNING: Are you sure you want to delete link #{choice} permanently? (yes/no): ").lower()
        if confirm == 'yes':

            conn = connect_db()
            if conn is None:
                return

            cursor = conn.cursor()

            cursor.execute("DELETE FROM user_files WHERE id = %s AND user_id = %s", (file_db_id, user_id))
            conn.commit()

            print(Fore.GREEN + "File link deleted successfully." + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "Action cancelled." + Style.RESET_ALL)

    except ValueError:
        print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"An error occurred during deletion: {e}" + Style.RESET_ALL)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()




def resource_menu(user):
    user_id = user['id']
    username = user['username']
    role = user['role']

    while True:
        display_resource_menu(role)
        choice = input(Fore.YELLOW + f"Enter choice ({role}): " + Style.RESET_ALL)

        if choice == '1':
            link_new_file(user_id)
        elif choice == '2':
            view_linked_files(user_id)
        elif choice == '3':
            open_linked_file(user_id)
        elif choice == '4':
            delete_file_link(user_id)
        elif choice == '7':
            change_password(user_id)
        elif choice == '8':
            delete_account_and_break = delete_account(user_id, username)
            if delete_account_and_break:
                break
        elif choice == '9':
            print(Fore.GREEN + f"\n[!] Session closed. Goodbye, {username}." + Style.RESET_ALL)
            break
        elif role == 'admin':
            if choice == '5':
                view_all_users()
            elif choice == '6':
                admin_reset_password()
            else:
                print(Fore.RED + "Invalid admin choice." + Style.RESET_ALL)

        else:
            print(Fore.RED + "Invalid choice or insufficient permissions." + Style.RESET_ALL)
