from stockfish import Stockfish
stockfish = Stockfish(parameters={
    "Debug Log File": "",
    "Contempt": 0,
    "Min Split Depth": 0,
    "Threads": 1, # More threads will make the engine stronger, but should be kept at less than the number of logical processors on your computer.
    "Ponder": "true",
    "Hash": 2048, # Default size is 16 MB. It's recommended that you increase this value, but keep it as some power of 2. E.g., if you're fine using 2 GB of RAM, set Hash to 2048 (11th power of 2).
    "MultiPV": 1,
    "Skill Level": 200,
    "Move Overhead": 10,
    "Minimum Thinking Time": 20,
    "Slow Mover": 1000,
    "UCI_Chess960": "false",
    "UCI_LimitStrength": "false",
    "UCI_Elo": 3000
}, depth=15)

def stockfishInit():
    stockfish.set_position()

def addMove(move):
    stockfish.make_moves_from_current_position([move])


def getAIMove(validMoves):
    move = stockfish.get_best_move()
    stockfish.make_moves_from_current_position([move])
    for temp_move in validMoves:
        if temp_move.getChessNotation() == move:
            return temp_move
        

