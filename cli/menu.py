from colorama import Fore, Style

def display_main_entry_menu():
    print(Fore.CYAN + "\n─────────────────────────────────────────────" + Style.RESET_ALL)
    print(Fore.CYAN + "                 AEGIS                " + Style.RESET_ALL)
    print(Fore.CYAN + "─────────────────────────────────────────────" + Style.RESET_ALL)
    print("A modular security system demonstrating RBAC and auditing.")
    print(Fore.CYAN + "─────────────────────────────────────────────" + Style.RESET_ALL)
    print(f"1. {Fore.YELLOW}Login{Style.RESET_ALL}")
    print(f"2. {Fore.YELLOW}Register{Style.RESET_ALL}")
    print(f"3. {Fore.RED}Exit{Style.RESET_ALL}")
    print(Fore.CYAN + "─────────────────────────────────────────────" + Style.RESET_ALL)

def display_dashboard_menu(user_role):
    print(Fore.CYAN + "\n─────────────────────────────────────────────" + Style.RESET_ALL)
    print(f"AEGIS DASHBOARD ({Fore.YELLOW}{user_role.upper()}{Style.RESET_ALL})")
    print(Fore.CYAN + "─────────────────────────────────────────────" + Style.RESET_ALL)
    print(f"1. Link a new resource")
    print(f"2. View my resources")
    print(f"3. Access a linked file")
    print(f"4. Change my password")

    if user_role == 'admin':
        print(Fore.RED + "\n--- [ADMIN CONTROLS] ---" + Style.RESET_ALL)
        print("5. View all users (Audit)")
        print("6. View access logs (Audit)")
        print("7. Reset user password")

    print(Fore.CYAN + "─────────────────────────────────────────────" + Style.RESET_ALL)
    print("9. Logout")
    print(Fore.CYAN + "─────────────────────────────────────────────" + Style.RESET_ALL)
