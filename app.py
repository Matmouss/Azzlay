from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit, join_room
from config import Config
import azzlay.access_puzzles
import uuid
import copy
import azzlay.azzlay_classes

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)

games = {}  # Stocke les états des jeux par session ID
puzzle_order_tutorials = azzlay.access_puzzles.load_puzzle_order('azzlay/tutorials.json')
puzzle_order_beta = azzlay.access_puzzles.load_puzzle_order('azzlay/first_levels.json')



# Routes Flask
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/more')
def more():
    return render_template('more.html')

@app.route('/puzzles/<world_name>')
def choose_puzzle(world_name):
    list_of_worlds = azzlay.access_puzzles.getWorldsFiles()
    monde = next((world for world in list_of_worlds if world["name"] == world_name), None)
    if monde:
        list_of_puzzles = azzlay.access_puzzles.load_puzzles_from_json(monde["path"])
        niveaux = [puzzle["name"] for puzzle in list_of_puzzles]
        return render_template('puzzles.html', niveaux=niveaux, world_name=world_name)
    return "World not found", 404

@app.route('/start-game/<world_name>/<puzzle_name>')
def start_game(world_name, puzzle_name):
    global current_game, games, temp_previous

    session_id = str(uuid.uuid4())  # Génère un ID de session unique
    session['session_id'] = session_id
    session['world_name'] = world_name
    session['puzzle_name'] = puzzle_name

    list_of_worlds = azzlay.access_puzzles.getWorldsFiles()
    monde = next(world for world in list_of_worlds if world["name"] == world_name)
    list_of_puzzles = azzlay.access_puzzles.load_puzzles_from_json(monde["path"])
    puzzle = next(puzzle for puzzle in list_of_puzzles if puzzle["name"] == puzzle_name)
    current_game = azzlay.azzlay_classes.Game(puzzle)

    games[session_id] = current_game  # Sauvegarde le jeu dans le dictionnaire games
    if world_name == "Puzzles beta":
        current_game.file_path = "azzlay/first_levels.json"
        next_level = puzzle_order_beta[puzzle_name]
    else:
        current_game.file_path = "azzlay/" + str(world_name) + ".json"
        next_level = puzzle_order_tutorials[puzzle_name]


    game_state = azzlay.azzlay_display.displayGame(current_game)

    

    return render_template('game.html', game_state=game_state, world_name=world_name, puzzle_name=puzzle_name, next_level=next_level)


@socketio.on("start")
def handle_start_game():
    sid = session['session_id']
    join_room(sid)
    if not validSid(sid):
        emit('restart', to = sid)
    else:
        game = games[sid]
        game_state = azzlay.azzlay_display.displayGame(game)
        socketio.emit('game_start', {'state': game_state}, to = sid)

@socketio.on('loop')
def game_loop():
    sid = session['session_id']
    if not validSid(sid):
        emit('restart', to = sid)
    else:
        game = games[sid]
        game_state = azzlay.azzlay_display.displayGame(game)
        socketio.emit('game_state', {'state': game_state}, to = sid)


@app.route('/select')
def play_game():
    list_of_worlds = azzlay.access_puzzles.getWorldsFiles()
    return render_template('select.html', worlds=list_of_worlds)


@socketio.on('game_action')
def handle_game_action(data):
    id = session['session_id']
    selecting = False
    action = data['action']
    if id in games:
        if not validSid(id):
            emit('restart', to = id)
        else :
            game = games[id]
            if game.nb_of_moves == 0:
                file_path = game.file_path
                game = gameReset(game.puzzle)
                game.file_path = file_path
                game.pieces_tracker = copy.deepcopy(azzlay.azzlay_classes.pieces_tracker(game.puzzle["starting pieces"]))
            result = False
            if game.state != "ended" and game.nb_of_moves < 300 : 
                temp_previous = azzlay.azzlay_classes.previous_state(game)
                if not selecting and action in ['up', 'down', 'left', 'right']:
                    result = game.cursor.moveCursor(game.grid_template.full_grid, game.pieces_tracker, action, game.cores, game)
                    if result:
                        game.nb_of_moves += 1
                        game.previous_state = azzlay.azzlay_classes.previous_state(temp_previous)
                        if game.nb_of_moves>2 and game.previous_state != None and game.previous_state.previous_state != None and game.previous_state.previous_state.previous_state != None:
                            game.previous_state.previous_state.previous_state = None
                    
                        # Apply upgrades, rules and check goals after each move
                        game.Rules_Tracker.checkRules(game, "end turn", None)
                        game.pieces_tracker.checkUpgrades(game.grid_template.full_grid, game)
                        game.Goals_Tracker.checkGoals(game)
                        
                        if game.Goals_Tracker.isWinner():
                            game.state = "ended"
                            game.checkBest()
                            emit('game_won', {'nb_moves':  game.nb_of_moves, 'best': game.best_score},to=id)

                elif action == 'enter':
                    if not selecting:
                        emit('piece_selection', None, to=id)

                elif action == 'space':
                        if not game.previous_state == None:
                            gameCopy(game, game.previous_state)

                elif action == "restart":
                    file_path = game.file_path
                    game = gameReset(game.puzzle)
                    game.file_path = file_path
                    game.pieces_tracker = copy.deepcopy(azzlay.azzlay_classes.pieces_tracker(game.puzzle["starting pieces"]))
                            
                games[id] = game
                updated_game_state = azzlay.azzlay_display.displayGame(game)
                socketio.emit('game_state', {'state': updated_game_state},to=id)

@socketio.on('selected_piece')
def handle_selected_piece(data):
    id = session['session_id']
    selecting = False
    if id in games:
        if not validSid(id):
            emit('restart', to = id)
        else :
            game = games[id]
            selecting = False
            index = data["index"]
            if index == -1:
                piece = "end"
            else:
                pieces = list(game.inventory.inventory.keys())
                piece = pieces[int(index)]
            result = game.placePiece(piece)

            if result:
                temp_previous = azzlay.azzlay_classes.previous_state(game)
                game.nb_of_moves += 1
                game.previous_state = azzlay.azzlay_classes.previous_state(temp_previous)
                if game.nb_of_moves>2 and game.previous_state.previous_state.previous_state != None:
                    game.previous_state.previous_state.previous_state = None

                game.Rules_Tracker.checkRules(game, "end turn", None)
                game.pieces_tracker.checkUpgrades(game.grid_template.full_grid, game)
                game.Goals_Tracker.checkGoals(game)
            
            if game.Goals_Tracker.isWinner():
                game.state = "ended"
                game.checkBest()
                emit('game_won', {'nb_moves':  game.nb_of_moves, 'best': game.best_score},to=id)
    games[id] = game
    updated_game_state = azzlay.azzlay_display.displayGame(game)
    socketio.emit('game_state', {'state': updated_game_state},to=id)

def validSid(sid):
    try: 
        games[sid]
        return True
    except: return False

def gameCopy(state, new_state):
        state.state = new_state.state
        state.nb_of_moves = new_state.nb_of_moves
        state.pieces_tracker = new_state.pieces_tracker
        state.previous_state = new_state.previous_state
        state.inventory = new_state.inventory
        state.cursor = new_state.cursor

def gameReset(puzzle):
    return azzlay.azzlay_classes.Game(puzzle)



if __name__ == "__main__":
    socketio.run(app, host='127.0.0.1', port=5000)
