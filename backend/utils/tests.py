import sys
from balance import user_unloading, loading
from parser import parseData

def parse_to_matrices(structured_data):
    weights = [[0] * 12 for _ in range(8)]  # 8 rows, 12 columns
    names = [["UNUSED"] * 12 for _ in range(8)]

    for entry in structured_data:
        row, col = map(int, entry['position'].split(','))
        weights[row - 1][col - 1] = int(entry['weight'])
        names[row - 1][col - 1] = entry['status']

    return weights, names

def print_ship_state(weights, names):
    """
    Prints the current state of the ship (weights and names).
    """
    print("Ship Weights:")
    for row in weights:
        print(row)
    print("\nShip Names:")
    for row in names:
        print(row)
    print()

if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python test.py <path_to_input_file>")
        sys.exit(1)

    # Get the input file path from the arguments
    file_path = sys.argv[1]

    try:
        # Parse the input file
        structured_data = parseData(file_path)

        # Convert structured data to weights and names matrices
        weights, names = parse_to_matrices(structured_data)

        # Display initial ship state
        print("\nInitial Ship State:")
        print_ship_state(weights, names)

        # Test unloading function
        print("\n=== Testing User Unloading ===")
        weights, names, unload_moves = user_unloading(weights, names)
        print("\nShip State After Unloading:")
        print_ship_state(weights, names)
        print("Unloading Moves:")
        for move in unload_moves:
            print(move)

        # Test loading function
        print("\n=== Testing User Loading ===")
        weights, names, load_moves = loading(weights, names)
        print("\nShip State After Loading:")
        print_ship_state(weights, names)
        print("Loading Moves:")
        for move in load_moves:
            print(move)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")