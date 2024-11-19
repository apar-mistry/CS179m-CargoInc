from collections import namedtuple

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
    print(container_names)
    return container_weights, container_names

def is_goal_state(weights):
    left, right = 0, 0
    for rows in range(8):
        for i in range(6):
            left += weights[rows][i]
        for i in range(6, 12):
            right += weights[rows][i]
    if left == right:
        return False
        
    return 1.1 > min(right,left) / max(right,left) > 0.9

def heuristic(weights):
    # Calculate the difference between left and right weights
    left_weight = sum(weights[row][i] for row in range(8) for i in range(6))
    right_weight = sum(weights[row][i] for row in range(8) for i in range(6, 12))
    return abs(left_weight - right_weight)
