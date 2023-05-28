'''
This is our main driver file, it wiill be responsible for handling user inpu and displaying the current GameState
'''

import pygame as p
import ChessEngine

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
The main dirver for our code. This will hander user input andd updating graphics
'''
def main():
  p.init()
  screen = p.display.set_mode((WIDTH, HEIGHT))
  clock = p.time.Clock()
  screen.fill(p.Color("white"))
  game_state = ChessEngine.GameState()
  validMoves = game_state.getValidMoves()
  moveMade = False # flag variable for when a move is made

  loadImages() # only do this once, before the while loop
  running = True
  sqSelected = () # no square selected initially, keep track of last click (tuple(row, coloumn))
  playerClicks = [] # keep track of player clicks (two tuples: [(x,y), (x,y)])
  
  while running:
    for e in p.event.get():
      if e.type == p.QUIT:
        running = False
      # mouse handler
      elif e.type == p.MOUSEBUTTONDOWN:
        location = p.mouse.get_pos() # (x,y) position of the mouse
        col = location[0]//SQUARE_SIZE
        row = location[1]//SQUARE_SIZE
        if sqSelected == (row, col): # if the user selected same square
          sqSelected == () # selected square becomes nothing
          playerClicks = [] # no player clicks
        else:
          sqSelected = (row, col)
          playerClicks.append(sqSelected) # add for both 1st and 2nd clicks
        if len(playerClicks) == 2: # after second click
          move = ChessEngine.Move(playerClicks[0], playerClicks[1], game_state.board)
          print(move.getChessNotation())
          if move in validMoves:
            game_state.makeMove(move)
            moveMade = True
            sqSelected = () # reset user clicks
            playerClicks = []
          else:
            playerClicks = [sqSelected]
      # key handlers
      elif e.type == p.KEYDOWN:
        if e.key == p.K_z: # undo when z is pressed
          game_state.undoMove()
          moveMade = True

    if moveMade:
      validMoves = game_state.getValidMoves()
      moveMade = False



    drawGameState(screen, game_state)
    clock.tick(MAX_FPS)
    p.display.flip()

'''    
Responsible for all the graphics within a current game state
'''
def drawGameState(screen, game_state):
  drawBoard(screen) # draw squares on the board
  # add in piece highlighting or move suggestions (later)
  drawPieces(screen, game_state.board) # draw pieces on top of those squares


'''
Draw the squares on the board. The top left square is always light
'''
def drawBoard(screen):
  colors = [p.Color("white"), p.Color("gray")]
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

if __name__ == "__main__":
  main()





