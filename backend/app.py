from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime
app = Flask(__name__)
CORS(app)  # Allow CORS for requests from frontend

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello from Flask!"})

@app.route('/api/log_login', methods=['POST'])
def log_login():
    data = request.get_json()
    username = data.get('username')

    # Define the desktop path and log directory
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    log_dir = os.path.join(desktop_path, "logs")

    # Ensure the log directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Define the log file path
    log_file_path = os.path.join(log_dir, "login_logs.txt")

    # Create log entry with the date and time
    log_entry = f"{username} logged in at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    # Append the log entry to the log file
    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry)

    return jsonify({"message": "Log created successfully"}), 200

@app.route('/api/log_logout', methods=['POST'])
def log_logout():
    data = request.get_json()
    username = data.get('username')

    # Define the desktop path and log directory
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    log_dir = os.path.join(desktop_path, "logs")

    # Ensure the log directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Define the log file path
    log_file_path = os.path.join(log_dir, "login_logs.txt")

    # Create log entry with the date and time
    log_entry = f"{username} logged out at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    # Append the log entry to the log file
    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry)

    return jsonify({"message": "Log created successfully"}), 200

if __name__ == '__main__':
    app.run(port=5000)  # Flask backend will run on port 5000