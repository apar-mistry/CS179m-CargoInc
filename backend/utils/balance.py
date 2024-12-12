from collections import namedtuple, defaultdict
import copy
from heapq import heappush, heappop
import math
from heapq import heappop, heappush
from itertools import combinations
container_weights = [[], [], [], [], [], [], [], []]
container_names = [[], [], [], [], [], [], [], []]
timeSpent = 0

def load_file(file):
    global container_weights, container_names
    with open(file, 'r') as f:
        for line in f:
            sections = line.split(',')
            row = int(sections[0].replace('[', ''))
            col = int(sections[1].replace(']', ''))
            weight = int(sections[2].replace('{', '').replace('}', ''))
            name = sections[3].replace("\n", '')
            container_weights[row-1].append(weight)
            container_names[row-1].append(name)
    return container_weights, container_names


def is_goal_state(weights):
    left, right = 0, 0
    for rows in range(8):
        for i in range(6):
            left += weights[rows][i]
        for i in range(6, 12):
            right += weights[rows][i]
    if left == right == 0:
        return True

    return 1.1 > min(right, left) / max(right, left) > 0.9


def calculate_f_score(weights, g_score):
    left_weight = sum(weights[row][i] for row in range(8) for i in range(6))
    right_weight = sum(weights[row][i]
                       for row in range(8) for i in range(6, 12))
    weight_diff = abs(left_weight - right_weight)

    total_containers = 0
    for row in weights:
        for w in row:
            if w > 0:
                total_containers += 1
    avg_weight = (left_weight + right_weight) / \
        total_containers if total_containers > 0 else 1
    h_score = weight_diff / avg_weight

    return g_score + h_score


def get_valid_moves(weights, names):
    moves = []

    for row1 in range(8):
        for col1 in range(12):
            if weights[row1][col1] > 0:
                container_above = False
                for r in range(row1 + 1, 8):
                    if weights[r][col1] > 0:
                        container_above = True
                        break

                if container_above is not True:
                    for row2 in range(8):
                        for col2 in range(12):
                            if col1 != col2 and is_valid_position(weights, names, row2, col2):
                                moves.append((row1, col1, row2, col2))

    return moves


def is_valid_position(weights, names, row, col):
    if names[row][col] == ' NAN' or weights[row][col] > 0:
        return False
    if row > 0:
        if names[row - 1][col] == ' UNUSED':
            return False
    if row < 7:
        if weights[row + 1][col] > 0:
            return False
    return True


def can_balance(weights):
    numbers = []
    for row in weights:
        for num in row:
            if num != 0:
                numbers.append(num)

    if len(numbers) < 2:
        return False

    numbers.sort()

    for l in range(1, len(numbers)):
        for left in combinations(numbers, l):
            left_arr = list(left)
            left_sum = sum(left_arr)
            right = [x for x in numbers if x not in left]
            right_sum = sum(right)

            min_sum = min(left_sum, right_sum)
            max_sum = max(left_sum, right_sum)

            if (left_sum + right_sum == sum(numbers)) and (max_sum > 0) and (min_sum / max_sum > 0.9):
                return True
    return False


from collections import defaultdict

def find_optimal_spot(weights, names, loading_point, container_weight=0):
    num_rows = len(weights)
    num_cols = len(weights[0]) if num_rows > 0 else 0

    loading_row, loading_col = loading_point
    loading_row -= 1  # Zero-based
    loading_col -= 1  # Zero-based

    min_distance = float('inf')
    optimal_spot = None

    for row in range(num_rows):
        for col in range(num_cols):
            # Check if the current spot is UNUSED
            if names[row][col] == "UNUSED":
                # Determine if the spot has a valid support
                if row == 0:
                    # Ground level; always valid
                    valid_support = True
                else:
                    # Check the spot below
                    below_weight = weights[row - 1][col]
                    below_name = names[row - 1][col]
                    if below_weight > 0 or below_name == "NAN":
                        valid_support = True
                    else:
                        valid_support = False

                if valid_support:
                    # Calculate Manhattan distance from loading point
                    distance = abs(row - loading_row) + abs(col - loading_col)

                    # Update the optimal spot if a closer spot is found
                    if distance < min_distance:
                        min_distance = distance
                        optimal_spot = (row, col)
                    elif distance == min_distance:
                        # Tie-breaker: prioritize lower row, then lower column
                        if optimal_spot is None or (row, col) < optimal_spot:
                            optimal_spot = (row, col)

    if optimal_spot:
        return optimal_spot, min_distance
    else:
        return (None, None)

