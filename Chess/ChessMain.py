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
# adaptable to let the user chose the chess set they want to use.
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ',]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE)) #scaling images

    # We can access an image by saying 'IMAGES['wp']'   


'''
Main drive for our code. Which will handle user input and upadting the graphics
'''

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white")) # not necessary cus we gon add other color later
    gs = ChessEngine.GameState() #created a gamestate object, this basically intializes the gamestate constructor in chessengine
    # and that we can access the board by just saying gs.board
    loadImages()
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
        drawGameState(screen,gs)
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
     colors = [p.Color("#f0d5b4"),p.Color("#663817")]
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
