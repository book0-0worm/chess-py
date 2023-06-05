'''
This class is responsible for all the information about the current state of the chess game. It will also be responsible for determining the valid moves at the current state. It will also have a move log.
'''

class GameState():
  def __init__(self):
    # board is a 8x8 2d list, and each lemenet of the list has 2 characters
    # the first character assigns the color (b,w)
    # the second character assigns the type of piece(k,q,r,b,n,p)
    # "--" represents a empty square on the board
    self.board = [
      ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
      ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
      ["--", "--", "--", "--", "--", "--", "--", "--"],
      ["--", "--", "--", "--", "--", "--", "--", "--"],
      ["--", "--", "--", "--", "--", "--", "--", "--"],
      ["--", "--", "--", "--", "--", "--", "--", "--"],
      ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
      ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
    self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                          'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

    self.whiteToMove = True # white goes first
    self.moveLog = [] # make a new movelog
    self.whiteKingLocation = (7, 4) # starting location of white king
    self.blackKingLocation = (0, 4) # starting location of black king
    self.checkmate = False # set checkmate to false
    self.stalemate = False # set stalemate to false
    self.enpassantPossible = () # coordinates for the square where enpassant is possible
    self.currentCastlingRight = CastleRights(True, True, True, True) # castling rights for the current state of the game
    self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                         self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)] # log of castling rights so we can undo



  '''
  Takes a move as a parameter and executes it (this will not work for castling, pawn promotion, and en-passant)
  '''
  def makeMove(self, move):
    self.board[move.startRow][move.startCol] = "--"
    self.board[move.endRow][move.endCol] = move.pieceMoved
    self.moveLog.append(move) # log the move so we can undo it later
    self.whiteToMove = not self.whiteToMove # swap players
    # update the kings location if moved
    if move.pieceMoved == 'wK':
      self.whiteKingLocation = (move.endRow, move.endCol)
    elif move.pieceMoved == 'bK':
      self.blackKingLocation = (move.endRow, move.endCol)

    # pawn promotion
    if move.isPawnPromotion:
      self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q' # promote to whatever piece the user wants
      
    # enpassant move
    if move.isEnpassantMove:
      self.board[move.startRow][move.endCol] = '--' # capturing the pawn
    
    # update enpassantPossible variable
    if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: # only on 2 square pawn advances
      self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol) # integer division to get the row
    else:
      self.enpassantPossible = () # if not a 2 square pawn advance, then no enpassant is possible

    # castle move
    if move.isCastleMove:
      if move.endCol - move.startCol == 2: # kingside castle move
        self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] # moves the rook
        self.board[move.endRow][move.endCol+1] = '--' # erase old rook
      else: # queenside castle move
        self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] # moves the rook
        self.board[move.endRow][move.endCol-2] = '--' # erase old rook

    # Update castling rights - whenever it is a rook or a king move
    self.updateCastleRights(move)
    self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                              self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))
 

  '''
  Undo the last move made
  '''
  def undoMove(self):
    if len(self.moveLog) != 0: # make sure that there is a move to undo
      move = self.moveLog.pop()
      self.board[move.startRow][move.startCol] = move.pieceMoved
      self.board[move.endRow][move.endCol] = move.pieceCaptured
      self.whiteToMove = not self.whiteToMove # switch turns back
      # update kings position if needed
      if move.pieceMoved == "wK": # if the white king was moved
        self.whiteKingLocation = (move.startRow, move.startCol) # set the white king location
      elif move.pieceMoved == "bK": # if the black king was moved
        self.blackKingLocation = (move.startRow, move.startCol) # set the black king location
      # undo enpassant move
      if move.isEnpassantMove:
        self.board[move.endRow][move.endCol] = '--' # leave landing square blank
        self.board[move.startRow][move.endCol] = move.pieceCaptured # put the captured piece back
        self.enpassantPossible = (move.endRow, move.endCol) # set the enpassantPossible to the square where the pawn was captured
      # undo 2 square pawn advance
      if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
        self.enpassantPossible = ()
      # undo castling rights
      self.castleRightsLog.pop() # get rid of the new castle rights from the move we are undoing
      newRights = self.castleRightsLog[-1] # set the current castle rights to the last one in the list
      self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs) # set the current castle rights to the last one in the list
      # undo castle move
      if move.isCastleMove:
        if move.endCol - move.startCol == 2: # kingside
          self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1] # move the rook back
          self.board[move.endRow][move.endCol-1] = '--' # leave blank space where the rook was
        else: # queenside
          self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1] # move the rook back
          self.board[move.endRow][move.endCol+1] = '--' # leave blank space where the rook was



  '''
  Update the castle rights given the move
  '''
  def updateCastleRights(self, move):
    if move.pieceMoved == 'wK':
      self.currentCastlingRight.wks = False
      self.currentCastlingRight.wqs = False
    elif move.pieceMoved == 'bK':
      self.currentCastlingRight.bks = False
      self.currentCastlingRight.bqs = False
    elif move.pieceMoved == 'wR':
      if move.startRow == 7: # black row
        if move.startCol == 0: # left rook
          self.currentCastlingRight.wqs = False
        elif move.startCol == 7: # right rook
          self.currentCastlingRight.wks = False
    elif move.pieceMoved == 'bR':
      if move.startRow == 0: # white row
        if move.startCol == 0: # left rook
          self.currentCastlingRight.bqs = False
        elif move.startCol == 7: # right rook
          self.currentCastlingRight.bks = False
    #if a rook is captured
    if move.pieceCaptured == 'wR':
        if move.endRow == 7:
            if move.endCol == 0:
                self.currentCastlingRight.wqs = False
            elif move.endCol == 7:
                self.currentCastlingRight.wks = False
    elif move.pieceCaptured == 'bR':
        if move.endRow == 0:
            if move.endCol == 0:
                self.currentCastlingRight.bqs = False
            elif move.endCol == 7:
                self.currentCastlingRight.bks = False

  '''
  All moves considering checks
  '''
  def getValidMoves(self):
    tempEnpassantPossible = self.enpassantPossible # save the current enpassantPossible
    tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                    self.currentCastlingRight.wqs, self.currentCastlingRight.bqs) # save the current castle rights
    # 1.) generate all possible moves
    moves = self.getAllPossibleMoves()

    # 2,) for each move, make the move
    for i in range(len(moves)-1, -1, -1): # when removing from a list, go backwards in order not to skip
      self.makeMove(moves[i])
      # 3.) generate all opponent moves
      # 4.) for each of those moves, see if they attack the king
      self.whiteToMove = not self.whiteToMove # swap moves since make move switches the turns, so we switch back to check for checks
      if self.inCheck():
        moves.remove(moves[i]) # 5.) if they do attack the king, not valid move 
      self.whiteToMove = not self.whiteToMove
      self.undoMove()
    if len(moves) == 0: # either checkmate or stalemate
      if self.inCheck(): # if in check
        self.checkmate = True # set checkmate to true
      else:
        self.stalemate = True # set stalemate to true

    if self.whiteToMove:
      self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
    else:
      self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
    self.enpassantPossible = tempEnpassantPossible # set the enpassantPossible back to what it was before
    self.currentCastlingRight = tempCastleRights # set the castle rights back to what they were before
    return moves
        
  '''
  Determine if the current player is in check
  '''
  def inCheck(self): 
    if self.whiteToMove:
      return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
    else:
      return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

  '''
  Determine if the enemy can attack the square r, c
  '''
  def squareUnderAttack(self, r, c):
    self.whiteToMove = not self.whiteToMove # switch to opponents POV
    oppMoves = self.getAllPossibleMoves() 
    self.whiteToMove = not self.whiteToMove # switch back
    for move in oppMoves:
      if move.endRow == r and move.endCol == c: # square is under attack
        return True
    return False


  '''
  All moves without considering checks
  '''
  def getAllPossibleMoves(self):
    moves = []
    for r in range(len(self.board)):
      for c in range(len(self.board[r])):
        turn = self.board[r][c][0]
        if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
          piece = self.board[r][c][1]
          self.moveFunctions[piece](r, c, moves) # calls the appropriate move function based on piece type
    return moves

  '''
  Get all pawn moves for the pawn located at row, col and add these moves to the list
  '''
  def getPawnMoves(self, r, c, moves):
    if self.whiteToMove: # white pawn moves
      if self.board[r-1][c] == "--": # 1 square pawn movement
        moves.append(Move((r, c), (r-1, c), self.board))
        if r == 6 and self.board[r-2][c] == "--": # 2 square pawn movement
          moves.append(Move((r,c), (r-2, c), self.board))
      if c-1 >= 0: # captures to left
        if self.board[r-1][c-1][0] == 'b': # enemy piece to capture
          moves.append(Move((r, c), (r-1, c-1), self.board))
        elif (r-1, c-1) == self.enpassantPossible:
          moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove = True))
      if c+1 <= 7: # captures to right
        if self.board[r-1][c+1][0] == 'b': # enemy piece to capture
          moves.append(Move((r, c), (r-1, c+1), self.board))
        elif (r-1, c+1) == self.enpassantPossible:
          moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove = True))

    else: # black pawn moves
      if self.board[r+1][c] == "--": # 1 square move
        moves.append(Move((r, c), (r + 1, c), self.board))
        if r == 1 and self.board[r + 2][c] == "--": #2 square move
          moves.append(Move((r, c), ( r + 2, c), self.board))
      # captures
      if c - 1 >= 0: # capture to left
        if self.board[r + 1][c -1][0] == "w":
          moves.append(Move((r, c), (r + 1, c - 1), self.board))
        elif (r + 1, c - 1) == self.enpassantPossible:
          moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove = True))
      if c + 1 <= 7: # capture to right
        if self.board[r + 1][c + 1][0] == 'w':
          moves.append(Move((r, c), (r + 1, c+ 1), self.board))
        elif (r + 1, c + 1) == self.enpassantPossible:
          moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove = True))
    # add pawn promotions later

  '''
  Get all the rook moves for the rook located at row, col and add these moves to the list
  '''
  def getRookMoves(self, r, c, moves):
    directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # up down right left
    enemyColor = "b" if self.whiteToMove else "w"
    for d in directions:
      for i in range(1, 8): # rook can move max of 7 squares
        endRow = r + d[0] * i
        endCol = c + d[1] * i
        if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
          endPiece = self.board[endRow][endCol]
          if endPiece == "--": # if its empty space and on board 
            moves.append(Move((r, c), (endRow, endCol), self.board))
          elif endPiece[0] == enemyColor: # a enemy piece valid
            moves.append(Move((r, c), (endRow, endCol), self.board))
            break
          else: # if friendly piece 
            break
        else: # if off board
          break

  '''
  Get all the knight moves for the knight located at row, col and add these moves to the list
  '''
  def getKnightMoves(self, r, c, moves):
    knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)) # the L shape directions
    allyColor = "w" if self.whiteToMove else "b"
    for m in knightMoves:
      endRow = r + m[0]
      endCol = c + m[1]
      if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
        endPiece = self.board[endRow][endCol]
        if endPiece[0] != allyColor: #not a ally piece (empty/enemy)
          moves.append(Move((r, c), (endRow, endCol), self.board))

  '''
  Get all the bishop moves for the bishop located at row, col and add these moves to the list
  '''
  def getBishopMoves(self, r, c, moves):
    directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # 4 diagnol directions
    enemyColor = "b" if self.whiteToMove else "w"
    for d in directions:
      for i in range(1, 8): # bishop can move max of 7 squares
        endRow = r + d[0] * i
        endCol = c + d[1] * i
        if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
          endPiece = self.board[endRow][endCol]
          if endPiece == "--": # if its empty space and on board 
            moves.append(Move((r, c), (endRow, endCol), self.board))
          elif endPiece[0] == enemyColor: # a enemy piece valid
            moves.append(Move((r, c), (endRow, endCol), self.board))
            break
          else: # if friendly piece 
            break
        else: # if off board
          break

  '''
  Get all the queen moves for the queen located at row, col and add these moves to the list
  '''
  def getQueenMoves(self, r, c, moves): # has the same movement possibilities as rook + bishop
    self.getRookMoves(r, c, moves)
    self.getBishopMoves(r, c, moves)

  '''
  Get all the king moves for the king located at row, col and add these moves to the list
  '''
  def getKingMoves(self, r, c, moves):
    kingMoves = ((-1, -1), (-1, 0), (-1, 1,), (0, 1), (0, -1), (1, -1), (1, 0), (1, 1)) # possible 8 landing squares
    allyColor = "w" if self.whiteToMove else "b"
    for i in range (8):
      endRow = r + kingMoves[i][0]
      endCol = c + kingMoves[i][1]
      if 0 <= endRow < 8 and 0 <= endCol <8: # on board
        endPiece = self.board[endRow][endCol]
        if endPiece[0] != allyColor: # not an ally piece (empty/enemy)
          moves.append(Move((r, c), (endRow, endCol), self.board))

  '''
  Generate all valid castle moves for the king at (r, c) and add them to the list of moves
  '''
  def getCastleMoves(self, r, c, moves):
    if self.squareUnderAttack(r, c):
      return # can't castle when in check
    if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
      self.getKingsideCastlemoves(r, c, moves)
    if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
      self.getQueensideCastleMoves(r, c, moves)

    
  def getKingsideCastlemoves(self, r, c, moves):
    if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
      if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
        moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove = True))

  def getQueensideCastleMoves(self, r, c, moves):
    if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
      if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
        moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove = True))



