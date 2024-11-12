import json
import os

def load_puzzles_from_json(file_path):
    # Ensure the file path is correct relative to the current working directory
    abs_file_path = os.path.join(os.path.dirname(__file__), file_path)
    with open(abs_file_path, 'r') as file:
        return json.load(file)
    
def load_puzzle_order(json_file):
    with open(json_file, 'r') as file:
        puzzles = json.load(file)
    
    # Créer un dictionnaire pour l'ordre des niveaux
    level_order = {}
    
    # Parcourir les puzzles et créer un ordre
    for i in range(len(puzzles) - 1):
        current_level = puzzles[i]['name']
        next_level = puzzles[i + 1]['name']
        level_order[current_level] = next_level
    
    # Le dernier niveau doit renvoyer au menu
    last_level = puzzles[-1]['name']
    level_order[last_level] = 'back-home'
    
    return level_order

def getPuzzle(puzzles, nb_puzzle):
    # Get the parameters of the puzzle with the given number.
    for puzzle in puzzles:
        if puzzle["nb"] == nb_puzzle:
            return puzzle
    print("Error: Puzzle not found.")
    return None

def getWorldsFiles():
    file_path = "puzzles.json"
    abs_file_path = os.path.join(os.path.dirname(__file__), file_path)
    with open(abs_file_path, 'r') as file:
        return json.load(file)