def find_alternative_spot(weights, names, loading_point, current_position):
    num_rows = len(weights)
    num_cols = len(weights[0]) if num_rows > 0 else 0

    loading_row, loading_col = loading_point
    loading_row -= 1  # Zero-based indexing
    loading_col -= 1  # Zero-based indexing

    current_row, current_col = current_position

    # Calculate the cost to move to buffer
    distance_to_buffer = abs(current_row - loading_row) + abs(current_col - loading_col)
    cost_to_buffer = 2 + (2 * distance_to_buffer)

    min_cost = float('inf')
    optimal_spot = (None, None)

    for row in range(num_rows):
        for col in range(num_cols):
            # Skip the current position
            if row == current_row and col == current_col:
                continue

            # Check if the spot is UNUSED
            if names[row][col] != "UNUSED":
                continue

            # Determine if the spot has valid support
            if row == 0:
                valid_support = True
            else:
                below_weight = weights[row - 1][col]
                below_name = names[row - 1][col]
                if below_weight > 0 or below_name == "NAN":
                    valid_support = True
                else:
                    valid_support = False

            if not valid_support:
                continue

            # Calculate Manhattan distance
            distance = abs(row - loading_row) + abs(col - loading_col)

            # Calculate total cost
            total_cost = 2 +  distance

            # Check if this spot has a lower cost than moving to buffer
            if total_cost < cost_to_buffer and total_cost < min_cost:
                min_cost = total_cost
                optimal_spot = (row, col)

    if optimal_spot != (None, None):
        return (*optimal_spot, min_cost)
    else:
        return (None, None, None)

def clear_above(row, col, weights, names, loading_point, buffer, moves):
    global timeSpent
    for r in range(len(weights) - 1, row, -1):
        if weights[r][col] > 0 and names[r][col] != "NAN":
            container_weight = weights[r][col]
            container_name = names[r][col]

            current_position = (r, col)

            # **Mark the current position as UNUSED before searching**
            weights[r][col] = 0
            names[r][col] = "UNUSED"

            # Attempt to find an alternative spot within the grid
            alternative_spot = find_alternative_spot(weights, names, loading_point, current_position)

            if alternative_spot[0] is not None:
                # Move container to the alternative spot
                new_row, new_col, min_distance = alternative_spot

                # Calculate total time: 2 minutes + 2 * distance
                distance = abs(r - new_row) + abs(col - new_col)
                total_time = 2 + distance

                # Update grids
                weights[new_row][new_col] = container_weight
                names[new_row][new_col] = container_name
                timeSpent += total_time
                # Record the move within the grid
                moves.append({
                    'container': container_name,
                    'from': [r + 1, col + 1],
                    'to': [new_row + 1, new_col + 1],
                    'time': total_time
                })
            else:
                # No alternative spot found; move container to buffer
                # Calculate Manhattan distance from loading point
                loading_row, loading_col = loading_point
                loading_row -= 1  # Zero-based indexing
                loading_col -= 1  # Zero-based indexing
                distance_to_buffer = abs(r - loading_row) + abs(col - loading_col)

                # Calculate total time: 2 minutes + 2 * distance
                total_time = 2 + distance_to_buffer
        
                # Move container to buffer
                buffer[col].append({
                    'weight': container_weight,
                    'name': container_name,
                    'original_position': (r, col)
                })

                # Record the move to buffer
                # to
                timeSpent += total_time
                moves.append({
                    'container': container_name,
                    'from': [r + 1, col + 1],
                    'to': "BUFFER",
                    'time': total_time
                })

