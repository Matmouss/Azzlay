# Ici je met les classes, plus rien a faire d'écrire en anglais
# On suppose que les pièces sont des dictionnaires avec une position et un type

import json
from . import azzlay_common_functions
from . import azzlay_display
from . import azzlay_goals
from . import azzlay_rules
import copy
import time

class Game:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.extra_text = puzzle["extra text"]
        self.grid_template = Grid(puzzle["size"], puzzle["void cells"])
        self.pieces_tracker = pieces_tracker(puzzle["starting pieces"])
        self.inventory = inventory(puzzle["initial inventory"])
        self.cores = puzzle["cores positions"]
        self.cursor = cursor(puzzle["cursor position"], self.cores)
        self.state = "ongoing"
        self.initializeGoals(puzzle["goals"])
        self.Goals_Tracker = Goals_Tracker(self.list_of_goals)
        self.initializeRules(puzzle["rules"])
        self.Rules_Tracker = Rules_Tracker(self.list_of_rules)
        self.nb_of_moves = 0
        self.items = self.initializeItems()
        self.best_score = puzzle["best_score"]
        self.previous_state = None
        self.file_path = None

        self.Rules_Tracker.checkRules(self, "start game", {})

    
    def reset(self):
        self.extra_text = None
        self.grid_template = None
        self.pieces_tracker = None
        self.inventory = None
        self.cores = None
        self.cursor = None
        self.state = None
        self.Goals_Tracker = None
        self.Rules_Tracker = None
        self.nb_of_moves = None
        self.items = None
        self.best_score = None
        self.previous_state = None
        self.file_path = None


    def initializeItems(self):
        items = []
        for item in self.Goals_Tracker.goals:
            if len(item.parameters) > 0:
                for param in item.parameters:
                    if param == "item type":
                        items.append({"type": item.parameters["item type"], "position": item.parameters["item position"]})
        for item in self.Rules_Tracker.rules:
            if len(item.parameters) > 0:
                for param in item.parameters:
                    if param == "item type":
                        items.append({"type": item.parameters["item type"], "position": item.parameters["item position"]})
        return items

    def initializeGoals(self, json_list):
        self.list_of_goals = []
        for goal_data in json_list:
            goal_class = azzlay_goals.goal_type_mapping.get(goal_data["type"])
            if goal_class:
                goal_instance = goal_class(goal_data["description"], goal_data["parameters"])
                self.list_of_goals.append(goal_instance)
                
    def initializeRules(self, json_list):
        self.list_of_rules = []
        for rule_data in json_list:
            rule_class = azzlay_rules.rule_type_mapping.get(rule_data["type"])
            if rule_class:
                rule_instance = rule_class(rule_data["description"], rule_data["parameters"])
                if "secret" in rule_data: 
                    secret = rule_data["secret"]
                    if secret == "True": 
                        rule_instance.secret = True
                self.list_of_rules.append(rule_instance)
                
    def createDisplayGrid(self):
        # Iterates through all the different displayable assets
        display_grid = copy.deepcopy(self.grid_template.full_grid)
        for core in self.cores:
            display_grid[core[0]][core[1]] = "core"
        for item in self.items:
            display_grid[item["position"][0]][item["position"][1]] = item["type"]
        for item in self.pieces_tracker.pieces:
            display_grid[item["position"][0]][item["position"][1]] = item["type"]  # To display pieces
        display_grid[self.cursor.position[0]][self.cursor.position[1]] = self.cursor.status  # To display the cursor
        return display_grid
    
    def createOverlayMap(self):
        overlay_map = copy.deepcopy(self.grid_template.full_grid)
        for item in self.pieces_tracker.pieces:
            if item["position"] == self.cursor.position:
                overlay_map[item["position"][0]][item["position"][1]] = azzlay_common_functions.item_to_url_map[item["type"]]
        return overlay_map
    
    def placePiece(self, chosen_piece):
        place = True 
        for item in self.pieces_tracker.pieces:
            if item["position"] == self.cursor.position:
                place = False
        if place:
            if chosen_piece == "end":
                return False
            else:
                if self.inventory.inventory[chosen_piece] > 0:
                    self.inventory.dec(chosen_piece)
                    self.pieces_tracker.addPiece({"type": chosen_piece, "position": self.cursor.position})
                    return True
        return False

    def checkBest(self):
        if self.best_score == "NA":
            self.best_score = self.nb_of_moves
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                data[int(self.puzzle["nb"])-1]['best_score'] = self.best_score
                with open(self.file_path, 'w') as file:
                    json.dump(data, file, indent=4)
    

