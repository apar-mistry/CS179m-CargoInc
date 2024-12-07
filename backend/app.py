from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime
import shutil
from utils.logger import *
from utils.parser import parseData
from utils.balance import * 
import glob
app = Flask(__name__)
CORS(app)  # Allow CORS for requests from frontend

# Define the upload directory and temporary storage for grid data
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
grid_data = None  # Temporary variable to store parsed grid data
filename = ''
# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/api/log_action', methods=['POST'])
def log_movement():
    data = request.get_json()
    username = 'SHIP MOVEMENT'
    action = data.get('message')
    log_action(username, action)
    return jsonify({"message": "Log created successfully"}), 200


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
    global filename
    global grid_data  # Use the global variable to store data temporarily

    # Clear the upload directory
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        shutil.rmtree(app.config['UPLOAD_FOLDER'])  # Remove the folder and its contents
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Recreate the directory

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.txt'):
        return jsonify({"error": "Invalid file type. Only .txt files are allowed."}), 400
    
    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save the uploaded file
    file.save(file_path)
    grid_data = parseData(file_path)
    count_entries = sum(1 for entry in grid_data if entry['status'] not in ("UNUSED", "NAN"))
    log_action(request.headers.get("Username"),
               f"uploaded manifest {filename}, there are {count_entries} containers on the ship")
    return jsonify({"message": "File uploaded successfully", "data": grid_data}), 200


# New route to fetch the grid data after upload
@app.route('/api/get_grid_data', methods=['GET'])
def get_grid_data():
    if grid_data is None:
        return jsonify({"error": "No grid data available"}), 404
    return jsonify({"data": grid_data}), 200

@app.route('/api/log_operator', methods=['POST'])
def log_operator():
    data = request.get_json()
    username = data.get('username')
    log = data.get('log')
    operator_logs(username, log)
    return jsonify({"message": "Log created successfully"}), 200



@app.route('/api/balance', methods=['GET'])
def balance():
        # Construct the path to the uploads directory
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        
        # Get the first file in the uploads directory
        file_list = glob.glob(os.path.join(uploads_dir, '*'))
        if not file_list:
            return jsonify({"error": "No files found in uploads directory"}), 404

        # Assuming there is only one file, use the first one
        file_path = file_list[-1]

        print(f"Processing file: {file_path}")
        
        new_w, new_n, moves, cost = process(file_path)

        return jsonify({
        "Data": moves,
        "Cost": cost,
        "NewW": new_w,
        "New_n": new_n}), 200
@app.route('/api/finalize_balance', methods=['POST'])
def finalize_balance():
    data = request.get_json()
    global filename

    # Since data is just a list, treat it as the grid
    grid = data

    lines = [
        f"[{cell.get('position','00,00')}], {{{cell.get('weight','00000')}}}, {cell.get('status','NAN')}"
        for row in reversed(grid)
        for cell in (row)
    ]

    formatted_text = "\n".join(lines)
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    log_dir = os.path.join(desktop_path, "logs")

    outbound_dir = os.path.join(log_dir, "outbound_manifests")
    if not os.path.exists(outbound_dir):
        os.makedirs(outbound_dir)

    output_filename = f"{filename[:-4]}OUTBOUND.txt"  
    output_file_path = os.path.join(outbound_dir, output_filename)
    with open(output_file_path, "w") as f:
        f.write(formatted_text)
    log_complete(f"Finished a Balance. Manifest {output_filename} was written to desktop, and a reminder pop-up to operator to send file was displayed.")
    return jsonify({"message": "Manifest finalized and saved.", "file": output_file_path}), 200

if __name__ == '__main__':
    app.run(port=5000) 