def user_unloading(weights, names, unload_data, loading_point=(8, 1)):
    global timeSpent
    moves = []   # List to track all moves
    buffer = defaultdict(list)  # Buffer to hold containers temporarily, grouped by column

    ROWS = len(weights)
    COLS = len(weights[0]) if ROWS > 0 else 0

    # Parse targets and group them by column
    targets_by_col = defaultdict(list)  # column: list of target rows
    for data in unload_data:
        if 'position' in data:
            # Unload Completely
            pos = data['position']
            row, col = map(int, pos.split(','))
            row -= 1  # Convert to zero-based indexing
            col -= 1
            targets_by_col[col].append(row)
        elif 'from' in data and data['to'] == "BUFFER":
            # Unload to BUFFER
            pos = data['from']
            row, col = pos
            row -= 1  # Convert to zero-based indexing
            col -= 1
            targets_by_col[col].append(row)
        # Else: Ignore other cases for unloading

    # Sort target rows in each column in descending order (top to bottom)
    for col in targets_by_col:
        targets_by_col[col].sort(reverse=True)

    # Remove targets and buffer obstructing containers
    for col, target_rows in targets_by_col.items():
        for target_row in target_rows:
            # Clear containers above the target
            clear_above(target_row, col, weights, names, loading_point, buffer, moves)

            # Remove the target container
            container_name = names[target_row][col]
            weights[target_row][col] = 0
            names[target_row][col] = "UNUSED"

            # Calculate time for unloading the target container
            distance_to_loading = abs(target_row - (loading_point[0] - 1)) + abs(col - (loading_point[1] - 1))
            total_time_unload = 2 + distance_to_loading  # Adjusted to match loading time logic
            timeSpent += total_time_unload
            # Record the removal of the target container
            moves.append({
                'container': container_name,
                'from': [target_row + 1, col + 1],
                'to': "UNLOAD",
                'time': total_time_unload
            })

    # After removing targets, shift containers down in each affected column
    for col, target_rows in targets_by_col.items():
        # Sort target rows in ascending order for shifting (bottom to top)
        sorted_targets = sorted(target_rows)

        for target_row in sorted_targets:
            # For each target_row, shift containers above down by one
            for r in range(target_row + 1, ROWS):
                if weights[r][col] > 0 and names[r][col] != "NAN":
                    container_weight = weights[r][col]
                    container_name = names[r][col]

                    # Calculate Manhattan distance from loading point
                    distance_shift = abs(r - (loading_point[0] - 1)) + abs(col - (loading_point[1] - 1))

                    # Calculate total time: 2 minutes + 2 * distance
                    total_time_shift = 2 +  distance_shift

                    # Shift container down by one
                    weights[r - 1][col] = container_weight
                    names[r - 1][col] = container_name

                    # Mark original spot as UNUSED
                    weights[r][col] = 0
                    names[r][col] = "UNUSED"
                    timeSpent += total_time_shift
                    # Record the shift move
                    moves.append({
                        'container': container_name,
                        'from': [r + 1, col + 1],
                        'to': [r, col + 1],
                        'time': total_time_shift
                    })

    # Restore containers from buffer back onto the ship using cost-based placement
    for col in buffer:
        # Sort buffered containers by original row in ascending order (bottom to top)
        buffer[col].sort(key=lambda x: x['original_position'][0])

        for item in buffer[col]:
            container_weight = item['weight']
            container_name = item['name']

            # Find the optimal spot for restoration
            optimal_spot, min_distance = find_optimal_spot(weights, names, loading_point, container_weight)

            if optimal_spot:
                row, col_spot = optimal_spot

                # Calculate Manhattan distance from loading point
                distance_to_ship = min_distance

                # Calculate total time: 2 minutes + 2 * distance
                total_time_restore = 2 + distance_to_ship

                # Place container back to the optimal position
                weights[row][col_spot] = container_weight
                names[row][col_spot] = container_name
                timeSpent += total_time_restore
                # Record the move from buffer back to the ship
                moves.append({
                    'container': container_name,
                    'from': "BUFFER",
                    'to': [row + 1, col_spot + 1],
                    'time': total_time_restore
                })
            else:
                # If no optimal spot found, log an error and optionally keep the container in BUFFER
                print(f"Error: No available supported space to restore container '{container_name}' from BUFFER.")
                # Optionally, implement logic to handle this scenario (e.g., retry later, expand grid, etc.)

    return weights, names, moves, timeSpent
