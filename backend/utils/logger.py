import os
import datetime

def log_action(username, action):
    # Define the desktop path and log directory
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    log_dir = os.path.join(desktop_path, "logs")

    # Ensure the log directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Define the log file path
    log_file_path = os.path.join(log_dir, "login_logs.txt")

    # Create log entry with the date and time
    log_entry = f"{username} {action} at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    # Append the log entry to the log file
    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry)