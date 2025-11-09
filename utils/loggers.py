import datetime
import os

LOG_FILE = "aegis_activity.log"

def log_activity(username: str, action: str, success: bool = True):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "FAILURE"

    log_entry = f"[{timestamp}] [USER:{username}] [STATUS:{status}] - {action}\n"

    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
    except Exception as e:
        pass

def view_logs():
    if not os.path.exists(LOG_FILE):
        print("No activity logs found.")
        return

    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()

        print("\n--- LAST 10 SYSTEM ACTIVITIES ---")
        for line in lines[-10:]:
            print(line.strip())
        print("---------------------------------")

    except Exception as e:
        print(f"Error reading log file: {e}")
