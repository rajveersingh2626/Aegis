import logging
from datetime import datetime
import os

LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'audit.log')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_event(user: str, action: str, details: str = ""):

    log_message = f"user='{user}' action='{action}' details='{details}'"

    logging.info(log_message)

def read_audit_logs(limit: int = 20):
    try:
        with open(LOG_FILE, 'r') as f:
            return f.readlines()[-limit:]
    except FileNotFoundError:
        return ["--- Audit log file not found. ---"]
    except Exception as e:
        return [f"--- Error reading log file: {e} ---"]
