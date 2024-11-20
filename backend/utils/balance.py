from collections import namedtuple
import copy

Cell = namedtuple('Cell', ['row', 'col'])

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

def balance(weights, names):
    # continue while open set has value in it
    open_set = []
    start = (0, 0, weights, names)
    open_set.append(start)

    # to prevent the same configuration to be drawn again
    visited = set()

    while open_set:
        # want the lowest costing operation
        sorted(open_set, key=lambda x: x[0])
        total_cost, new_cost, curr_weights, curr_names = open_set.pop(0)
        if is_goal_state(curr_weights):
            print('Balanced')
            return curr_weights, curr_names
        visited_row = tuple(tuple(row) for row in curr_weights)
        if visited_row in visited:
            continue
        visited.add(visited_row)

        left_weight, right_weight, heuristic_val = heuristic(curr_weights)

        if left_weight > right_weight:
            for r in range(0,8):
                for c in range(5,-1,-1):
                    if curr_weights[r][c] <= 0:
                        continue
                    for i in range(6,12):
                        if curr_names[r][i] == 'NAN':
                            continue
                        if curr_weights[r][i] == 0:
                            new_weight = [list(r) for r in curr_weights]
                            new_names = [list(r) for r in curr_names]
                            new_weight[r][i] = new_weight[r][c]
                            new_weight[r][c] = 0
                            new_names[r][i] = new_names[r][c]
                            new_names[r][c] = 'UNUSED'
                            
                            new_cost += 1
                            _,_, h_cost = heuristic(new_weight)
                            total_cost = new_cost + h_cost

                            open_set.append((total_cost,new_cost,new_weight,new_names))
                            break
                    break
        else:
            for r in range(0,8):
                for c in range(6,12):
                    if curr_weights[r][c] <= 0:
                        continue
                    for i in range(5,-1,-1):
                        if curr_names[r][i] == 'NAN':
                            continue
                        if curr_weights[r][i] == 0:
                            new_weight = [list(r) for r in curr_weights]
                            new_names = [list(r) for r in curr_names]
                            new_weight[r][i] = new_weight[r][c]
                            new_weight[r][c] = 0
                            new_names[r][i] = new_names[r][c]
                            new_names[r][c] = 'UNUSED'
                            
                            new_cost += 1
                            _,_, h_cost = heuristic(new_weight)
                            total_cost = new_cost + h_cost

                            open_set.append((total_cost,new_cost,new_weight,new_names))
                            break
                    break
    print('No Solution')
    return None, None

def floor_cargo(weights, names):
    for c in range(len(weights[0])):
        for r in range(1, len(weights)):
            if weights[r][c] > 0:
                curr = r
                while curr > 0 and weights[curr-1][c] == 0:
                    if 'NAN' in names[curr-1][c]:
                        break
                    weights[curr-1][c] = weights[curr][c]
                    names[curr-1][c] = names[curr][c]
                    weights[curr][c] = 0
                    names[curr][c] = 'UNUSED'
                    curr -=1
    return weights, names


w, n = load_file('/Users/aakgna/Downloads/SilverQueen.txt')
new_w, new_n = balance(w,n)
if new_w and new_n:
    w, n = floor_cargo(new_w, new_n)
for r in w:
    print(r)
