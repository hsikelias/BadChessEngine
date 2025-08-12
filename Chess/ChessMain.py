"""
This is the main driver file, responsible for handling user input and displaying the real time GameState
"""

import pygame as p
import os
from Chess import ChessEngine

# Initialize pygame mixer FIRST, before pygame.init()
p.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
p.mixer.init()
p.init() # initializing pygame

WIDTH = HEIGHT = 512 # board size
DIMENSION = 8 # dimensions of the chess board.
SQ_SIZE = HEIGHT//DIMENSION
MAX_FPS = 15
IMAGES = {}
SOUNDS = {}

def loadImages():
    """
    Loading images should be done only once, saving to memory only once. loading images every frame
    causes lag.
    Initialize a global dictionary of images. This will be called exactly only once in the main.
    """
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        # Load and scale each piece image
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def loadSounds():
    """
    Load all chess sound effects
    """
    global SOUNDS
    try:
        sound_files = {
            'move': 'move.wav',
            'check': 'check.wav',
            'checkmate': 'checkmate.wav',
            'stalemate': 'stalemate.wav',
            'castle': 'castle.wav',
            'promotion': 'promotion.wav',
            'rook_sacrifice': 'rook_sacrifice.wav',
            'enpassant': 'enpassant.wav'
        }

        for sound_name, filename in sound_files.items():
            sound_path = os.path.join("sounds", filename)
            if os.path.exists(sound_path):
                SOUNDS[sound_name] = p.mixer.Sound(sound_path)
                print(f"✓ Loaded sound: {filename}")
            else:
                print(f"⚠ Warning: {sound_path} not found")

        print(f"Loaded {len(SOUNDS)} sound files successfully!")
        return True

    except Exception as e:
        print(f"Error loading sounds: {e}")
        return False

def playMoveSound(move, gs):
    """
    Play appropriate sound for the move made
    """
    try:
        # Check game state first - IMPORTANT: Check for checkmate/stalemate BEFORE other conditions
        if gs.checkMate:
            SOUNDS.get('checkmate', p.mixer.Sound("sounds/checkmate.wav")).play()
            return  # Exit early so no other sounds play
        elif gs.staleMate:
            SOUNDS.get('stalemate', p.mixer.Sound("sounds/stalemate.wav")).play()
            return  # Exit early so no other sounds play
        elif move.isCastleMove:
            SOUNDS.get('castle', p.mixer.Sound("sounds/castle.wav")).play()
        elif move.isPawnPromotion:
            SOUNDS.get('promotion', p.mixer.Sound("sounds/promotion.wav")).play()
        elif move.pieceCaptured != '--':
            # Only play sound for rook captures
            captured_piece = move.pieceCaptured[1]  # Get piece type (R, Q, B, N, p)

            if captured_piece == 'R':  # Only rook sacrifice sound
                SOUNDS.get('rook_sacrifice', p.mixer.Sound("sounds/rook_sacrifice.wav")).play()
            else:
                # For all other captures (Queen, Bishop, Knight, Pawn), just play regular move sound
                SOUNDS.get('move', p.mixer.Sound("sounds/move.wav")).play()
        else:
            # Regular move
            SOUNDS.get('move', p.mixer.Sound("sounds/move.wav")).play()

        # Check for check AFTER the move (but not if checkmate/stalemate already played)
        if gs.inCheck and not gs.checkMate and not gs.staleMate:
            # Small delay before playing check sound so it doesn't overlap with move sound
            p.time.set_timer(p.USEREVENT + 1, 200)  # 200ms delay

    except Exception as e:
        print(f"Error playing sound: {e}")

def main():
    """
    Main drive for our code. Which will handle user input and updating the graphics
    """
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState() #created a gamestate object
    validMoves = gs.getValidMoves() # Get valid moves for current position
    moveMade = False # Flag for when a move is made

    # Load resources
    loadImages()
    sounds_loaded = loadSounds()
    if not sounds_loaded:
        print("Running without sound effects")

    running = True
    sqSelected = () # no square selected, keeps track of the last click of the user(tuple: (row, col))
    playerClicks = [] #keeps tracks of player clicks( two tuples: [(6,4)(4,4])
    checkSoundTimer = False  # Flag for delayed check sound

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Handle delayed check sound
            elif e.type == p.USEREVENT + 1:
                if sounds_loaded and 'check' in SOUNDS:
                    SOUNDS['check'].play()
                p.time.set_timer(p.USEREVENT + 1, 0)  # Cancel timer
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

            # Play sound AFTER move is made and game state is updated
            if sounds_loaded:
                # Find the last move made
                if gs.moveLog:
                    last_move = gs.moveLog[-1]
                    playMoveSound(last_move, gs)

            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()

def drawGameState(screen, gs):
    """
    Draws the squares on the board, responsible for all the graphics within a current game state
    Order definitely matters, you gotta draw the board before u draw the pieces
    """
    drawBoard(screen)  #draws squares on the board
    # adding in piece highlighting or move suggestion.(later)
    drawPieces(screen, gs.board) #draws pieces on top of the board.

def drawBoard(screen):
    """
    draw the squares on the board. top left square is always light(both from white and blacks perspective)
    """
    colors = [p.Color("#f0d5b4"), p.Color("#663817")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            #Self note: Adding up the row and column and divide it by 2.. light squares are even paired,
            # dark squares are odd paired(so u get a remainder) .
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    """
    Draws the pieces on the board, using the current gamestate.board.
    """
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #not empty squares
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == "__main__":
    main()