class previous_state:
    def __init__(self, game):
        self.state = copy.deepcopy(game.state)
        self.nb_of_moves = copy.deepcopy(game.nb_of_moves)
        self.pieces_tracker = copy.deepcopy(game.pieces_tracker)
        self.previous_state = copy.deepcopy(game.previous_state)
        self.inventory = copy.deepcopy(game.inventory)
        self.cursor = copy.deepcopy(game.cursor)

class pieces_tracker:
    def __init__(self, list_of_pieces):
        self.count = {"square": 0, "triangle": 0, "circle": 0, "quantum": 0}
        self.pieces = list_of_pieces
        for piece in self.pieces:
            self.count[piece["type"]] += 1
        
        self.piece_moved = [] # To keep track of pieces moved during a turn/ has to be reset each turn

    def addPiece(self, piece):
        self.pieces.append(piece)
        self.count[piece["type"]] += 1
        if piece not in self.piece_moved:
            self.piece_moved.append(piece)

    def delPiece(self, piece):
        self.pieces.remove(piece)
        #if piece in self.piece_moved:
        #   self.piece_moved.remove(piece)
        self.count[piece["type"]] -= 1

    def whoIsHere(self, position):
        for item in self.pieces:
            if item["position"] == position:
                return item
        return "nobody"
    
    def findNeighbours(self, piece, template_grid):
        # Quite obvious, find the neighbouring pieces to the current one
        neighbours = []
        for item in ["up", "down", "right", "left"]:
            if azzlay_common_functions.isInGrid(piece["position"], template_grid):
                whats_here = self.whoIsHere(azzlay_common_functions.sumLists(piece["position"], azzlay_common_functions.readDir(item)))
                if whats_here != "nobody":
                    neighbours.append(whats_here)
        return neighbours
   
    def movePiece(self, piece, template_grid, direction):
        # Assuming that the pieces are in a valid position in the list
        wasmoved = False
        # Move piece from its position to the direction 
        destination = azzlay_common_functions.sumLists(piece["position"], azzlay_common_functions.readDir(direction))
        whats_here = self.whoIsHere(destination)
        if whats_here == "nobody":
            whats_here = azzlay_common_functions.whatIsInCell(destination, template_grid)
            if whats_here == "":
                self.delPiece(piece)
                self.addPiece({"type": piece["type"], "position": destination})
                wasmoved = True
        else:
            if self.movePiece(self.whoIsHere(destination), template_grid, direction):
                self.delPiece(piece)
                self.addPiece({"type": piece["type"], "position": destination})
                wasmoved = True
        return wasmoved

    def checkUpgrades(self, template_grid, puzzle):
        upgrade_table = {"circle": "triangle", "triangle": "square", "square": "quantum", "quantum": "quantum"}
        if puzzle.cursor.current_speed < 2:
            for piece in self.piece_moved:
                neighbours = self.findNeighbours(piece, template_grid)
                if not puzzle.Rules_Tracker.checkRules(puzzle, "placing", {"piece": piece, "neighbours": neighbours}):
                    for item in neighbours:
                        if item["type"] == piece["type"]:
                            self.delPiece(item)
                            self.delPiece(piece)
                            self.addPiece({"type": upgrade_table[piece["type"]], "position": piece["position"]})
                            break
                        elif item["type"] == "quantum":
                            self.delPiece(item)
                            self.delPiece(piece)
                            self.addPiece({"type": upgrade_table[piece["type"]], "position": piece["position"]})
                            break
                        elif piece["type"] == "quantum":
                            self.delPiece(item)
                            self.delPiece(piece)
                            self.addPiece({"type": upgrade_table[item["type"]], "position": piece["position"]})
                            break
            self.piece_moved = []


class Grid:
    def __init__(self, size, void_cells, default_value=""):
        self.full_grid = []
        self.size = size
        
        for i in range(size[1]):
            self.full_grid.append([])
            for j in range(size[0]):
                self.full_grid[i].append(default_value)

        for item in void_cells:
            self.full_grid[item[0]][item[1]] = None

    def is_in_grid(self, position):
        return (0 <= position[0] < self.size[0] and 0 <= position[1] < self.size[1]) and self.full_grid[position[0]][position[1]] is not None

    def set_cell(self, position, value):
        if self.is_in_grid(position):
            self.full_grid[position[0]][position[1]] = value


