from collections import namedtuple
import copy
from heapq import heappush, heappop
import math

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

def heuristic(weights):
    left_weight = sum(weights[row][i] for row in range(8) for i in range(6))
    right_weight = sum(weights[row][i] for row in range(8) for i in range(6, 12))
    return left_weight, right_weight, abs(left_weight - right_weight)

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

def balance(weights, names):
    # continue while open set has value in it
    open_set = []
    start = (0, 0, weights, names, []) # added history component
    open_set.append(start)

    # to prevent the same configuration to be drawn again
    visited = set()

    while open_set:
        # want the lowest costing operation
        sorted(open_set, key=lambda x: x[0])
        total_cost, new_cost, curr_weights, curr_names, moves = open_set.pop(0)

        if is_goal_state(curr_weights):
            print('Balanced')
            print("Moves:")
            for move in moves:
                print(f"From: ({move[0]}, {move[1]}), To: ({move[2]}, {move[3]})")
            print(total_cost)
            return curr_weights, curr_names, moves
        visited_row = tuple(tuple(row) for row in curr_weights)
        if visited_row in visited:
            continue
        visited.add(visited_row)

        left_weight, right_weight, heuristic_val = heuristic(curr_weights)

        if left_weight > right_weight:
            for r in range(0,8):
                for c in range(6):
                    if curr_weights[r][c] <= 0:
                        continue
                    temp_w = [list(row) for row in curr_weights]
                    temp_n = [list(row) for row in curr_names]
                    temp_m = moves.copy()

                    for empty_r in range(7, r, -1):
                        if temp_w[empty_r][c] == 0:
                            continue
                        dist, cell = find_closest_space(temp_n, empty_r, c, 'l')
                        new_cost += dist
                        temp_w[cell[0]][cell[1]] = temp_w[empty_r][c]
                        temp_w[empty_r][c] = 0
                        temp_n[cell[0]][cell[1]] = temp_n[empty_r][c]
                        temp_n[empty_r][c] = 'UNUSED'
                        temp_m.append((empty_r, c, cell[0], cell[1]))
                    dist, cell = find_closest_space(temp_n, r, c, 'r')
                    new_cost += dist
                    total_cost = new_cost
                    temp_w[cell[0]][cell[1]] = temp_w[r][c]
                    temp_w[r][c] = 0
                    temp_n[cell[0]][cell[1]] = temp_n[r][c]
                    temp_n[r][c] = 'UNUSED'
                    temp_m.append((r, c, cell[0], cell[1]))
                    open_set.append((total_cost, new_cost, temp_w, temp_n, temp_m))
                    break

        else:
            for r in range(0,8):
                for c in range(6,12):
                    if curr_weights[r][c] <= 0:
                        continue
                    temp_w = [list(row) for row in curr_weights]
                    temp_n = [list(row) for row in curr_names]
                    temp_m = moves.copy()

                    for empty_r in range(7, r, -1):
                        if temp_w[empty_r][c] == 0:
                            continue
                        dist, cell = find_closest_space(temp_n, empty_r, c, 'r')
                        new_cost += dist
                        temp_w[cell[0]][cell[1]] = temp_w[empty_r][c]
                        temp_w[empty_r][c] = 0
                        temp_n[cell[0]][cell[1]] = temp_n[empty_r][c]
                        temp_n[empty_r][c] = 'UNUSED'
                        temp_m.append((empty_r, c, cell[0], cell[1]))
                    dist, cell = find_closest_space(temp_n, r, c, 'l')
                    new_cost += dist
                    total_cost = new_cost
                    temp_w[cell[0]][cell[1]] = temp_w[r][c]
                    temp_w[r][c] = 0
                    temp_n[cell[0]][cell[1]] = temp_n[r][c]
                    temp_n[r][c] = 'UNUSED'
                    temp_m.append((r, c, cell[0], cell[1]))
                    open_set.append((total_cost, new_cost, temp_w, temp_n, temp_m))
                    break

    # If balance isn't possible, use sift method
    print('Balance not Possible, calling sift function')
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

w, n = load_file('ShipCase5.txt')
for r in w:
    print(r)

new_w, new_n, moves = balance(w,n)
if new_w != None:
    for r in new_w:
        print(r)

if new_n != None:
    for n in new_n:
        print(n)

if moves != None:
    for move in moves:
        print(f"From: ({move[0]}, {move[1]}), To: ({move[2]}, {move[3]})")