def loading(weights, names, load_data, loading_point=(8, 1)):
    moves = []
    total_time = 0
    num_rows = len(weights)
    num_cols = len(weights[0]) if num_rows > 0 else 0
    
    loading_row, loading_col = loading_point
    loading_row -= 1  # Zero-based
    loading_col -= 1  # Zero-based
    
    for data in load_data:
        container_name = data['containerName']
        weight = int(data['weight'])
        placed = False 
        min_distance = float('inf')
        optimal_spot = None
        
        for row in range(num_rows):
            for col in range(num_cols):
                # Check if the current spot is UNUSED
                if names[row][col] == "UNUSED":
                    # Determine if the spot has a valid support
                    if row == 0:
                        # Ground level; always valid
                        valid_support = True
                    else:
                        # Check the spot below
                        below_weight = weights[row - 1][col]
                        below_name = names[row - 1][col]
                        if below_weight > 0 or below_name == "NAN":
                            valid_support = True
                        else:
                            valid_support = False
                    
                    if valid_support:
                        # Calculate Manhattan distance from loading point
                        distance = abs(row - loading_row) + abs(col - loading_col)
                        
                        # Update the optimal spot if a closer spot is found
                        if distance < min_distance:
                            min_distance = distance
                            optimal_spot = (row, col)
                        elif distance == min_distance:
                            # Tie-breaker: prioritize lower row, then lower column
                            if (row, col) < optimal_spot:
                                optimal_spot = (row, col)
        
        if optimal_spot:
            # Place the container at the optimal spot
            row, col = optimal_spot
            weights[row][col] = weight
            names[row][col] = container_name
            
            # Calculate total time: 2 minutes + 2 * Manhattan distance
            total_time += (2 + min_distance)
            
            moves.append({
                'container': container_name,
                'position': (row + 1, col + 1),
                'weight': weight,  # Convert back to one-based index
                'time': total_time
            })
            placed = True
        else:
            raise ValueError(f"No legal spot found for container '{container_name}'.")
    return weights, names, moves, total_time
def balance(weights, names):

    visited_states = set()
    start_state = tuple(tuple(row) for row in weights)
    g_scores = {start_state: 0}
    f_scores = {start_state: calculate_f_score(weights, 0)}
    open_set = [(f_scores[start_state], 0, weights, names, [])]

    best_solution = None
    best_score = float('inf')
    best_g = float('inf')

    while open_set:
        if all(g_score > best_g for f, g_score, w, n, m in open_set):
            break

        temp_f, curr_g_score, curr_weights, curr_names, curr_moves = heappop(
            open_set)
        curr_state = tuple(tuple(row) for row in curr_weights)

        if curr_state not in visited_states:
            visited_states.add(curr_state)
        else:
            continue

        if is_goal_state(curr_weights):
            current_score = calculate_f_score(curr_weights, curr_g_score)
            if current_score < best_score:
                for r in curr_weights:
                    print(r)
                print("==============")
                best_solution = (curr_weights, curr_names, curr_moves)
                best_score = current_score
                best_g = curr_g_score

        for move in get_valid_moves(curr_weights, curr_names):
            row1, col1, row2, col2 = move

            new_weights = [list(row) for row in curr_weights]
            new_names = [list(row) for row in curr_names]
            new_weights[row2][col2] = new_weights[row1][col1]
            new_weights[row1][col1] = 0
            new_names[row2][col2] = new_names[row1][col1]
            new_names[row1][col1] = 'UNUSED'

            new_state = tuple(tuple(row) for row in new_weights)
            move_cost = abs(row1 - row2) + abs(col1 - col2)
            test_g_score = curr_g_score + move_cost

            if new_state not in g_scores or test_g_score < g_scores[new_state]:
                g_scores[new_state] = test_g_score
                f_score = calculate_f_score(new_weights, test_g_score)
                f_scores[new_state] = f_score
                new_moves = curr_moves + [move]
                heappush(open_set, (f_score, test_g_score,
                         new_weights, new_names, new_moves))

    if best_solution:
        fweights, fnames, fmoves = best_solution
        return fweights, fnames, fmoves

    # If balance isn't possible, use sift method
    print('Balance not possible, calling sift function')
    sift_weights, sift_names, sift_moves = sift(weights, names)

    return sift_weights, sift_names, sift_moves


