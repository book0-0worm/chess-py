import random
from stockfish import Stockfish
stockfish = Stockfish(parameters={"UCI_Elo": 900})
print(stockfish.get_best_move())





def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]