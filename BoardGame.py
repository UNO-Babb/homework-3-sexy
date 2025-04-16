#Owen Betts & Fatima Davila 
#4/15/2025
#Homework 3 - Pixel Pushers

from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

GRID_SIZE = 9
EMPTY = "white"
PLAYER_COLORS = {"player1": "pink", "player2": "blue"}

# Initialize game state
grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
grid[GRID_SIZE - 1][0] = PLAYER_COLORS["player1"]  # Bottom-left
grid[0][GRID_SIZE - 1] = PLAYER_COLORS["player2"]  # Top-right
current_player = "player1"

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, grid=grid, current_player=current_player)

@app.route("/select", methods=["POST"])
def select():
    global current_player
    data = request.json
    row, col = data["row"], data["col"]
    player = data["player"]

    if player != current_player:
        return jsonify(success=False, error="Not your turn")

    color = PLAYER_COLORS[player]

    if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
        return jsonify(success=False, error="Out of bounds")

    if grid[row][col] != EMPTY:
        return jsonify(success=False, error="Cell already taken")

    if not is_adjacent_to_player_color(row, col, color):
        return jsonify(success=False, error="Invalid move: not adjacent to your color")

    grid[row][col] = color

    if not has_moves(PLAYER_COLORS["player1"]):
        return jsonify(success=True, winner="player2")
    elif not has_moves(PLAYER_COLORS["player2"]):
        return jsonify(success=True, winner="player1")

    # Switch turns
    current_player = "player2" if current_player == "player1" else "player1"

    return jsonify(success=True, grid=grid, next_player=current_player)

def is_adjacent_to_player_color(row, col, color):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            if grid[r][c] == color:
                return True
    return False

def has_moves(color):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if grid[row][col] == EMPTY and is_adjacent_to_player_color(row, col, color):
                return True
    return False

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>2 Player Grid Game</title>
    <style>
        .grid {
            display: grid;
            grid-template-columns: repeat({{ grid|length }}, 40px);
            grid-gap: 2px;
        }
        .cell {
            width: 40px;
            height: 40px;
            border: 1px solid black;
        }
    </style>
</head>
<body>
    <h2>2 Player Grid Game - Turn: {{ current_player }}</h2>
    <h3>Player 1: pink | Player 2: blue</h3>
    <div class="grid">
        {% for row in range(grid|length) %}
            {% for col in range(grid[0]|length) %}
                <div class="cell" style="background-color: {{ grid[row][col] }}" 
                     onclick="selectSquare({{ row }}, {{ col }})"></div>
            {% endfor %}
        {% endfor %}
    </div>
    <script>
        let currentPlayer = '{{ current_player }}';

        function selectSquare(row, col) {
            fetch('/select', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({row: row, col: col, player: currentPlayer})
            }).then(response => response.json()).then(data => {
                if (data.success) {
                    if (data.winner) {
                        alert(data.winner + ' wins!');
                        location.reload();
                    } else {
                        location.reload();
                    }
                } else {
                    alert(data.error);
                }
            });
        }
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    app.run(debug=True)
