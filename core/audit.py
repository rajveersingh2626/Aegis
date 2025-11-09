
import logging
import os
from colorama import Fore, Style

LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'audit.log')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s | (levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_event(user: str, action: str, details: str=""):
    log_message = f"users'{user}' action='{action}' details='{details}'"
    logging.info(log_message)

def read_audit_logs(limit: int = 100) -> list[str]:
    if not os.path.exists(LOG_FILE):
        return [f"{Fore.YELLOW}[LOGGING] Audit file not found.{Style.RESET_ALL}"]

    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            latest_logs = [line.strip() for line in lines[-limit:][::-1]]

            return latest_logs

    except Exception as e:
        return [f"{Fore.RED}[CRITICAL LOG ERROR] Failed to read log file: {e}{Style.RESET_ALL}"]
