from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

games = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/new-game', methods=['POST'])
def new_game():
    game_id = str(random.randint(1000, 9999))
    # Generate separate targets for each player
    games[game_id] = {
        'player1': {
            'target': random.randint(1, 100),
            'attempts': 0,
            'found': False
        },
        'player2': {
            'target': random.randint(1, 100),
            'attempts': 0,
            'found': False
        },
        'current_phase': 1,  # 1 = Player 1's turn, 2 = Player 2's turn
        'game_over': False
    }
    return jsonify({
        'game_id': game_id,
        'message': 'New game started'
    })

@app.route('/api/submit-guess', methods=['POST'])
def submit_guess():
    game_id = request.json['game_id']
    player = request.json['player']
    guess = request.json['guess']
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    
    # Validate it's the correct player's turn
    if (game['current_phase'] == 1 and player != 1) or (game['current_phase'] == 2 and player != 2):
        return jsonify({'error': 'Not your turn'}), 400
    
    # Update attempts
    player_key = f'player{player}'
    game[player_key]['attempts'] += 1
    
    # Check guess against the player's specific target
    if guess == game[player_key]['target']:
        game[player_key]['found'] = True
        
        if game['current_phase'] == 1:
            # Player 1 found their number, switch to Player 2's phase
            game['current_phase'] = 2
            response = {
                'correct': True,
                'message': f'Player 1 found their number in {game["player1"]["attempts"]} attempts! Now Player 2\'s turn.',
                'attempts': game[player_key]['attempts'],
                'game_over': False,
                'phase_complete': True
            }
        else:
            # Player 2 found their number, game over
            game['game_over'] = True
            if game['player1']['attempts'] < game['player2']['attempts']:
                winner = 1
            elif game['player2']['attempts'] < game['player1']['attempts']:
                winner = 2
            else:
                winner = 0  # Draw
            
            response = {
                'correct': True,
                'message': f'Player 2 found their number in {game["player2"]["attempts"]} attempts. ' +
                          f'Player 1: {game["player1"]["attempts"]} attempts, Player 2: {game["player2"]["attempts"]} attempts. ' +
                          ('Player 1 wins!' if winner == 1 else 
                           'Player 2 wins!' if winner == 2 else "It's a draw!"),
                'attempts': game[player_key]['attempts'],
                'game_over': True,
                'winner': winner
            }
    else:
        hint = 'lower' if guess > game[player_key]['target'] else 'higher'
        response = {
            'correct': False,
            'hint': hint,
            'message': f'Player {player}, try a {hint} number',
            'attempts': game[player_key]['attempts'],
            'game_over': False
        }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)