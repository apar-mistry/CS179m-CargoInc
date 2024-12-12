from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime
import shutil
from utils.logger import *
from utils.parser import parseData
from utils.balance import * 
import glob
from utils.toMatrix import parse_to_matrices
app = Flask(__name__)
CORS(app)  # Allow CORS for requests from frontend

# Define the upload directory and temporary storage for grid data
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
grid_data = None  # Temporary variable to store parsed grid data
filename = ''
weights, names = None, None
# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def convert_to_grid_data(updated_weights, updated_names):
    grid_data = []
    for row_idx, (weight_row, name_row) in enumerate(reversed(list(zip(updated_weights, updated_names)))):
        for col_idx, (weight, name) in enumerate(zip(weight_row, name_row)):
            position = f"{row_idx + 1:02},{col_idx + 1:02}" 
            grid_data.append({
                "position": position,
                "weight": f"{weight:05}" if weight > 0 else "00000",  
                "status": name
            })
    return grid_data
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
    global weights, names
    # Clear the upload directory
    filename = ''  # Reset the filename
    grid_data = None  # Reset the grid data
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
    weights, names = parse_to_matrices(grid_data)
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
        global filename
        # Construct the path to the uploads directory
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        
        # Get the first file in the uploads directory
        file_list = glob.glob(os.path.join(uploads_dir, filename))
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

@app.route('/api/load_unload', methods=['POST'])
def getMoves():
    try:
        ltime, utime = 0, 0
        global weights, names  # Access global variables
        if weights is None or names is None:
            return jsonify({"error": "Ship data not initialized. Upload a file first."}), 400

        # Retrieve the JSON body from the request
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        # Extract load and unload data
        load_data = data.get("load", [])
        unload_data = data.get("unload", [])

        # Perform unloading
        if unload_data:
            weights, names, unload_moves, utime = user_unloading(weights, names, unload_data)
        else:
            unload_moves = []

        # Perform loading
        if load_data:
            weights, names, load_moves, ltime = loading(weights, names, load_data)
        else:
            load_moves = []
        # Sum the time for load and unload moves
        total_time = sum(move['time'] for move in load_moves) + sum(move['time'] for move in unload_moves)
        grid_data = convert_to_grid_data(weights, names)
        # total_time = ltime + utime
        # Construct the response
        response = {
            "data": grid_data,
            "unloadMoves": unload_moves,
            "loadMoves": load_moves,
            "total_time": total_time,
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
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
    log_complete(f"Finished a Balance. Manifest {filename[:-4]}OUTBOUND.txt was written to desktop, and a reminder pop-up to operator to send file was displayed.")
    return jsonify({"message": "Manifest finalized and saved.", "file": output_file_path}), 200

@app.route('/api/finalize_load_unload', methods=['POST'])
def finalize_load_unload():
    try:
        data = request.get_json()
        global filename
        
        # Validate received data
        if not isinstance(data, list):
            return jsonify({"message": "Invalid data format. Expected a list."}), 400

        grid = data

        # Format each cell's data
        lines = [
            f"[{cell.get('position', '00,00')}], {{{cell.get('weight', '00000')}}}, {cell.get('status', 'NAN')}"
            for row in reversed(grid)
            for cell in row
        ]

        formatted_text = "\n".join(lines)

        # Define paths
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        log_dir = os.path.join(desktop_path, "logs")
        load_unload_dir = os.path.join(log_dir, "outbound_manifests")

        # Create directories if they don't exist
        os.makedirs(load_unload_dir, exist_ok=True)

        # Generate output filename
        if filename.lower().endswith('.txt'):
            base_filename = filename[:-4]
        else:
            base_filename = filename
        output_filename = f"{base_filename}OUTBOUND.txt"
        output_file_path = os.path.join(load_unload_dir, output_filename)

        # Write formatted text to the file
        with open(output_file_path, "w") as f:
            f.write(formatted_text)

        # Log the completion
        log_complete(f"Finished Load/Unload operations. Manifest {base_filename}OUTBOUND.txt was written to desktop, and a reminder pop-up to operator to send file was displayed.")

        # Return success response
        return jsonify({"message": "Load/Unload manifest finalized and saved.", "file": output_file_path}), 200

    except Exception as e:
        # Handle unexpected errors
        log_complete(f"Error during finalize_load_unload: {str(e)}")
        return jsonify({"message": "An error occurred while finalizing the Load/Unload manifest.", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000) 
