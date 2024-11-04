from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)  # Allow CORS for requests from frontend

# Define the upload directory
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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

# New route for uploading a file
@app.route('/api/upload', methods=['POST'])
def upload_file():
    # Check if a file part is in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # Check if a file was selected and has the correct extension
    if file.filename == '' or not file.filename.endswith('.txt'):
        return jsonify({"error": "Invalid file type. Only .txt files are allowed."}), 400

    # Generate a unique filename and save the file
    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    return jsonify({"message": "File uploaded successfully", "filename": filename}), 200

if __name__ == '__main__':
    app.run(port=5000)  # Flask backend will run on port 5000