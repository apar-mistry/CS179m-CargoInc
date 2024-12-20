import os
import datetime

def log_action(username, action):
    # Define the desktop path and log directory
    current_year = datetime.datetime.now().year
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    log_dir = os.path.join(desktop_path, "logs")

    # Ensure the log directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file_path = os.path.join(log_dir, f"KeoghPorts{current_year}.txt")
    log_entry = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}   {username} {action}\n"

    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry)


def log_complete(action):
    # Define the desktop path and log directory
    current_year = datetime.datetime.now().year
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    log_dir = os.path.join(desktop_path, "logs")

    # Ensure the log directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file_path = os.path.join(log_dir, f"KeoghPorts{current_year}.txt")
    log_entry = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}   {action}\n"

    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry)


def operator_logs(username, log):
    current_year = datetime.datetime.now().year
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    log_dir = os.path.join(desktop_path, "logs")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file_path = os.path.join(log_dir, f"KeoghPorts{current_year}.txt")
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{time}   {username}    {log} \n"

    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry)
