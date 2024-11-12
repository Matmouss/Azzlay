from flask_socketio import emit, join_room
from game_manager import games, update_game_state, valid_sid, reset_game, game_copy, process_game_action
import copy
import azzlay.azzlay_display

def handle_start_game(data):
    sid = data['sessionId']
    join_room(sid)
    if not valid_sid(sid):
        emit('restart', to=sid)
    else:
        game = games[sid]
        game_state = display_game(game)  # Fonction d'affichage du jeu
        emit('game_start', {'state': game_state}, to=sid)

def handle_game_action(data):
    sid = data['sessionId']
    action = data['action']
    selecting = False  # Suivi de l'état de sélection

    if not valid_sid(sid):
        emit('restart', to=sid)
    else:
        game = games[sid]

        if action in ['up', 'down', 'left', 'right']:
            result = update_game_state(game, action)
            if result:
                result_data = process_game_action(game, sid)
                if result_data['game_won']:
                    emit('game_won', {'nb_moves': result_data['nb_moves'], 'best': result_data['best']}, to=sid)

        elif action == 'enter':
            if not selecting:
                emit('piece_selection', None, to=sid)
                selecting = True

            @socketio.on('selected_piece')
            def handle_selected_piece(index):
                selecting = False
                index = index['index']
                if index == -1:
                    piece = "end"
                else:
                    pieces = list(game.inventory.inventory.keys())
                    piece = pieces[int(index)]
                result = game.placePiece(piece)

                if result:
                    result_data = process_game_action(game, sid)
                    if result_data['game_won']:
                        emit('game_won', {'nb_moves': result_data['nb_moves'], 'best': result_data['best']}, to=sid)

        elif action == 'space':
            if game.previous_state:
                game_copy(game, game.previous_state)

        elif action == 'restart':
            game = reset_game(game)

        games[sid] = game
        updated_game_state = display_game(game)
        emit('game_state', {'state': updated_game_state}, to=sid)

def display_game(game):
    return azzlay.azzlay_display.displayGame(game)
