
from db_connector import connect_db
from user_manager import change_password
from utils.hashing import hash_password
from colorama import Fore, Style
import getpass


def view_all_users():
    conn = connect_db()
    if not conn: return
    cursor = conn.cursor()

    print(Fore.RED + "\n--- ADMIN AUDIT: ALL USERS ---" + Style.RESET_ALL)

    cursor.execute("SELECT id, username, role FROM users ORDER BY id")
    users = cursor.fetchall()

    if not users:
        print(Fore.YELLOW + "[!] No users found in the system." + Style.RESET_ALL)
        return

    print(Fore.CYAN + "ID | Username | Role" + Style.RESET_ALL)
    print("----------------------------")
    for user in users:
        print(f"{user[0]:<2} | {user[1]:<10} | {user[2].upper()}")

    print("----------------------------")
    cursor.close()
    conn.close()


def admin_reset_password():
    conn = connect_db()
    if not conn: return
    cursor = conn.cursor()

    print(Fore.RED + "\n--- ADMIN: RESET USER PASSWORD ---" + Style.RESET_ALL)
    target_username = input("Enter username whose password you want to reset: ")

    cursor.execute("SELECT id, role FROM users WHERE username = %s", (target_username,))
    target_user = cursor.fetchone()

    if not target_user:
        print(Fore.RED + "User not found." + Style.RESET_ALL)
        cursor.close()
        conn.close()
        return

    target_id, target_role = target_user

    if target_role == 'admin':
        print(Fore.RED + "Cannot reset another admin's password through this interface." + Style.RESET_ALL)
        cursor.close()
        conn.close()
        return

    new_password = getpass.getpass("Enter NEW password for the user: ")
    confirm_password = getpass.getpass("Confirm NEW password: ")

    if new_password != confirm_password:
        print(Fore.RED + "New passwords do not match. Operation cancelled." + Style.RESET_ALL)
        cursor.close()
        conn.close()
        return

    new_hash = hash_password(new_password)
    cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, target_id))
    conn.commit()
    print(Fore.GREEN + f"Password for {target_username} successfully reset by Admin." + Style.RESET_ALL)

    cursor.close()
    conn.close()
