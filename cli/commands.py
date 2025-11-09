import os
import getpass
from colorama import Fore, Style
from core.db import initialize_db_and_connect
from core.auth import verify_password
from core.audit import log_event, read_audit_logs
from core.encryption import encrypt_data, decrypt_data

def link_new_resource(user):
    conn = initialize_db_and_connect()
    if not conn: return
    cursor = conn.cursor()

    print(Fore.CYAN + "\n--- LINK NEW RESOURCE ---" + Style.RESET_ALL)
    resource_name = input("Enter descriptive name for the resource: ")
    resource_path = input("Enter full file/network path: ")

    encrypted_path = encrypt_data(resource_path)

    use_password = input("Add secondary password protection? (y/n): ").lower()
    secondary_secret = None

    if use_password == 'y':
        secondary_secret = getpass.getpass("Enter secret protection key: ")
        print(Fore.GREEN + "Secondary protection enabled." + Style.RESET_ALL)
    try:
        cursor.execute(
            "INSERT INTO resources (user_id, name, encrypted_path, secondary_secret) VALUES (%s, %s, %s, %s)",
            (user['id'], resource_name, encrypted_path, secondary_secret)
        )
        conn.commit()
        print(Fore.GREEN + f"Resource link '{resource_name}' registered and path encrypted successfully." + Style.RESET_ALL)
    except Exception as e: 
        print(Fore.RED + f"Database Error: {e}" + Style.RESET_ALL)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()




    try:
        cursor.execute(
            "INSERT INTO resources (user_id, name, encrypted_path, secondary_secret) VALUES (%s, %s, %s, %s)",
            (user['id'], resource_name, encrypted_path, secondary_secret)
        )
        conn.commit()
        print(Fore.GREEN + f"Resource link '{resource_name}' registered successfully." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Database Error: {e}" + Style.RESET_ALL)
    finally:
        cursor.close()
        conn.close()


def view_all_users():
    conn = initialize_db_and_connect()
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
    for user_record in users:
        print(f"{user_record[0]:<2} | {user_record[1]:<10} | {user_record[2].upper()}")

    print("----------------------------")
    cursor.close()
    conn.close()


def view_linked_resources(user):
    conn = initialize_db_and_connect()
    if not conn: return None
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, secondary_secret FROM resources WHERE user_id = %s", (user['id'],))
    resources = cursor.fetchall()

    if not resources:
        print(Fore.YELLOW + "\n[!] No resources linked yet. Use option 1 to add one." + Style.RESET_ALL)
        cursor.close()
        conn.close()
        return None

    print(Fore.CYAN + "\n─────────────────────────────────────────────" + Style.RESET_ALL)
    print(f"{Fore.CYAN}Your Linked Resources (ID | Name | Protected){Style.RESET_ALL}")
    print(Fore.CYAN + "─────────────────────────────────────────────" + Style.RESET_ALL)

    resource_map = {}
    for i, resource in enumerate(resources):
        is_protected = "[LOCK]" if resource[2] else ""
        print(f"{i+1}. {resource[1]} {is_protected}")
        resource_map[i+1] = resource[0]

    print(Fore.CYAN + "─────────────────────────────────────────────" + Style.RESET_ALL)
    cursor.close()
    conn.close()

    return resource_map


def access_linked_resource(user):
    resource_map = view_linked_resources(user)
    if not resource_map:
        return

    conn = None
    cursor = None

    try:
        choice = int(input("Enter resource number to open or '0' to go back: "))
        if choice == 0:
            return

        resource_db_id = resource_map.get(choice)
        if not resource_db_id:
            print(Fore.RED + "Invalid selection." + Style.RESET_ALL)
            return

        conn = initialize_db_and_connect()
        if not conn: return
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name, encrypted_path, secondary_secret FROM resources WHERE id = %s AND user_id = %s",
            (resource_db_id, user['id'])
        )
        resource_record = cursor.fetchone()
        resource_name = resource_record[0]
        encrypted_path = resource_record[1]
        secondary_secret = resource_record[2]

        resource_path = decrypt_data(encrypted_path)

        if resource_path == "ERROR: DECRYPTION FAILED":
            print(Fore.RED + "Critical decryption failure. Resource link is unusable." + Style.RESET_ALL)
            return

        if secondary_secret:
            entered_password = getpass.getpass(Fore.YELLOW + "Resource protected. Enter secret key: " + Style.RESET_ALL)

            if entered_password != secondary_secret:
                log_event(user['username'], 'ACCESS_FAIL', f"ResourceID={resource_db_id}, Reason=SecretMismatch")
                print(Fore.RED + "Secret key mismatch. Access denied." + Style.RESET_ALL)
                return


        print(Fore.GREEN + f"Access granted. Attempting to open '{resource_record[0]}'..." + Style.RESET_ALL)
        log_event(user['username'], 'ACCESS_SUCCESS', f"Resource='{resource_record[0]}', Path={resource_path}")


        if os.name == 'nt': # Windows
            os.startfile(resource_path)
        elif os.uname().sysname == 'Darwin': # macOS
            os.system(f'open "{resource_path}"')
        else: # Linux
            os.system(f'xdg-open "{resource_path}"')

    except ValueError:
        print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)
    except FileNotFoundError:
        print(Fore.RED + f"Resource path not found: {resource_path}. Link may be outdated." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"An unexpected error occurred: {e}" + Style.RESET_ALL)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def delete_linked_resource(user):
    resource_map = view_linked_resources(user)
    if not resource_map:
        return

    conn = None
    cursor = None

    try:
        choice = input(Fore.YELLOW + "\nEnter resource number to DELETE link or '0' to go back: " + Style.RESET_ALL)
        if choice == '0':
            return

        try:
            choice_int = int(choice)
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)
            return

        resource_db_id = resource_map.get(choice_int)
        if not resource_db_id:
            print(Fore.RED + "Invalid selection." + Style.RESET_ALL)
            return

        confirm = input(f"Are you sure you want to delete resource link #{choice}? (yes/no): ").lower()
        if confirm == 'yes':

            conn = initialize_db_and_connect()
            if not conn: return
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM resources WHERE id = %s AND user_id = %s",
                (resource_db_id, user['id'])
            )
            conn.commit()

            print(Fore.GREEN + "Resource link deleted successfully." + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "Action cancelled." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + f"An error occurred during deletion: {e}" + Style.RESET_ALL)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def delete_user_account(user):
    print(Fore.RED + "\n!!! DANGER ZONE: ACCOUNT DELETION !!!" + Style.RESET_ALL)

    confirm_username = input(f"Type your username '{user['username']}' to proceed: ")
    if confirm_username != user['username']:
        print(Fore.YELLOW + "Action cancelled. Username mismatch." + Style.RESET_ALL)
        return

    password = getpass.getpass("Enter your password to authorize permanent deletion: ")

    result = db_delete_account(user['id'], password)

    if result is True:
        print(Fore.RED + f"Account for {user['username']} and all resources permanently deleted." + Style.RESET_ALL)
        print(Fore.RED + "Exiting session..." + Style.RESET_ALL)
        return True # Signal main loop to break
    elif result is False:
        print(Fore.RED + "Password incorrect. Deletion failed." + Style.RESET_ALL)
        return False
    else:
        print(Fore.RED + "System error during account deletion." + Style.RESET_ALL)
        return False



