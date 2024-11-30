from collections import namedtuple
import copy
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

    print('No Solution')
    return None, None, None

w, n = load_file('/Users/aakgna/Downloads/SilverQueen.txt')
for r in w:
    print(r)

new_w, new_n, moves = balance(w,n)
if new_w != None:
    for r in new_w:
        print(r)
