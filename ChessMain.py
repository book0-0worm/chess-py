'''
This is our main driver file, it wiill be responsible for handling user inpu and displaying the current GameState
'''

import pygame as p
import ChessEngine, ChickenStock
import os
import time
import chalk

red = chalk.Chalk('red')
green = chalk.Chalk('green')
yellow = chalk.Chalk('yellow')
blue = chalk.Chalk('blue')
cyan = chalk.Chalk('cyan')
magenta = chalk.Chalk('magenta')


def clear():
    # checks for os and sends appropriate clear command
    if os.name == 'posix':
        os.system("clear")
    else:
        os.system("cls")



WIDTH = HEIGHT = 512 # 400 also works
DIMENSION = 8 # dimensions of a hess board are 8x8
SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # for animations
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called exactly once in the main
'''
def loadImages():
  pieces = ['wp', 'wR', 'wN', 'wK', 'wB', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
  for piece in pieces:
    IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))
# Note: we can access an image by saying "IMAGES['wp']" 

'''
The main driver for our code. This will hander user input and updating graphics
'''
def main():
  p.init()
  screen = p.display.set_mode((WIDTH, HEIGHT))
  clock = p.time.Clock()
  screen.fill(p.Color("white"))
  game_state = ChessEngine.GameState()
  validMoves = game_state.getValidMoves()
  moveMade = False # flag variable for when a move is made
  animate = False # flag variable for when we should animate a move
  loadImages() # only do this once, before the while loop
  running = True
  sqSelected = () # no square selected initially, keep track of last click (tuple(row, coloumn))
  playerClicks = [] # keep track of player clicks (two tuples: [(x,y), (x,y)])
  gameOver = False
  playerOne = True # if a human is playing white, then this will be True, else False
  playerTwo = False # if a human is playing black, then this will be True, else False
  while running:
    humanTurn = (game_state.whiteToMove and playerOne) or (not game_state.whiteToMove and playerTwo) # check if it is a human's turn
    for e in p.event.get():
      if e.type == p.QUIT: # quit the game when the user presses the x button
        running = False
      # mouse handler
      elif e.type == p.MOUSEBUTTONDOWN:
        if not gameOver and humanTurn: # if the game is not over and it is a human's turn
          location = p.mouse.get_pos() # (x,y) position of the mouse
          col = location[0]//SQUARE_SIZE
          row = location[1]//SQUARE_SIZE
          if sqSelected == (row, col): # if the user selected same square
            sqSelected == () # unselect
            playerClicks = [] # no player clicks
          else:
            sqSelected = (row, col)
            playerClicks.append(sqSelected) # add for both 1st and 2nd clicks
          if len(playerClicks) == 2: # after second click
            move = ChessEngine.Move(playerClicks[0], playerClicks[1], game_state.board)
            for i in range(len(validMoves)):
              if move == validMoves[i]:
                ChickenStock.addMove(move.getChessNotation())
                game_state.makeMove(validMoves[i])
                moveMade = True
                animate = True
                sqSelected = () # reset user clicks
                playerClicks = []
            if not moveMade: 
              playerClicks = [sqSelected]
      # key handlers
      
      elif e.type == p.KEYDOWN:
        if e.key == p.K_r: # reset the game when r is pressed
          running = False
          ChickenStock.stockfishInit()
          main()
        if e.key == p.K_q: # quit the game when q is pressed
          running = False


    # AI move finder logic
    if not gameOver and not humanTurn:
      AIMove = ChickenStock.getAIMove(validMoves)
      game_state.makeMove(AIMove)
      moveMade = True
      animate = True

    if moveMade: # if a move is made, update valid moves
      if animate: 
        animateMove(game_state.moveLog[-1], screen, game_state.board, clock)
      validMoves = game_state.getValidMoves()
      moveMade = False
      animate = False

    drawGameState(screen, game_state, validMoves, sqSelected)

    if game_state.checkmate: # check if the game is over
      gameOver = True 
      if game_state.whiteToMove:# if white is in checkmate
        drawText(screen, 'Black wins by checkmate')
      else: # if black is in checkmate
        drawText(screen, 'White wins by checkmate')
    elif game_state.stalemate: # check if the game is in stalemate
      gameOver = True
      drawText(screen, 'Stalemate')

    clock.tick(MAX_FPS)
    p.display.flip()

"""
Highlight square selected and moves for piece selected
"""
def highlightSquares(screen, game_state, validMoves, sqSelected):
  if sqSelected != (): # if a square is selected
    r, c = sqSelected # get row and coloumn of selected square
    if game_state.board[r][c][0] == ('w' if game_state.whiteToMove else 'b'): # sqSelected is a piece that can be moved
      # highlight selected square
      s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
      s.set_alpha(100) # transparency value -> 0 transparent; 255 opaque
      s.fill(p.Color('gold'))
      screen.blit(s, (c*SQUARE_SIZE, r*SQUARE_SIZE))
      # highlight moves from that square
      s.fill(p.Color('lightsteelblue'))
      for move in validMoves:
        if move.startRow == r and move.startCol == c:
          screen.blit(s, (move.endCol*SQUARE_SIZE, move.endRow*SQUARE_SIZE))


'''    
Responsible for all the graphics within a current game state
'''
def drawGameState(screen, game_state, validMoves, sqSelected):
  drawBoard(screen) # draw squares on the board
  highlightSquares(screen, game_state, validMoves, sqSelected) # highlight square selected and moves for piece selected
  drawPieces(screen, game_state.board) # draw pieces on top of those squares


'''
Draw the squares on the board. The top left square is always light
'''
def drawBoard(screen):
  global colors
  colors = [p.Color("blanchedalmond"), p.Color("burlywood")] # colors of the squares (light, dark)
  screen.fill(p.Color("white"))
  for r in range(DIMENSION):
    for c in range(DIMENSION):
      color = colors[((r+c) % 2)]
      p.draw.rect(screen,color, p.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

'''
Draw the pieces on the board using the current GameState.board
'''
def drawPieces(screen, board): 
  for r in range(DIMENSION):
    for c in range(DIMENSION):
      piece = board[r][c]
      if piece != "--": # not a empty square
        screen.blit(IMAGES[piece], p.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

"""
Animating a move
"""
def animateMove(move, screen, board, clock):
  global colors
  dR = move.endRow - move.startRow # delta row
  dC = move.endCol - move.startCol # ddelta coloumn
  framesPerSquare = 5 # frames to move one square
  frameCount = (abs(dR) + abs(dC)) * framesPerSquare # total number of frames for a move
  for frame in range(frameCount + 1):
    r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount) # current row and coloumn
    drawBoard(screen)
    drawPieces(screen, board)
    # erase the piece moved from its ending square
    color = colors[(move.endRow + move.endCol) % 2] # alternate between light and dark squares
    endSquare = p.Rect(move.endCol*SQUARE_SIZE, move.endRow*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE) # rectangle for end square
    p.draw.rect(screen, color, endSquare) # draw rectangle
    # draw captured piece onto rectangle
    if move.pieceCaptured != '--':
      screen.blit(IMAGES[move.pieceCaptured], endSquare) # draw captured piece onto rectangle
    # draw moving piece
    screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)) # draw moving piece
    p.display.flip() # update the screen
    clock.tick(60)   # 60 frames per second

def drawText(screen, text): # draw text on the screen
  font = p.font.SysFont("Courier", 32, True, False) # font type, size, bold, italics (for easy reference)
  textObject = font.render(text, 0, p.Color('Gray')) # text, antialiasing, color (for future reference)
  textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2) # center text
  screen.blit(textObject, textLocation) # draw text
  textObject = font.render(text, 0, p.Color('Black')) # text, antialiasing, color (for future reference)
  screen.blit(textObject, textLocation.move(2,2)) # draw text slightly offset for outline look

if __name__ == "__main__":
  clear()
  print(chalk.bold('''
