from collections import namedtuple
import copy
import math
from heapq import heappop, heappush

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
    if names[row][col] == 'NAN' or weights[row][col] > 0:
        return False
    if row > 0:
        if names[row - 1][col] == 'UNUSED':
            return False
    if row  < 7:
        if weights[row + 1][col] > 0:
            return False
    return True


def balance(weights, names):
    
    visited_states = set()
    start_state = tuple(tuple(row) for row in weights)
    g_scores = {start_state: 0}
    f_scores = {start_state: float('inf')}
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

        if is_goal_state(curr_weights):
            current_score = calculate_f_score(curr_weights, curr_g_score)
            if current_score < best_score:
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

w, n = load_file('/Users/kotasawada/Documents/CargoInc/CS179m-CargoInc/backend/utils/ShipCase5.txt')
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


