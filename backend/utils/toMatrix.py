def parse_to_matrices(structured_data):
    weights = [[0] * 12 for _ in range(8)]  # 8 rows, 12 columns
    names = [["UNUSED"] * 12 for _ in range(8)]

    for entry in structured_data:
        row, col = map(int, entry['position'].split(','))
        
        # Check for 'NaN' status
        if entry['status'] == "NAN":
            weights[row - 1][col - 1] = 0  # NaN spaces have no weight
            names[row - 1][col - 1] = "NAN"  # Mark as NaN
        else:
            weights[row - 1][col - 1] = int(entry['weight'])
            names[row - 1][col - 1] = entry['status']

    return weights, names