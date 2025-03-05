# app.py
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow all origins for debugging

# Store game state
players = {}
game_rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    logging.debug('Client connected')
    print('Client connected')

@socketio.on('join_game')
def handle_join_game(data):
    # Create a room or join an existing one
    room = 'game_room'
    player_id = data.get('player_id')
    
    logging.debug(f'Player {player_id} attempting to join game')
    print(f'Player {player_id} attempting to join game')
    
    players[player_id] = {
        'choice': None,
        'room': room
    }
    
    # If room doesn't exist, initialize it
    if room not in game_rooms:
        game_rooms[room] = {
            'players': set(),
            'choices': {}
        }
    
    game_rooms[room]['players'].add(player_id)
    
    logging.debug(f'Players in room: {game_rooms[room]["players"]}')
    print(f'Players in room: {game_rooms[room]["players"]}')
    
    emit('joined_game', {'message': f'Player {player_id} joined the game'}, room=room)

@socketio.on('player_choice')
def handle_player_choice(data):
    player_id = data.get('player_id')
    choice = data.get('choice')
    room = players[player_id]['room']
    
    logging.debug(f'Player {player_id} chose {choice}')
    print(f'Player {player_id} chose {choice}')
    
    # Store player's choice
    players[player_id]['choice'] = choice
    game_rooms[room]['choices'][player_id] = choice
    
    logging.debug(f'Current choices: {game_rooms[room]["choices"]}')
    print(f'Current choices: {game_rooms[room]["choices"]}')
    
    # Check if both players have made a choice
    if len(game_rooms[room]['choices']) == 2:
        determine_winner(room)

def determine_winner(room):
    choices = game_rooms[room]['choices']
    players_in_room = list(choices.keys())
    
    if len(players_in_room) < 2:
        return
    
    player1, player2 = players_in_room
    choice1, choice2 = choices[player1], choices[player2]
    
    logging.debug(f'Determining winner: {player1}({choice1}) vs {player2}({choice2})')
    print(f'Determining winner: {player1}({choice1}) vs {player2}({choice2})')
    
    # Winning logic
    result = 'tie'
    if choice1 != choice2:
        if (
            (choice1 == 'rock' and choice2 == 'scissors') or
            (choice1 == 'scissors' and choice2 == 'paper') or
            (choice1 == 'paper' and choice2 == 'rock')
        ):
            result = player1
        else:
            result = player2
    
    logging.debug(f'Winner: {result}')
    print(f'Winner: {result}')
    
    # Emit result to players
    emit('game_result', {
        'winner': result,
        'choices': choices
    }, room=room)
    
    # Reset game state
    game_rooms[room]['choices'] = {}

@socketio.on('disconnect')
def handle_disconnect():
    logging.debug('Client disconnected')
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)