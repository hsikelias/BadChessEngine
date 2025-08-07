"""
This is responsible for storing all the info about the current state of a chess game. It will also be responsible
for determining the valid moves. Also keeps the move log.
"""

class GameState():
    def __init__(self):
        # Board design
        # board is a 8*8 2d list, each element of the list has 2 characters. First char
        #represents the color of the piece- 'b' or 'w. 2d Character represents the type-
        # 'K', 'Q', 'B', 'R', 'N', 'p'
        # "--" represents empty space with no piece.
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"], #back rank pieces for black pov
            ["bp","bp","bp","bp","bp","bp","bp","bp"], #black pawn rank row
            # Representing a blank space on the board?
            ["--","--","--","--","--","--","--","--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            # could js leave em blank or 0, but this makes it easier to implement some core features in the future.
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],  # white rank pieces for black pov
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],  # white pawn rank row
        ]
        
        #determines whos move it is/ the move log
        self.whiteToMove = True
        #i just realized castling and en passant exists T_T
        self.moveLog = []

    def makeMove(self, move):
        """Executes a move (without any move validation for now)"""
        # Clear the starting square
        self.board[move.startRow][move.startCol] = "--"
        # Place the moved piece on the destination square
        # FIXED: Was setting to "--" which erased the piece!
        self.board[move.endRow][move.endCol] = move.pieceMoved
        # Add to move history
        self.moveLog.append(move)
        # Switch turns
        self.whiteToMove = not self.whiteToMove

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

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        # FIXED: Was using endSq[0] for both row and col!
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # thinking of how to write my logic so i can easily implement the file notation thing.

    # ranks file notations, not pure real chess like notations.. it will just be a string of values
    def getChessNotation(self):
        # real chess notation logic is a lot harder i aint doing that
        # This gives us simple notation like "a2a4"
        return self.getRankFile(self.startRow,self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self,r,c):
        # Converts row/col to chess notation (e.g., (0,0) -> "a8")
        return self.colsToFiles[c] + self.rowsToRanks[r]