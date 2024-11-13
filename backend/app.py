from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime
import shutil
from utils.logger import log_action
from utils.parser import parseData
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
    log_action(username, "logged in")
    return jsonify({"message": "Log created successfully"}), 200


@app.route('/api/log_logout', methods=['POST'])
def log_logout():
    data = request.get_json()
    username = data.get('username')
    log_action(username, "logged out")
    folder_path = "./uploads"  # Adjust the path if necessary
    
    # Clear the folder contents
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)  # Remove the entire uploads folder
            os.makedirs(folder_path)  # Recreate the empty uploads folder
        except Exception as e:
            return jsonify({"error": f"Error clearing uploads folder: {str(e)}"}), 500
    return jsonify({"message": "Log created successfully"}), 200


# Route for uploading a file
@app.route('/api/upload', methods=['POST'])
def upload_file():
    global grid_data  # Use the global variable to store data temporarily
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.txt'):
        return jsonify({"error": "Invalid file type. Only .txt files are allowed."}), 400
    
    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    file.save(file_path)
    grid_data = parseData(file_path)
    log_action(request.headers.get("Username"),
               f"uploaded manifest {filename}")
    return jsonify({"message": "File uploaded successfully", "data": grid_data}), 200


# New route to fetch the grid data after upload
@app.route('/api/get_grid_data', methods=['GET'])
def get_grid_data():
    if grid_data is None:
        return jsonify({"error": "No grid data available"}), 404
    return jsonify({"data": grid_data}), 200


if __name__ == '__main__':
    app.run(port=5000)  # Flask backend will run on port 5000
