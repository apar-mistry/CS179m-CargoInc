

def parseData(file_path):
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
    return structured_data