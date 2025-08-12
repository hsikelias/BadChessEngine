# Chess Game in Python: 

A fully functional chess game built with Python and Pygame, featuring complete chess rules implementation, sound effects, and standard graphical interface features.
Players have the option to choose between playing on their own or with a bot.

✅ Complete chess rule implementation
✅ Legal move validation and check detection
✅ Checkmate and stalemate detection
✅ Castling (kingside and queenside)
✅ Pawn promotion (auto-promotes to queen)
✅ Pin detection (pieces protecting the king)
✅ Move undo functionality (press 'Z')
✅ Sound effects for different move types
✅ Clean graphical interface with piece images
   Multiple Ai difficulties
   Saving game files

# Screenshots:


# Installation: 
1. Prerequisites:
     Python 3.7+
     Pygame
2. Setup: 
   git clone https://github.com/hsikelias/BadChessEngine.git
   cd BadChessEngine
3. Pygame:
    win: pip install pygame
4. Make sure you have the assets for images and audio from this repository


# How To Play: 
1. Run the game
     python ChessMain.py
2. Making Moves:
     - Click on a piece to select it
     - Click on the square u want the piece to move
     - Click the same square twice to deselect the piece
3. Controls:
     - Right mouse button to select and move pieces
     - Z to undo moves

# Project Structure: 

Chess/
├── ChessEngine.py      # Game logic and chess rules
├── ChessMain.py        # GUI and user interface  
├── __init__.py         # Package initializer
├── images/             # Chess piece sprites
│   ├── wp.png         # White pawn
│   ├── wR.png         # White rook
│   └── ...            # Other pieces
└── sounds/             # Sound effects
    ├── move.wav
    ├── checkmate.wav
    ├── rook_sacrifice.wav
    └── ...
   
     
# Contributing: 
Feel free to fork this project and submit pull requests for improvements!


# License: 
This project is open source and available under the MIT License.