Welcome to ''') + blue("Chess", bold=True, underline=True) + chalk.bold('''! You will be set up against ChickenStock, our unbeatable chess AI. Good luck!
To play, click on the piece you want to move, then click on the square you want to move it to.
If you want to restart, press 'r'. If you wish to quit, press 'q'.\n '''))
  eloChoosing = True
  while eloChoosing:

    print(chalk.bold(chalk.underline("Select the difficulty (ELO) you want to play at: ")))
    print(chalk.bold("[1] ") + cyan("500", bold=True))
    print(chalk.bold("[2] ") + green("700", bold=True))
    print(chalk.bold("[3] ") + yellow("1000", bold=True))
    print(chalk.bold("[4] ") + red("Unbeatable", bold=True))

    choice = input("Enter your choice: ")
    if choice == "1":
      ChickenStock.stockfish.update_engine_parameters({"UCI_LimitStrength": "true", "UCI_Elo": 500})
      eloChoosing = False
      main()
    elif choice == "2":
      ChickenStock.stockfish.update_engine_parameters({"UCI_LimitStrength": "true", "UCI_Elo": 700})
      eloChoosing = False
      main()
    elif choice == "3":
      ChickenStock.stockfish.update_engine_parameters({"UCI_LimitStrength": "true", "UCI_Elo": 1000})
      eloChoosing = False
      main()
    elif choice == "4":
      ChickenStock.stockfish.update_engine_parameters({"UCI_LimitStrength": "false", "UCI_Elo": 3000})
      eloChoosing = False
      main()
    else:
      print("Invalid input. Please try again.")
      time.sleep(1)
      clear()