class Goals_Tracker:
    def __init__(self, list_of_goals):
        self.goals = list_of_goals
        self.checked = [False for i in range(len(self.goals))]
        self.descriptions = self.getDescriptions(list_of_goals)
        self.display_descriptions = []
        self.getDisplayDescriptions()

    def getDescriptions(self, goals):
        ret = []
        for item in goals:
            ret.append(item.description)
        return ret
    
    def getDisplayDescriptions(self):
        self.display_descriptions = []
        for i, item in enumerate(self.descriptions):
            check = self.checked[i]
            if check == False: 
                state = "✗"
            else: 
                state = "✓"
            self.display_descriptions.append(item + " - " + state)

    def isWinner(self):
        # Return True if the player won
        win = True 
        for item in self.checked:
            if item == False:
                win = False
        return win

    def checkGoals(self, current_puzzle):
        # Check if goals are accomplished
        for i in range(len(self.goals)):
            if self.goals[i].checkGoal(current_puzzle):
                self.checked[i] = True
            else:
                self.checked[i] = False
        self.getDisplayDescriptions()


class Rules_Tracker:
    def __init__(self, list_of_rules):
        self.rules = list_of_rules
        self.status = self.getListOfStatus()
        self.descriptions = self.getDescriptions()
        
    def getListOfStatus(self):
        status = []
        for item in self.rules:
            status.append(item.status)
        return status
    
    def getDescriptions(self):
        descriptions = []
        for item in self.rules:
            if item.secret:
                descriptions.append("not revealed yet")
            else:
                if not item == "":
                    descriptions.append(item.description)               
        if len(descriptions) == 0:
            descriptions = ["normal rules"]
        return descriptions
            
    def checkRules(self, current_game, status, specific_parameter):
        # Check the rules corresponding to the current state 
        replace_action = False
        if status == "end turn":
            appliquer = True
            while appliquer:
                appliquer = False
                for i in range(len(self.status)):
                    if status in self.status[i]:
                        if self.rules[i].applyRule(current_game, status, specific_parameter): 
                            appliquer = True
            return False
        else:
            for i in range(len(self.status)):   
                if status in self.status[i]:
                    if self.rules[i].applyRule(current_game, status, specific_parameter): 
                        replace_action = True
            return replace_action


class inventory:
    def __init__(self, starting_inventory):
        self.inventory = {"circle": 0, "triangle": 0, "square": 0, "quantum": 0}
        for item in starting_inventory:
            self.inventory[item] = starting_inventory[item]

    def dec(self, type):
        self.inventory[type] -= 1

    def add(self, type):
        self.inventory[type] += 1

  
class cursor:
    def __init__(self, initial_position, cores_positions, strength=1, speed=1):
        self.status = "normal"
        self.total_strength = strength
        self.current_strength = strength
        self.position = initial_position
        for core in cores_positions:
            if self.position == core:
                self.changeStatus("strong")
        self.total_speed = speed
        self.current_speed = speed
    
    def changeStatus(self, status):
        if status == "normal":
            self.current_strength -= 1
            if self.current_strength < 1:
                self.status = status
        else:
            self.current_strength = self.total_strength
            self.status = status

    def moveCursor(self, template_grid, pieces_tracker, direction, cores_positions, puzzle):
        # Check if the position is valid and if there already is a piece at the position
        do_we_move = True 
        destination = azzlay_common_functions.sumLists(self.position, azzlay_common_functions.readDir(direction))
        des_cell = azzlay_common_functions.whatIsInCell(destination, template_grid)
        if des_cell == "not in grid" or des_cell is None: 
            do_we_move = False    
        
        if do_we_move:
            if puzzle.Rules_Tracker.checkRules(puzzle, "moving cursor", direction):
                return True
            who_is_here = pieces_tracker.whoIsHere(destination)
            if who_is_here == "nobody":
                # Move cursor
                self.position = destination
                for core in cores_positions:
                    if self.position == core:
                        self.changeStatus("strong")
                puzzle.Rules_Tracker.checkRules(puzzle, "moved cursor", direction)
                return True
            else:
                # Move piece then move cursor if its status is set to strong
                if self.status == "strong" and self.current_strength > 0:
                    if pieces_tracker.movePiece(who_is_here, template_grid, direction):
                        self.changeStatus("normal")
                        self.position = destination
                        for core in cores_positions:
                            if self.position == core:
                                self.changeStatus("strong")
                        puzzle.Rules_Tracker.checkRules(puzzle, "moved cursor", direction)
                        return True
            return False
