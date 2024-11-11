from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)  # Allow CORS for requests from frontend

# Define the upload directory and temporary storage for grid data
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
grid_data = None  # Temporary variable to store parsed grid data

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


# Route for uploading a file
@app.route('/api/upload', methods=['POST'])
def upload_file():
    global grid_data  # Use the global variable to store data temporarily

    # Check if a file part is in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # Check if a file was selected and has the correct extension
    if file.filename == '' or not file.filename.endswith('.txt'):
        return jsonify({"error": "Invalid file type. Only .txt files are allowed."}), 400
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

    log_dir = os.path.join(desktop_path, "logs")

    # Ensure the log directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Define the log file path
    log_file_path = os.path.join(log_dir, "login_logs.txt")

    # Create log entry with the date and time
    log_entry = f"{request.headers.get("Username")} uploaded manifest: {file.filename} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    # Append the log entry to the log file
    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry)
    # Generate a unique filename and save the file
    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Parse the file content into structured data for the grid
    structured_data = []
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split(', ')
            position = parts[0].strip("[]")
            weight = parts[1].strip("{}")
            status = parts[2].strip()

            # Add parsed data to structured_data list as a dictionary
            structured_data.append({
                'position': position,  # e.g., "06,11"
                'weight': weight,      # e.g., "00000"
                'status': status       # e.g., "UNUSED" or a name
            })

    # Store the parsed data temporarily in the global variable
    grid_data = structured_data

    return jsonify({"message": "File uploaded successfully", "data": structured_data}), 200


# New route to fetch the grid data after upload
@app.route('/api/get_grid_data', methods=['GET'])
def get_grid_data():
    if grid_data is None:
        return jsonify({"error": "No grid data available"}), 404
    return jsonify({"data": grid_data}), 200



if __name__ == '__main__':
    app.run(port=5000)  # Flask backend will run on port 5000
