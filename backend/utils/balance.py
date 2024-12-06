from collections import namedtuple
import copy
from heapq import heappush, heappop
import math
from heapq import heappop, heappush
from itertools import combinations 

def load_file(file):
    container_weights = [[], [], [], [], [], [], [], []]
    container_names = [[], [], [], [], [], [], [], []]
    
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
        
    return 1.1 > min(right,left) / max(right,left) > 0.9

def calculate_f_score(weights, g_score):
    left_weight = sum(weights[row][i] for row in range(8) for i in range(6))
    right_weight = sum(weights[row][i] for row in range(8) for i in range(6, 12))
    weight_diff = abs(left_weight - right_weight)

    total_containers = 0
    for row in weights:
        for w in row:
            if w > 0:
                total_containers += 1
    avg_weight = (left_weight + right_weight)/total_containers if total_containers > 0 else 1
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
    if row  < 7:
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

def a_star_unloading(weights, names, goal_unload):
    #A* for optimizing unloading
    open_set = []
    visited = set()
    
    #initial state
    start_state = {
        "weights": weights, 
        "names": names, 
        "remaining_moves": goal_unload, 
        "cost": 0, 
        "history": []
    }
    heappush(open_set, (0, start_state))
    
    while open_set:
        _, current_state = heappop(open_set)
        
        #check if all containers are unloaded
        if not current_state["remaining_moves"]:
            print("Unloading optimized!")
            print("Moves:", current_state["history"])
            return current_state["weights"], current_state["names"], current_state["history"]
        
        #Prevent revisiting states
        state_tuple = tuple(tuple(row) for row in current_state["weights"])
        if state_tuple in visited:
            continue
        visited.add(state_tuple)
        
        for container in current_state["remaining_moves"]:
            r, c = container
            
            #generate a new state with the container unloaded
            new_weights = copy.deepcopy(current_state["weights"])
            new_names = copy.deepcopy(current_state["names"])
            new_history = current_state["history"].copy()
            
            #move any blocking containers
            for row_above in range(r-1, -1, -1):
                if new_weights[row_above][c] > 0:
                    _, closest_space = find_closest_space(new_names, row_above, c, side='l')
                    new_weights[closest_space[0]][closest_space[1]] = new_weights[row_above][c]
                    new_weights[row_above][c] = 0
                    new_names[closest_space[0]][closest_space[1]] = new_names[row_above][c]
                    new_names[row_above][c] = 'UNUSED'
                    new_history.append((row_above, c, closest_space[0], closest_space[1]))
            
            #unload the target container
            new_weights[r][c] = 0
            new_names[r][c] = 'UNUSED'
            new_history.append((r, c, -1, -1)) #-1, -1 indicates unloading
            
            #calculate cost
            new_cost = current_state["cost"] + abs(r - 7) + abs(c - 0)
            
            #add the new state to the open set
            new_state = {
                "weights": new_weights, 
                "names": new_names, 
                "remaining_moves": [
                    move for move in current_state["remaining_moves"] if move != (r, c)
                    ],
                "cost": new_cost, 
                "history": new_history
            }
            heappush(open_set, (new_cost, new_state))
        
    print("No valid unloading sequence found.")
    return None, None, None

def loading(weights, names, containers_to_load):
    moves = []
    
    for container in containers_to_load:
        #extract container information
        container_weight = container['weight']
        container_name = container['name']
        
        #calculate left and right side weights
        left_weight = sum(weights[row][col] for row in range(8) for col in range(6))
        right_weight = sum(weights[row][col] for row in range(8) for col in range(6, 12))
        
        #decide which side to load the container (prioritize lighter side)
        side = 'l' if left_weight < right_weight else 'r'
        
        #find the closest available space on the chosen side
        _, closest_space = find_closest_space(names, 0, 0, side)
        if closest_space == [0, 0]: #if not space found on chosen side, try the other side
            side = 'r' if side == 'l' else 'l'
            _, closest_space = find_closest_space(names, 0, 0, side)
            
        #place the container in the chosen space
        r, c = closest_space
        weights[r][c] = container_weight
        names[r][c] = container_name
        
        #log the move
        moves.append({'container': container_name, 'position': (r+1, c+1)})
        print(f"Loaded container '{container_name}' at position ({r + 1}, {c + 1})")
        
        #periodically check balance and adjust if necessary 
        if not is_goal_state(weights):
            print("Rebalancing the ship...")
            weights, names, _ = balance(weights, names)
            
    return weights, names, moves

def find_closest_space(names, old_r, old_c, side):
    smallest = math.inf
    cell = [old_r, old_c]
    if side == 'l':
        for r in range(8):
            for c in range(6):
                if c == old_c:
                    continue
                if 'UNUSED' in names[r][c]:
                    if r > 0 and 'UNUSED' in names[r-1][c]:
                        continue
                    manhattan = abs(r-old_r) + abs(c-old_c)
                    if manhattan < smallest:
                        cell = [r, c]
                        smallest = manhattan
    else:
        for r in range(8):
            for c in range(6, 12):
                if c == old_c:
                    continue
                if 'UNUSED' in names[r][c]:
                    if r > 0 and 'UNUSED' in names[r-1][c]:
                        continue
                    manhattan = abs(r-old_r) + abs(c-old_c)
                    if manhattan < smallest:
                        cell = [r, c]
                        smallest = manhattan
    return smallest, cell

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
        
        temp_f, curr_g_score, curr_weights, curr_names, curr_moves = heappop(open_set)
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
                heappush(open_set, (f_score, test_g_score, new_weights, new_names, new_moves))


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

    sift_pattern = [6,5,7,4,8,3,9,2,10,1,11,0]
    sift_weights = [[0 for i in range(12)] for j in range(8)]
    sift_names = [['UNUSED' for i in range(12)] for j in range(8)]
    sift_moves = []

    curr_row = 0
    for x, container in enumerate(containers):

        curr_col = sift_pattern[x % len(sift_pattern)]
        sift_weights[curr_row][curr_col] = container['weight']
        sift_names[curr_row][curr_col] = container['name']
        if (container['position'][0], container['position'][1]) != (curr_row, curr_col):
            sift_moves.append((container['position'][0], container['position'][1], curr_row, curr_col))

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

def process(input_file):
    w, n = load_file(input_file)
    if can_balance(w):
        print("Balance")
        new_w, new_n, moves = balance(w, n)
    else:
        print('sift')
        new_w, new_n, moves = sift(w, n)
    cost = calculate_cost(w, moves)
    return new_w, new_n, moves, cost

w, n, m, c = process('../SilverQueen.txt')