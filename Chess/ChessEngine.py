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

        self.whiteTOMove = True    
        #i just realized castling and en passant exists T_T
        self.moveLog = []