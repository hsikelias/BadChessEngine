"""
This is the main driver file, responsible for handling user input and displaying the real time GameState
"""

import pygame as p
from Chess import ChessEngine

p.init() # initiazling pygame
WIDTH = HEIGHT = 512 # board size
DIMENSION = 8 #dimensions of the chess board.
SQ_SIZE = HEIGHT//DIMENSION
MAX_FPS = 15
IMAGES = {}

'''
Loading images should be done only once, saving to memory only once. loading images every frame
causes lag. 
Initialize a global dictionary of images. This will be called exactly only once in the main.
'''
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ',]
    for piece in pieces:
        # Load and scale each piece image
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

'''
Main drive for our code. Which will handle user input and updating the graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState() #created a gamestate object
    validMoves = gs.getValidMoves() # Get valid moves for current position
    moveMade = False # Flag for when a move is made
    loadImages()
    running = True
    sqSelected = () # no square selected, keeps track of the last click of the user(tuple: (row, col))
    playerClicks = [] #keeps tracks of player clicks( two tuples: [(6,4)(4,4])

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse clicks
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() # the x,y location fo the mouse.
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE

                if sqSelected == (row, col): #user clicked same square twice
                    sqSelected = () # basically deselects
                    playerClicks = [] #clear player clicks
                else:
                    sqSelected = (row,col)
                    playerClicks.append(sqSelected) #appends for both 1st and 2nd click

                if len(playerClicks) == 2: #after 2nd click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation()) # Print move in chess notation
                    
                    # Check if move is valid before making it
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            sqSelected = () #reset user selection
                            playerClicks = [] # Clear clicks after move
                            break
                    
                    if not moveMade:
                        playerClicks = [sqSelected] # Keep the second click as first click for next attempt
            
            # Key presses
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # Press 'z' to undo move
                    gs.undoMove()
                    moveMade = True

        # If a move was made, recalculate valid moves
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Draws the squares on the board, responsible for all the graphics within a current game state
Order definetly matters, you gotta draw the board before u draw the pieces
'''
def drawGameState(screen, gs):
    drawBoard(screen)  #draws squares on the board
    # adding in piece highlighting or move suggestion.(later)
    drawPieces(screen, gs.board) #draws pieces on top of the board.

'''
draw the squares on the board. top left square is always light(both from white and blacks perspective)
'''
def drawBoard(screen):
    colors = [p.Color("#f0d5b4"), p.Color("#663817")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            #Self note: Adding up the row and column and divide it by 2.. light squares are even paired,
            # dark squares are odd paired(so u get a remainder) .
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draws the pieces on the board, using the current gamestate.board.
'''
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #not empty squares
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == "__main__":
    main()