def change_user_password(user):
    print(Fore.CYAN + "\n--- CHANGE PASSWORD ---" + Style.RESET_ALL)

    old_password = getpass.getpass("Enter current password: ")
    new_password = getpass.getpass("Enter new password: ")
    confirm_password = getpass.getpass("Confirm new password: ")

    if new_password != confirm_password:
        print(Fore.RED + "New passwords do not match. Action cancelled." + Style.RESET_ALL)
        return

    if len(new_password) < 6: # Basic check
        print(Fore.RED + "New password must be at least 6 characters long." + Style.RESET_ALL)
        return

    result = db_change_password(user['id'], old_password, new_password)

    if result is True:
        print(Fore.GREEN + "Password updated successfully! Session remains active." + Style.RESET_ALL)
    elif result is False:
        print(Fore.RED + "Current password incorrect. Update failed." + Style.RESET_ALL)
    else:
        print(Fore.RED + "System error during password update." + Style.RESET_ALL)



def view_access_logs():
    print(Fore.RED + "\n--- ADMIN AUDIT: LATEST ACCESS LOGS (Last 20 entries) ---" + Style.RESET_ALL)

    logs = read_audit_logs(limit=20)

    if not logs or logs == ["--- Audit log file not found. ---"]:
        print(Fore.YELLOW + "Log file is empty or missing." + Style.RESET_ALL)
        return

    for line in logs:
        print(line.strip())
    print(Fore.RED + "---------------------------------------------------------" + Style.RESET_ALL)




def admin_reset_user_password(admin_user):
    print(Fore.RED + "\n--- ADMIN PASSWORD RESET ---" + Style.RESET_ALL)
    target_username = input("Enter username to reset password for: ")

    if target_username == admin_user['username']:
        print(Fore.YELLOW + "Use 'Change Password' (Choice 4) to modify your own account." + Style.RESET_ALL)
        return

    new_password = getpass.getpass("Enter new password for target user: ")
    confirm_password = getpass.getpass("Confirm new password: ")

    if new_password != confirm_password:
        print(Fore.RED + "New passwords do not match. Action cancelled." + Style.RESET_ALL)
        return

    if len(new_password) < 6:
        print(Fore.RED + "New password must be at least 6 characters long." + Style.RESET_ALL)
        return

    result = db_admin_reset_password(target_username, new_password)

    if result is True:
        log_event(admin_user['username'], 'ADMIN_PW_RESET_SUCCESS', f'Target={target_username}')
        print(Fore.GREEN + f"Successfully reset password for {target_username}." + Style.RESET_ALL)
    elif result is False:
        print(Fore.RED + "Target username not found." + Style.RESET_ALL)
    else:
        print(Fore.RED + "System error during password reset." + Style.RESET_ALL)
