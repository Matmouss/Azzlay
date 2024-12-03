#rules !!!!!!!!!!!! 
#rules activate during theit corresponding game state
#a rule checks the current puzzle situation and applys the ruling
#different states : "start game", "upgrade","moving cursor","moving piece", "end turn"
from . import azzlay_common_functions

"""

bien utiliser les préfixes suivants:

item type
item position

pour que les items puissent s'initier correctement

"""

class rules:
    def __init__(self, description, initial_parameters, status = ""):
        self.description = description
        self.parameters = initial_parameters
        self.status = status
        self.secret = False

    def isRightStatus(self, game_status):
        return game_status == self.status

    def applyRule(self, puzzle, status, specifique_parameter):
        return False

class cursorStrength(rules):
    #parameters {"strength"}
    def __init__(self, description, initial_parameters, status = "start game"):
        super().__init__(description, initial_parameters, status)

    def applyRule(self, puzzle, status, specifique_parameter):
        puzzle.cursor.total_strength = self.parameters["strength"]
        puzzle.cursor.current_strength = self.parameters["strength"]

class cursorSpeed(rules):
    #parameters {"speed"}
    def __init__(self, description, initial_parameters, status = "start game"):
        super().__init__(description, initial_parameters, status)

    def applyRule(self, puzzle, status, specifique_parameter):
        puzzle.cursor.total_speed = self.parameters["speed"]
        puzzle.cursor.current_speed = self.parameters["speed"]

class modifyUpgrades(rules):
    def __init__(self, description, initial_parameters, status = "placing"):
        super().__init__(description, initial_parameters, status)

    #parameters : "type", "upgrade"
    def applyRule(self, puzzle, status, current_param):
        if current_param["piece"]["type"] == self.parameters["type"]:
            for item in current_param["neighbours"]:
                if item["type"] == current_param["piece"]["type"]:
                    puzzle.pieces_tracker.delPiece(item)
                    puzzle.pieces_tracker.delPiece(current_param["piece"])
                    puzzle.pieces_tracker.addPiece({"type": self.parameters["upgrade"], "position": current_param["piece"]["position"]})
                    puzzle.pieces_tracker.piece_moved.append({"type": self.parameters["upgrade"], "position": current_param["piece"]["position"]})
                    self.secret = False
                    break
                elif item["type"] == "quantum":
                    puzzle.pieces_tracker.delPiece(item)
                    puzzle.pieces_tracker.delPiece(current_param["piece"])
                    puzzle.pieces_tracker.addPiece({"type": self.parameters["upgrade"], "position": current_param["piece"]["position"]})
                    puzzle.pieces_tracker.piece_moved.append({"type": self.parameters["upgrade"], "position": current_param["piece"]["position"]})
                    self.secret = False
                    break
            return True 

class magneticField(rules):
    #parameters {"direction", "strength"}
    def __init__(self, description, initial_parameters, status = "end turn"):
        super().__init__(description, initial_parameters, status)

    def applyRule(self, puzzle, status, specifique_parameter):
        if puzzle.cursor.current_speed < 1:
            for i in range(self.parameters["strength"]):
                for piece in puzzle.pieces_tracker.pieces:
                    puzzle.pieces_tracker.movePiece(piece, puzzle.grid_template.full_grid, self.parameters["direction"])
                puzzle.cursor.moveCursor(puzzle.grid_template.full_grid, puzzle.pieces_tracker, self.parameters["direction"], puzzle.cores, puzzle)
                puzzle.pieces_tracker.checkUpgrades(puzzle.grid_template.full_grid, puzzle)
        return False

class changePieceWhenTurn(rules):
    #parameters {"turn", "type", "upgrade"}
    def __init__(self, description, initial_parameters, status = "end turn"):
        super().__init__(description, initial_parameters, status)

    def applyRule(self, puzzle, status, specifique_parameter):
        if puzzle.nb_of_moves % self.parameters["turn"] == 0:
            for piece in puzzle.pieces_tracker.pieces:
                if piece["type"] == self.parameters["type"]:
                    puzzle.pieces_tracker.delPiece(piece)
                    puzzle.pieces_tracker.addPiece({"type": self.parameters["upgrade"], "position": piece["position"]})
                    self.applyRule(puzzle, status, specifique_parameter)
                    break
        return False


class deletePieceOnItem(rules):
    #parameters {"item", "position", "type"}
    def __init__(self, description, initial_parameters, status = "end turn"):
        super().__init__(description, initial_parameters, status)

    def applyRule(self, puzzle, status, specifique_parameter):
        for piece in puzzle.pieces_tracker.pieces:
            if piece["position"] == self.parameters["position"] and piece["type"] == self.parameters["type"]:
                puzzle.pieces_tracker.delPiece(piece)
        return False

class movePieceWhenMove(rules):
    #parameters {"type"}
    def __init__(self, description, initial_parameters, status = "moved cursor"):
        super().__init__(description, initial_parameters, status)

    def applyRule(self, puzzle, status, specifique_parameter):
        for piece in puzzle.pieces_tracker.pieces:
            if piece["type"] == self.parameters["type"]:
                do = True
                for item in puzzle.pieces_tracker.piece_moved:
                    if piece["position"] == item["position"]:
                        do = False
                if do:
                    puzzle.pieces_tracker.movePiece(piece,puzzle.grid_template.full_grid,specifique_parameter)
        return False

class itemMovesPieces(rules):
    #parameters {"item type", "item position", "dir"}
    def __init__(self, description, initial_parameters, status="end turn"):
        super().__init__(description, initial_parameters, status)

    def applyRule(self, puzzle, status, specifique_parameter):
        ret = False
        for piece in puzzle.pieces_tracker.pieces:
            if piece["position"] == self.parameters["item position"]:
                ret = True
                puzzle.pieces_tracker.movePiece(piece,puzzle.grid_template.full_grid, self.parameters["dir"])
        return ret
        

rule_type_mapping = {
    "modifyUpgrades": modifyUpgrades,
    "cursorStrength": cursorStrength,
    "cursorSpeed": cursorSpeed,
    "magneticField": magneticField,
    "changePieceWhenTurn": changePieceWhenTurn,
    "deletePieceOnItem": deletePieceOnItem,
    "movePieceWhenMove": movePieceWhenMove,
    "itemMovesPieces":itemMovesPieces

    #others mappings
}