def sift(weights, names):

    containers = []
    for r in range(8):
        for c in range(12):
            if weights[r][c] > 0 and 'UNUSED' not in names[r][c] and 'NAN' not in names[r][c]:
                containers.append({
                    'weight': weights[r][c],
                    'name': names[r][c],
                    'position': (r, c)
                })

    containers.sort(key=lambda x: x['weight'], reverse=True)

    sift_pattern = [6, 5, 7, 4, 8, 3, 9, 2, 10, 1, 11, 0]
    sift_weights = [[0 for i in range(12)] for j in range(8)]
    sift_names = [['UNUSED' for i in range(12)] for j in range(8)]
    sift_moves = []

    curr_row = 0
    for x, container in enumerate(containers):

        curr_col = sift_pattern[x % len(sift_pattern)]
        sift_weights[curr_row][curr_col] = container['weight']
        sift_names[curr_row][curr_col] = container['name']
        if (container['position'][0], container['position'][1]) != (curr_row, curr_col):
            sift_moves.append(
                (container['position'][0], container['position'][1], curr_row, curr_col))

        if x % len(sift_pattern) == 0 and x > 0:
            curr_row += 1

    return sift_weights, sift_names, sift_moves


def calculate_cost(old_weights, moves):
    total_cost = 0

    for move in moves:
        start = [move[0], move[1]]
        end = [move[2], move[3]]

        while start != end:
            if start[1] < end[1]:
                if old_weights[start[0]][start[1] + 1] == 0:
                    start[1] += 1
                else:
                    start[0] += 1
                total_cost += 1
            elif start[1] > end[1]:
                if old_weights[start[0]][start[1] - 1] == 0:
                    start[1] -= 1
                else:
                    start[0] += 1
                total_cost += 1
            elif start[0] < end[0]:
                start[0] += 1
                total_cost += 1
            elif start[0] > end[0]:
                start[0] -= 1
                total_cost += 1

        old_weights[end[0]][end[1]] = old_weights[move[0]][move[1]]
        old_weights[move[0]][move[1]] = 0

    return total_cost


def map_nested_grid(nested_data):
    # Define the transformation logic
    def map_values(row):
        return [
            value + 1 if index % 2 == 0 else value +
            1  # Add 1 to both x (even) and y (odd)
            for index, value in enumerate(row)
        ]

    # Apply the transformation to each row in the nested grid
    mapped_data = [map_values(row) for row in nested_data]
    return mapped_data


def process(input_file):
    w, n = load_file(input_file)
    if can_balance(w):
        print("Balance")
        new_w, new_n, moves = balance(w, n)
    else:
        print('sift')
        new_w, new_n, moves = sift(w, n)
    cost = calculate_cost(w, moves)
    return new_w, new_n, map_nested_grid(moves), cost

# print(process('../ShipCase2.txt'))
