# app.py
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Store game state
players = {}
game_rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('join_game')
def handle_join_game(data):
    # Create a room or join an existing one
    room = 'game_room'
    player_id = data.get('player_id')
    
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
    emit('joined_game', {'message': f'Player {player_id} joined the game'}, room=room)

@socketio.on('player_choice')
def handle_player_choice(data):
    player_id = data.get('player_id')
    choice = data.get('choice')
    room = players[player_id]['room']
    
    # Store player's choice
    players[player_id]['choice'] = choice
    game_rooms[room]['choices'][player_id] = choice
    
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
    
    # Emit result to players
    emit('game_result', {
        'winner': result,
        'choices': choices
    }, room=room)
    
    # Reset game state
    game_rooms[room]['choices'] = {}

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True)