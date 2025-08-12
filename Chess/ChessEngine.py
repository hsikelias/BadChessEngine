"""
This is responsible for storing all the info about the current state of a chess game. It will also be responsible
for determining the valid moves. Also keeps the move log.
"""

class GameState():
    def __init__(self):
        # Board design - FIXED: Corrected white pawn and piece positions
        # board is a 8*8 2d list, each element of the list has 2 characters. First char
        #represents the color of the piece- 'b' or 'w. 2d Character represents the type-
        # 'K', 'Q', 'B', 'R', 'N', 'p'
        # "--" represents empty space with no piece.
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"], # Rank 8 - Black back rank
            ["bp","bp","bp","bp","bp","bp","bp","bp"], # Rank 7 - Black pawns
            ["--","--","--","--","--","--","--","--"], # Rank 6 - Empty
            ["--", "--", "--", "--", "--", "--", "--", "--"], # Rank 5 - Empty
            ["--", "--", "--", "--", "--", "--", "--", "--"], # Rank 4 - Empty
            ["--", "--", "--", "--", "--", "--", "--", "--"], # Rank 3 - Empty
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"], # Rank 2 - White pawns (FIXED!)
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"], # Rank 1 - White back rank (FIXED!)
        ]

        #determines whos move it is/ the move log
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)  # Track king positions for check detection
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False

        # Castling rights - track if castling is still legal
        self.currentCastlingRight = CastleRights(True, True, True, True)  # wks, bks, wqs, bqs
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                           self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    def makeMove(self, move):
        """Executes a move (now with validation!)"""
        # Clear the starting square
        self.board[move.startRow][move.startCol] = "--"
        # Place the moved piece on the destination square
        self.board[move.endRow][move.endCol] = move.pieceMoved
        # Add to move history
        self.moveLog.append(move)
        # Switch turns
        self.whiteToMove = not self.whiteToMove

        # Update king location if king moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn promotion - automatically promote to queen
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'  # Keep color, make it queen

        # Castle move - move the rook too
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # King side castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]  # Move rook
                self.board[move.endRow][move.endCol+1] = '--'  # Clear old rook position
            else:  # Queen side castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]  # Move rook
                self.board[move.endRow][move.endCol-2] = '--'  # Clear old rook position

        # Update castling rights when king or rooks move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                               self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    def undoMove(self):
        """Undo the last move made"""
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            # Update king position if king was moved
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            # Undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # King side
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:  # Queen side
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'

            # Restore castling rights
            self.castleRightsLog.pop()
            self.currentCastlingRight = self.castleRightsLog[-1]

            self.checkMate = False
            self.staleMate = False

    def updateCastleRights(self, move):
        """Update castling rights based on the move made"""
        if move.pieceMoved == 'wK':  # White king moved
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':  # Black king moved
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':  # White rook moved
            if move.startRow == 7:
                if move.startCol == 0:  # Queen side rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # King side rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':  # Black rook moved
            if move.startRow == 0:
                if move.startCol == 0:  # Queen side rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # King side rook
                    self.currentCastlingRight.bks = False

        # If rook is captured, also lose castling rights
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

    def getValidMoves(self):
        """Get all valid moves for the current player (removes moves that leave king in check)"""
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.inCheck:
            if len(self.checks) == 1:  # Only 1 check, block or move king
                moves = self.getAllPossibleMoves()
                # To block check: move piece into check direction
                check = self.checks[0]  # Check info
                checkRow = check[0]
                checkCol = check[1]
                pieceGivingCheck = self.board[checkRow][checkCol]  # Enemy piece giving check
                validSquares = []  # Squares that pieces can move to

                # If knight, must capture knight or move king (knight checks can't be blocked)
                if pieceGivingCheck[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)  # check[2] and check[3] are check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:  # Once you get to piece giving check
                            break

                # Get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # Go through backwards when removing from a list as iterating
                    if moves[i].pieceMoved[1] != 'K':  # Move doesn't move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:  # Move doesn't block check or capture piece
                            moves.remove(moves[i])
            else:  # Double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # Not in check so all moves are fine
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:  # Either checkmate or stalemate
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves

    def getAllPossibleMoves(self):
        """Get all possible moves without considering check"""
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0] # Get piece color ('w' or 'b')
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1] # Get piece type
                    # Call appropriate function based on piece type
                    if piece == 'p':
                        self.getPawnMoves(r, c, moves)
                    elif piece == 'R':
                        self.getRookMoves(r, c, moves)
                    elif piece == 'N':
                        self.getKnightMoves(r, c, moves)
                    elif piece == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif piece == 'Q':
                        self.getQueenMoves(r, c, moves)
                    elif piece == 'K':
                        self.getKingMoves(r, c, moves)
        return moves

    def checkForPinsAndChecks(self):
        """Returns if player is in check, list of pins, and list of checks"""
        pins = []  # Squares where allied pieces are pinned and direction of pin
        checks = []  # Squares where enemy is applying check
        inCheck = False

        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        # Check outward from king for pins and checks
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # Reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # 2nd allied piece, so no pin or check in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 possibilities here in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():  # No piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # Piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # Enemy piece not applying check
                            break
                else:
                    break  # Off board

        # Check for knight checks
        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':  # Enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))

        return inCheck, pins, checks

    def getPawnMoves(self, r, c, moves):
        """Generate all valid pawn moves from position (r, c)"""
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove: # White pawn moves
            # One square forward
            if self.board[r-1][c] == "--": # Check if square is empty
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    # Two squares forward from starting position
                    if r == 6 and self.board[r-2][c] == "--": # White pawns start at rank 6 (index)
                        moves.append(Move((r, c), (r-2, c), self.board))

            # Diagonal captures
            if c - 1 >= 0: # Capture left
                if not piecePinned or pinDirection == (-1, -1):
                    if self.board[r-1][c-1][0] == 'b': # Enemy piece
                        moves.append(Move((r, c), (r-1, c-1), self.board))
            if c + 1 <= 7: # Capture right
                if not piecePinned or pinDirection == (-1, 1):
                    if self.board[r-1][c+1][0] == 'b': # Enemy piece
                        moves.append(Move((r, c), (r-1, c+1), self.board))

        else: # Black pawn moves
            # One square forward
            if self.board[r+1][c] == "--": # Check if square is empty
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                    # Two squares forward from starting position
                    if r == 1 and self.board[r+2][c] == "--": # Black pawns start at rank 1 (index)
                        moves.append(Move((r, c), (r+2, c), self.board))

            # Diagonal captures
            if c - 1 >= 0: # Capture left
                if not piecePinned or pinDirection == (1, -1):
                    if self.board[r+1][c-1][0] == 'w': # Enemy piece
                        moves.append(Move((r, c), (r+1, c-1), self.board))
            if c + 1 <= 7: # Capture right
                if not piecePinned or pinDirection == (1, 1):
                    if self.board[r+1][c+1][0] == 'w': # Enemy piece
                        moves.append(Move((r, c), (r+1, c+1), self.board))

    def getRookMoves(self, r, c, moves):
        """Generate all valid rook moves (horizontal and vertical)"""
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': # Can't remove queen from pin on rook moves, only remove rook
                    self.pins.remove(self.pins[i])
                break

        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)] # Up, left, down, right
        enemy_color = "b" if self.whiteToMove else "w"

        for d in directions:
            if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                for i in range(1, 8): # Rook can move up to 7 squares in any direction
                    end_row = r + d[0] * i
                    end_col = c + d[1] * i

                    if 0 <= end_row < 8 and 0 <= end_col < 8: # On board
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--": # Empty square
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color: # Enemy piece
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break # Can't jump over pieces
                        else: # Friendly piece
                            break
                    else: # Off board
                        break

    def getKnightMoves(self, r, c, moves):
        """Generate all valid knight moves (L-shapes)"""
        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        ally_color = "w" if self.whiteToMove else "b"

        if not piecePinned: # Knight can't move when pinned
            for m in knight_moves:
                end_row = r + m[0]
                end_col = c + m[1]
                if 0 <= end_row < 8 and 0 <= end_col < 8: # On board
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color: # Not a friendly piece (empty or enemy)
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    def getBishopMoves(self, r, c, moves):
        """Generate all valid bishop moves (diagonal)"""
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] # Four diagonals
        enemy_color = "b" if self.whiteToMove else "w"

        for d in directions:
            if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                for i in range(1, 8): # Bishop can move up to 7 squares diagonally
                    end_row = r + d[0] * i
                    end_col = c + d[1] * i

                    if 0 <= end_row < 8 and 0 <= end_col < 8: # On board
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--": # Empty square
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color: # Enemy piece
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break # Can't jump over pieces
                        else: # Friendly piece
                            break
                    else: # Off board
                        break

    def getQueenMoves(self, r, c, moves):
        """Generate all valid queen moves (combines rook + bishop)"""
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        """Generates all valid king moves """
        king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        ally_color = "w" if self.whiteToMove else "b"

        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8: # On board
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color: # Not a friendly piece
                    # Place king on end square and check for checks
                    if ally_color == 'w':
                        self.whiteKingLocation = (end_row, end_col)
                    else:
                        self.blackKingLocation = (end_row, end_col)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    # Place king back on original location
                    if ally_color == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

        # Castling moves
        self.getCastleMoves(r, c, moves)

    def getCastleMoves(self, r, c, moves):
        """Generate all valid castling moves for the king at (r, c)"""
        if self.inCheck:
            return  # Cannot castle while in check

        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        """Check for kingside castle moves"""
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        """Check for queenside castle moves"""
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))

    def squareUnderAttack(self, r, c):
        """Determine if enemy can attack square r, c"""
        self.whiteToMove = not self.whiteToMove  # Switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # Switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # Square is under attack
                return True
        return False

class CastleRights():
    """Class to track castling rights"""
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks  # White king side
        self.bks = bks  # Black king side
        self.wqs = wqs  # White queen side
        self.bqs = bqs  # Black queen side

class Move():
    # maps keys to values
    # key : value
    # These dictionaries convert between chess notation and array indices
    ranksToRows = {"1":7,"2":6, "3":5, "4":4,
                   "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()} #reversing the dictionary
    filesToCols = {"a":0, "b":1,"c":2,"d":3,
                   "e":4, "f":5,"g":6,"h":7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # Pawn promotion - check if pawn reached the end
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)

        # Castle move
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    # ranks file notations, not pure real chess like notations.. it will just be a string of values
    def getChessNotation(self):
        # This gives us simple notation like "a2a4"
        return self.getRankFile(self.startRow,self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self,r,c):
        # Converts row/col to chess notation (e.g., (0,0) -> "a8")
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def __eq__(self, other):
        """Compare two moves for equality"""
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False