class CastleRights():
  def __init__(self, wks, bks, wqs, bqs):
    self.wks = wks
    self.bks = bks
    self.wqs = wqs
    self.bqs = bqs


class Move():
  # maps keys to values
  # key : value
  ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                 "5": 3, "6": 2, "7": 1, "8": 0}
  rowsToRanks = {v: k for k, v in ranksToRows.items()}
  filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, 
                 "e": 4, "f": 5, "g": 6, "h": 7}
  colsToFiles = {v: k for k, v in filesToCols.items()}

  def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
    self.startRow = startSq[0]
    self.startCol = startSq[1]
    self.endRow = endSq[0]
    self.endCol = endSq[1]
    self.pieceMoved = board[self.startRow][self.startCol]
    self.pieceCaptured = board[self.endRow][self.endCol]
    # pawn promotion
    self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
    # enpassant
    self.isEnpassantMove = isEnpassantMove
    if self.isEnpassantMove:
      self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
    # castle move
    self.isCastleMove = isCastleMove

    self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

  '''
  Overriding the equals method
  '''
  def __eq__(self, other):
    if isinstance(other, Move):
      return self.moveID == other.moveID
    return False

  def getChessNotation(self):
    # you can add to make this like real chess notation
    return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

  def getRankFile(self, r, c):
    return self.colsToFiles[c] + self.rowsToRanks[r]
  
  




