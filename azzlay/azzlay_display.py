# azzlay_display.py
# Fonctions d'affichage pour une interface web

def handleArrows(key):
    key_map = {
        113: "quit",
        81: "quit",
        "ArrowUp": "up",
        "ArrowDown": "down",
        "ArrowRight": "right",
        "ArrowLeft": "left",
        "Enter": "enter",
        10: "enter",
        11: "enter",
        114: "restart",
        82: "restart"
    }
    return key_map.get(key, "nothing")

def displayVictory(game_state):
    return {
        "type": "victory",
        "grid": game_state.createDisplayGrid(),
        "title": "Y O U  W I N !",
        "goals": game_state.goal_tracker.display_descriptions,
        "extra_text": f"Number of moves: {game_state.nb_of_moves}\nPress 'r' to restart or 'q' to quit"
    }

def displayGame(game):
    # The function that triggers all the others display functions
    grid_state = game.createDisplayGrid()
    grid_overlay = game.createOverlayMap()
    inventory = game.inventory.inventory if game.inventory.inventory else {}
    goals = game.Goals_Tracker.display_descriptions if game.Goals_Tracker.display_descriptions else []
    rules = game.Rules_Tracker.getDescriptions() if game.Rules_Tracker.descriptions else []
    extra_text = game.extra_text if game.extra_text else ""
    moves = game.nb_of_moves

    return {
        "grid": grid_state,
        "overlay": grid_overlay,
        "inventory": inventory,
        "goals": goals, 
        "rules": rules,
        "extra_text": extra_text,
        "moves": moves
    }

def createMenu(menu_name, menu_options, menu_cursor="-->", center=2):
    return {
        "type": "menu",
        "menu_name": menu_name,
        "menu_options": menu_options,
        "menu_cursor": menu_cursor,
        "center": center
    }
