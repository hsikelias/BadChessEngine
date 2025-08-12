# Chess Engine in Python(Still under active development)

A fully functional chess game built with Python and Pygame, featuring complete chess rules implementation, sound effects, and a standard graphical interface.

## Features

- ✅ Complete chess rule implementation
- ✅ Legal move validation and check detection
- ✅ Checkmate and stalemate detection
- ✅ Castling (kingside and queenside)
- ✅ Pawn promotion (auto-promotes to queen)
- ✅ Pin detection (pieces protecting the king)
- ✅ Move undo functionality (press 'Z')
- ✅ Sound effects for different move types
- ✅ Clean graphical interface with piece images

## Screenshots

## Installation

### Prerequisites
- Python 3.7+
- Pygame

### Setup
1. Clone this repository:
```bash
git clone https://github.com/hsikelias/BadChessEngine.git
cd BadChessEngine
```

2. Install Pygame:
```bash
pip install pygame
```

3. Ensure you have the required assets:
   - `images/` folder with chess piece PNG files (wp.png, wR.png, etc.)
   - `sounds/` folder with WAV sound files

## How to Play

1. Run the game:
```bash
python ChessMain.py
```

2. **Making Moves:**
   - Click on a piece to select it
   - Click on a destination square to move
   - Click the same square twice to deselect

3. **Controls:**
   - **Mouse**: Select and move pieces
   - **Z Key**: Undo last move

## Project Structure

```
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
```

## Sound Effects

The game includes audio feedback for:
- Regular moves
- Rook captures (special sacrifice sound ft.GothamChess)
- Check warnings
- Checkmate/stalemate notifications
- Castling moves
- Pawn promotions

## Technical Implementation

- **Game Engine**: Custom chess logic with advanced features like pin detection
- **Graphics**: Pygame-based GUI with 512x512 pixel board
- **Architecture**: Clean separation between game logic and presentation
- **Move Validation**: Comprehensive legal move checking prevents illegal moves
- **Chess Notation**: Supports standard algebraic notation output

## Future Enhancements

- [ ] AI opponent implementation
- [ ] Move highlighting and suggestions
- [ ] En passant capture
- [ ] Game save/load functionality
- [ ] Online multiplayer support
- [ ] Opening book integration
- [ ] Move timer/clock

## Contributing

Feel free to fork this project and submit pull requests for improvements!

## License

This project is open source and available under the [MIT License](LICENSE).

---

*Built with Python and Pygame* 🐍♟️
