from balance import load_file, loading, a_star_unloading

w, n = load_file('../SilverQueen.txt')

#display initial ship state
print("Initial Ship Weights:")
for row in w:
    print(row)
    
print("Initial Ship Names:")
for row in n:
    print(row)
    
# #test loading
# print("\n=== Testing Loading Function ===")
# containers_to_load = [
#     {"name": "Fox", "weight": 150}, 
#     {"name": "Wolf", "weight": 200}
# ]

# new_w, new_n, moves = loading(w, n, containers_to_load)
# print("\nShip Weights After Loading:")
# for row in new_w:
#     print(row)
    
# print("\nLoading Moves:")
# for move in moves:
#     print(move)
    
#Test Unloading 
print("\n=== Testing Unloading Function ===")
containers_to_unload = [(0, 1), (0, 2)]
final_w, final_n, unload_moves = a_star_unloading(new_w, new_n, containers_to_unload)
print("\nShip Weights After Unloading:")
for row in final_w:
    print(row)
    
print("\nUnloading Moves:")
for move in unload_moves:
    print(move)