# ici les objectifs 
class goals:
    def __init__(self, description, parameters):
        self.description = description
        self.parameters = parameters

    def checkGoal(self, puzzle):
        pass

class EmptyInventory(goals):
    #parameters : nothing {}
    def checkGoal(self, puzzle):
        ret = True
        for item in puzzle.inventory.inventory:
            if puzzle.inventory.inventory[item] != 0:
                ret = False
        return ret

class NoPiecesOfType(goals):
    # parameters : {type}
    def checkGoal(self, puzzle):
        ret = True
        for item in puzzle.pieces_tracker.pieces:
            if item["type"] == self.parameters["type"]: 
                ret = False
        return ret

class NbOfPiecesOfType(goals):
    #parameters {"type", "number"}
    def checkGoal(self, puzzle):
        ret = False
        if puzzle.pieces_tracker.count[self.parameters["type"]] == self.parameters["number"]:
            ret = True
        return ret

class pieceOnItem(goals):
    #parameters {"piece type", "item type", "item position"}
    def checkGoal(self, puzzle):
        ret = False 
        for piece in puzzle.pieces_tracker.pieces:
            if piece["type"] == self.parameters["piece type"]:
                for item in puzzle.items:
                    if item["type"] == self.parameters["item type"] and piece["position"] == item["position"]:
                        ret = True
        return ret

class cursorOnItem(goals):
    #parameters {"item type", "item position"}
    def checkGoal(self, puzzle):
        ret = False
        for item in puzzle.items:
            if item["type"] == self.parameters["item type"] and puzzle.cursor.position == item["position"]:
                ret = True
        return ret

class ImpossibleChallenge(goals):
    #parameters rien nada {}
    def checkGoal(self, puzzle):
        pass

goal_type_mapping = {
    "EmptyInventory": EmptyInventory,
    "NoPiecesOfType": NoPiecesOfType,
    "NbOfPiecesOfType": NbOfPiecesOfType,
    "ImpossibleChallenge": ImpossibleChallenge,
    "pieceOnItem": pieceOnItem,
    "cursorOnItem": cursorOnItem,
    # ... other mappings
}
