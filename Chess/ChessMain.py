def draw_footer(self):
    """Draw bottom status bar"""
    footer_rect = p.Rect(0, WINDOW_HEIGHT - FOOTER_HEIGHT, WINDOW_WIDTH, FOOTER_HEIGHT)
    p.draw.rect(self.screen, COLORS['bg_secondary'], footer_rect)
    p.draw.line(self.screen, COLORS['border'], (0, WINDOW_HEIGHT - FOOTER_HEIGHT),
                (WINDOW_WIDTH, WINDOW_HEIGHT - FOOTER_HEIGHT))

    # Status message
    status_msg = "Ready to play"
    if self.gs.checkMate:
        status_msg = "Game Over - Checkmate!"
    elif self.gs.staleMate:
        status_msg = "Game Over - Stalemate!"
    elif self.gs.inCheck():
        status_msg = "Check!"
    elif self.last_move:
        status_msg = f"Last move: {self.last_move.getChessNotation()}"

    status_surf = self.font_small.render(status_msg, True, COLORS['text_secondary'])
    self.screen.blit(status_surf, (20, WINDOW_HEIGHT - 25))

    # Keyboard shortcuts hint
    shortcuts = "Ctrl+N: New | Ctrl+Z: Undo | Ctrl+S: Save | Ctrl+F: Flip"
    shortcuts_surf = self.font_tiny.render(shortcuts, True, COLORS['text_muted'])
    shortcuts_x = WINDOW_WIDTH - shortcuts_surf.get_width() - 20
    self.screen.blit(shortcuts_surf, (shortcuts_x, WINDOW_HEIGHT - 25))
    """
Chess.com Style Desktop Chess Game
Clean, modern UI inspired by chess.com
"""


import pygame as p
import os
import sys
import json
import time
from datetime import datetime
# Import your fixed ChessEngine
import ChessEngine

# Initialize pygame mixer FIRST
p.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
p.mixer.init()
p.init()

# Chess.com inspired dimensions
BOARD_SIZE = 640  # Clean, large board
SIDEBAR_WIDTH = 320  # Right sidebar for controls and game info
HEADER_HEIGHT = 60  # Top header bar
FOOTER_HEIGHT = 40  # Bottom status bar

WINDOW_WIDTH = BOARD_SIZE + SIDEBAR_WIDTH
WINDOW_HEIGHT = BOARD_SIZE + HEADER_HEIGHT + FOOTER_HEIGHT

DIMENSION = 8
SQ_SIZE = BOARD_SIZE // DIMENSION
MAX_FPS = 60

# Chess.com inspired color palette
COLORS = {
    # Board colors (chess.com green theme)
    'light_square': p.Color("#f0d9b4"),  # Light wood
    'dark_square': p.Color("#b58863"),  # Dark wood
    'light_highlight': p.Color("#ffff7f"),  # Yellow highlight
    'dark_highlight': p.Color("#ffdd7f"),  # Darker yellow
    'last_move_light': p.Color("#cdd26a"),  # Last move on light
    'last_move_dark': p.Color("#aaa23a"),  # Last move on dark
    'check_square': p.Color("#ff6b6b"),  # Red for check
    'valid_move': p.Color("#00aa00"),  # Green dots for valid moves
    'selected': p.Color("#ffff00"),  # Selected piece highlight

    # UI colors (chess.com style)
    'bg_primary': p.Color("#312e2b"),  # Main background (dark brown)
    'bg_secondary': p.Color("#262421"),  # Darker panels
    'bg_card': p.Color("#3c3936"),  # Card backgrounds
    'accent': p.Color("#81b64c"),  # Chess.com green accent
    'accent_hover': p.Color("#9bcc5f"),  # Lighter green hover
    'accent_active': p.Color("#6fa03f"),  # Darker green active

    # Text colors
    'text_primary': p.Color("#ffffff"),  # White text
    'text_secondary': p.Color("#b9b9b9"),  # Gray text
    'text_muted': p.Color("#8d8d8d"),  # Muted text
    'text_success': p.Color("#81b64c"),  # Success text
    'text_danger': p.Color("#ff6b6b"),  # Error/danger text

    # Border and divider colors
    'border': p.Color("#4a4744"),  # Subtle borders
    'divider': p.Color("#3c3936"),  # Section dividers
}

IMAGES = {}
SOUNDS = {}


class GameManager:
    """Manages saved games and game history"""

    def __init__(self):
        self.games_file = "chess_games.json"
        self.games = self.load_games()

    def load_games(self):
        """Load saved games from file"""
        try:
            if os.path.exists(self.games_file):
                with open(self.games_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading games: {e}")
        return []

    def save_games(self):
        """Save games to file"""
        try:
            with open(self.games_file, 'w') as f:
                json.dump(self.games, f, indent=2)
        except Exception as e:
            print(f"Error saving games: {e}")

    def add_game(self, moves, result, white_player="Human", black_player="Human"):
        """Add a new game to the collection"""
        game_data = {
            'id': len(self.games) + 1,
            'date': datetime.now().isoformat(),
            'white_player': white_player,
            'black_player': black_player,
            'moves': moves,
            'result': result,
            'move_count': len(moves),
            'duration': "Unknown"  # Could track game duration
        }

        self.games.insert(0, game_data)  # Add to beginning
        if len(self.games) > 100:  # Keep only last 100 games
            self.games = self.games[:100]
        self.save_games()

    def get_games(self):
        """Get list of games"""
        return self.games

    def delete_game(self, game_id):
        """Delete a game by ID"""
        self.games = [g for g in self.games if g['id'] != game_id]
        self.save_games()


class ChessComGame:
    """Chess.com style chess game"""

    def __init__(self):
        self.screen = p.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        p.display.set_caption("Chess Desktop - Play Like a Pro")
        self.clock = p.time.Clock()

        # Game state
        self.gs = ChessEngine.GameState()
        self.valid_moves = self.gs.getValidMoves()
        self.move_made = False

        # UI state
        self.sq_selected = ()
        self.player_clicks = []
        self.last_move = None
        self.show_valid_moves = True  # Chess.com style move hints
        self.board_flipped = False  # Board orientation

        # Game management
        self.game_manager = GameManager()
        self.game_list_scroll = 0
        self.selected_game_id = None
        self.hovered_game_index = -1

        # Animation state
        self.animation_time = 0
        self.animated_squares = set()

        # Load resources
        self.load_images()
        self.load_sounds()

        # Fonts (chess.com uses clean sans-serif)
        self.font_large = p.font.Font(None, 28)
        self.font_medium = p.font.Font(None, 22)
        self.font_small = p.font.Font(None, 18)
        self.font_tiny = p.font.Font(None, 16)
        self.font_header = p.font.Font(None, 24)

        # UI elements
        self.buttons = self.create_buttons()

        # Game start time
        self.game_start_time = time.time()

    def load_images(self):
        """Load piece images with chess.com style fallbacks"""
        pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']

        for piece in pieces:
            try:
                img_path = os.path.join("images", f"{piece}.png")
                if os.path.exists(img_path):
                    IMAGES[piece] = p.transform.scale(p.image.load(img_path), (SQ_SIZE, SQ_SIZE))
                else:
                    self.create_chess_com_piece(piece)
            except Exception as e:
                self.create_chess_com_piece(piece)

    def create_chess_com_piece(self, piece):
        """Create chess.com style piece graphics"""
        surf = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)

        # Chess.com style colors
        if piece[0] == 'w':
            main_color = p.Color("#ffffff")
            border_color = p.Color("#cccccc")
        else:
            main_color = p.Color("#2c2c2c")
            border_color = p.Color("#1a1a1a")

        center = SQ_SIZE // 2

        # Draw piece based on type with chess.com styling
        if piece[1] == 'p':  # Pawn
            # Simple pawn shape
            points = [
                (center, center - 15),
                (center - 8, center + 15),
                (center + 8, center + 15)
            ]
            p.draw.polygon(surf, main_color, points)
            p.draw.polygon(surf, border_color, points, 2)
            p.draw.circle(surf, main_color, (center, center - 10), 8)
            p.draw.circle(surf, border_color, (center, center - 10), 8, 2)

        elif piece[1] == 'K':  # King
            # Crown shape for king
            p.draw.circle(surf, main_color, (center, center), 18)
            p.draw.circle(surf, border_color, (center, center), 18, 3)
            # Crown points
            crown_points = [
                (center - 12, center - 12),
                (center - 6, center - 20),
                (center, center - 15),
                (center + 6, center - 20),
                (center + 12, center - 12),
            ]
            p.draw.polygon(surf, main_color, crown_points)
            p.draw.polygon(surf, border_color, crown_points, 2)
            # Cross on top
            p.draw.line(surf, border_color, (center, center - 25), (center, center - 15), 2)
            p.draw.line(surf, border_color, (center - 3, center - 22), (center + 3, center - 22), 2)

        elif piece[1] == 'Q':  # Queen
            p.draw.circle(surf, main_color, (center, center), 16)
            p.draw.circle(surf, border_color, (center, center), 16, 3)
            # Crown with multiple points
            for i in range(5):
                angle = (i * 72 - 90) * 3.14159 / 180
                x = center + int(12 * p.math.cos(angle))
                y = center - 5 + int(12 * p.math.sin(angle))
                p.draw.circle(surf, main_color, (x, y), 3)

        elif piece[1] == 'R':  # Rook
            # Castle tower shape
            rect = p.Rect(center - 12, center - 8, 24, 16)
            p.draw.rect(surf, main_color, rect)
            p.draw.rect(surf, border_color, rect, 2)
            # Battlements
            for i in range(3):
                x = center - 8 + i * 8
                p.draw.rect(surf, main_color, (x, center - 15, 4, 7))
                p.draw.rect(surf, border_color, (x, center - 15, 4, 7), 1)

        elif piece[1] == 'B':  # Bishop
            # Bishop hat shape
            p.draw.circle(surf, main_color, (center, center), 14)
            p.draw.circle(surf, border_color, (center, center), 14, 2)
            # Hat point
            points = [
                (center - 8, center - 8),
                (center, center - 18),
                (center + 8, center - 8)
            ]
            p.draw.polygon(surf, main_color, points)
            p.draw.polygon(surf, border_color, points, 2)
            p.draw.circle(surf, border_color, (center, center - 15), 2)

        elif piece[1] == 'N':  # Knight
            # Simplified horse head
            p.draw.circle(surf, main_color, (center, center), 15)
            p.draw.circle(surf, border_color, (center, center), 15, 2)
            # Ears
            p.draw.circle(surf, main_color, (center - 8, center - 8), 4)
            p.draw.circle(surf, main_color, (center + 8, center - 8), 4)

        # Add piece letter for clarity
        font = p.font.Font(None, 24)
        text = font.render(piece[1], True, border_color)
        text_rect = text.get_rect(center=(center, center + 5))
        surf.blit(text, text_rect)

        IMAGES[piece] = surf

    def load_sounds(self):
        """Load chess sound effects"""
        sound_files = {
            'move': 'move.wav',
            'capture': 'capture.wav',
            'check': 'check.wav',
            'checkmate': 'checkmate.wav',
            'castle': 'castle.wav',
            'promotion': 'promotion.wav',
            'game_start': 'game_start.wav',
            'game_end': 'game_end.wav'
        }

        for sound_name, filename in sound_files.items():
            try:
                sound_path = os.path.join("sounds", filename)
                if os.path.exists(sound_path):
                    SOUNDS[sound_name] = p.mixer.Sound(sound_path)
            except Exception as e:
                pass  # Silent fallback

    def create_buttons(self):
        """Create simplified buttons"""
        buttons = []

        # Main action buttons (top of sidebar)
        button_x = BOARD_SIZE + 20
        button_y = HEADER_HEIGHT + 20
        button_width = SIDEBAR_WIDTH - 40
        button_height = 40

        main_buttons = [
            ("🆕 New Game", self.new_game, COLORS['accent']),
            ("↶ Undo Move", self.undo_move, COLORS['bg_card']),
            ("💾 Save Game", self.save_current_game, COLORS['bg_card']),
            ("🔄 Flip Board", self.flip_board, COLORS['bg_card']),
        ]

        for text, callback, color in main_buttons:
            buttons.append({
                'rect': p.Rect(button_x, button_y, button_width, button_height),
                'text': text,
                'callback': callback,
                'color': color,
                'hover_color': COLORS['accent_hover'] if color == COLORS['accent'] else COLORS['border'],
                'hovered': False
            })
            button_y += button_height + 10

        # Utility button
        util_y = button_y + 20
        buttons.append({
            'rect': p.Rect(button_x, util_y, button_width, 35),
            'text': "🗑️ Clear All Games",
            'callback': self.clear_games,
            'color': COLORS['bg_secondary'],
            'hover_color': COLORS['border'],
            'hovered': False
        })

        self.buttons = buttons
        return buttons

    def handle_events(self):
        """Handle pygame events"""
        for event in p.event.get():
            if event.type == p.QUIT:
                return False

            elif event.type == p.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_mouse_click(event.pos)
                elif event.button == 4:  # Scroll up
                    self.game_list_scroll = max(0, self.game_list_scroll - 3)
                elif event.button == 5:  # Scroll down
                    self.game_list_scroll += 3

            elif event.type == p.MOUSEMOTION:
                self.handle_mouse_motion(event.pos)

            elif event.type == p.KEYDOWN:
                if event.key == p.K_z and p.key.get_pressed()[p.K_LCTRL]:
                    self.undo_move()
                elif event.key == p.K_n and p.key.get_pressed()[p.K_LCTRL]:
                    self.new_game()
                elif event.key == p.K_s and p.key.get_pressed()[p.K_LCTRL]:
                    self.save_current_game()
                elif event.key == p.K_f and p.key.get_pressed()[p.K_LCTRL]:
                    self.flip_board()

        return True

    def handle_mouse_click(self, pos):
        """Handle mouse clicks with chess.com style interactions"""
        # Check button clicks first
        for button in self.buttons:
            if button['rect'].collidepoint(pos):
                button['callback']()
                return

        # Check game list clicks
        if self.handle_game_list_click(pos):
            return

        # Handle board clicks (only within board area)
        board_rect = p.Rect(0, HEADER_HEIGHT, BOARD_SIZE, BOARD_SIZE)
        if board_rect.collidepoint(pos):
            col = pos[0] // SQ_SIZE
            row = (pos[1] - HEADER_HEIGHT) // SQ_SIZE

            # Flip coordinates if board is flipped
            if self.board_flipped:
                row = 7 - row
                col = 7 - col

            if 0 <= row < 8 and 0 <= col < 8:  # Valid board position
                if self.sq_selected == (row, col):
                    # Clicking same square deselects
                    self.sq_selected = ()
                    self.player_clicks = []
                else:
                    self.sq_selected = (row, col)
                    self.player_clicks.append(self.sq_selected)

                if len(self.player_clicks) == 2:
                    self.attempt_move()

    def handle_game_list_click(self, pos):
        """Handle clicks in game list"""
        list_area = self.get_game_list_area()
        if not list_area.collidepoint(pos):
            return False

        # Calculate which game was clicked
        relative_y = pos[1] - list_area.top
        if relative_y < 30:  # Header area
            return True

        item_height = 60
        game_index = ((relative_y - 30) // item_height) + self.game_list_scroll

        games = self.game_manager.get_games()
        if 0 <= game_index < len(games):
            game = games[game_index]
            self.selected_game_id = game['id']
            # Load the selected game
            self.load_game(game)
            print(f"Loaded game from {game['date']}")

        return True

    def handle_mouse_motion(self, pos):
        """Handle mouse motion for hover effects"""
        for button in self.buttons:
            button['hovered'] = button['rect'].collidepoint(pos)

        # Add hover effect for game list items
        self.hovered_game_index = -1
        list_area = self.get_game_list_area()
        if list_area.collidepoint(pos):
            relative_y = pos[1] - list_area.top
            if relative_y > 45:  # Below header and instruction
                item_height = 50
                game_index = ((relative_y - 45) // item_height) + self.game_list_scroll
                games = self.game_manager.get_games()
                if 0 <= game_index < len(games):
                    self.hovered_game_index = game_index

    def attempt_move(self):
        """Attempt to make a chess move"""
        move = ChessEngine.Move(self.player_clicks[0], self.player_clicks[1], self.gs.board)

        for valid_move in self.valid_moves:
            if move == valid_move:
                self.make_move(valid_move)
                return

        # Invalid move - keep second click as new selection
        self.player_clicks = [self.sq_selected]

    def make_move(self, move):
        """Execute a chess move"""
        self.gs.makeMove(move)
        self.last_move = move
        self.move_made = True
        self.sq_selected = ()
        self.player_clicks = []

        # Add animation effect
        self.animated_squares.add((move.endRow, move.endCol))
        self.animation_time = time.time()

        self.play_sound(move)

    def play_sound(self, move):
        """Play move sound effect"""
        if self.gs.checkMate:
            sound = SOUNDS.get('checkmate') or SOUNDS.get('game_end')
        elif self.gs.inCheck():
            sound = SOUNDS.get('check')
        elif move.isCastleMove:
            sound = SOUNDS.get('castle')
        elif move.isPawnPromotion:
            sound = SOUNDS.get('promotion')
        elif move.pieceCaptured != '--':
            sound = SOUNDS.get('capture')
        else:
            sound = SOUNDS.get('move')

        if sound:
            sound.play()

    def new_game(self):
        """Start a new game"""
        # Auto-save current game if it has moves
        if len(self.gs.moveLog) > 0:
            result = self.get_game_result()
            moves = [move.getChessNotation() for move in self.gs.moveLog]
            self.game_manager.add_game(moves, result)

        # Reset game state
        self.gs = ChessEngine.GameState()
        self.valid_moves = self.gs.getValidMoves()
        self.sq_selected = ()
        self.player_clicks = []
        self.last_move = None
        self.move_made = True
        self.selected_game_id = None
        self.game_start_time = time.time()

        # Play new game sound
        if SOUNDS.get('game_start'):
            SOUNDS['game_start'].play()

    def undo_move(self):
        """Undo the last move"""
        if self.gs.moveLog:
            self.gs.undoMove()
            self.move_made = True
            self.sq_selected = ()
            self.player_clicks = []
            self.last_move = self.gs.moveLog[-1] if self.gs.moveLog else None

    def flip_board(self):
        """Flip the board orientation"""
        self.board_flipped = not self.board_flipped
        # Clear selection when flipping
        self.sq_selected = ()
        self.player_clicks = []
        print(f"🔄 Board flipped - {'Black' if self.board_flipped else 'White'} perspective")
        """Save the current game manually"""
        if len(self.gs.moveLog) > 0:
            result = self.get_game_result()
            moves = [move.getChessNotation() for move in self.gs.moveLog]
            self.game_manager.add_game(moves, result)
            print("✓ Game saved successfully!")
        else:
            print("⚠ No moves to save")

    def load_game(self, game_data):
        """Load a saved game"""
        try:
            # Reset to new game state
            self.gs = ChessEngine.GameState()

            # Replay all moves from the saved game
            for move_notation in game_data['moves']:
                # Find the corresponding move object
                valid_moves = self.gs.getValidMoves()
                move_found = False

                for move in valid_moves:
                    if move.getChessNotation() == move_notation:
                        self.gs.makeMove(move)
                        self.last_move = move
                        move_found = True
                        break

                if not move_found:
                    print(f"⚠ Could not replay move: {move_notation}")
                    break

            # Update game state
            self.valid_moves = self.gs.getValidMoves()
            self.sq_selected = ()
            self.player_clicks = []
            self.move_made = True

            # Update game start time (approximate)
            self.game_start_time = time.time()

            print(f"✓ Loaded game with {len(game_data['moves'])} moves")

        except Exception as e:
            print(f"✗ Failed to load game: {e}")
            # Reset to new game if loading fails
            self.new_game()

    def save_current_game(self):
        """Export current game as PGN"""
        if not self.gs.moveLog:
            print("⚠ No game to export")
            return

        # Create PGN content
        pgn_lines = [
            f'[Date "{datetime.now().strftime("%Y.%m.%d")}"]',
            '[White "Human"]',
            '[Black "Human"]',
            f'[Result "{self.get_game_result()}"]',
            '[TimeControl "-"]',
            '',
        ]

        # Add moves
        move_text = ""
        for i, move in enumerate(self.gs.moveLog):
            if i % 2 == 0:
                move_text += f"{i // 2 + 1}. {move.getChessNotation()} "
            else:
                move_text += f"{move.getChessNotation()} "

        move_text += self.get_game_result()
        pgn_lines.append(move_text)

        # Save to file
        filename = f"chess_game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn"
        try:
            with open(filename, 'w') as f:
                f.write('\n'.join(pgn_lines))
            print(f"✓ Game exported to {filename}")
        except Exception as e:
            print(f"✗ Export failed: {e}")

    def show_settings(self):
        """Show settings (placeholder)"""
        print("⚙️ Settings panel - coming soon!")

    def clear_games(self):
        """Clear all saved games"""
        self.game_manager.games = []
        self.game_manager.save_games()
        self.selected_game_id = None
        print("🗑️ All games cleared")

    def get_game_result(self):
        """Get current game result in PGN format"""
        if self.gs.checkMate:
            return "0-1" if self.gs.whiteToMove else "1-0"
        elif self.gs.staleMate:
            return "1/2-1/2"
        else:
            return "*"

    def get_game_list_area(self):
        """Get the rectangle area for game list"""
        x = BOARD_SIZE + 20
        y = HEADER_HEIGHT + 300  # Below buttons
        w = SIDEBAR_WIDTH - 40
        h = WINDOW_HEIGHT - y - FOOTER_HEIGHT - 20
        return p.Rect(x, y, w, h)

    def draw_everything(self):
        """Draw the complete chess.com style interface"""
        # Clear screen with main background
        self.screen.fill(COLORS['bg_primary'])

        # Draw components
        self.draw_header()
        self.draw_board()
        self.draw_pieces()
        self.draw_highlights()
        self.draw_sidebar()
        self.draw_footer()

        # Clean up old animations
        current_time = time.time()
        if current_time - self.animation_time > 0.5:
            self.animated_squares.clear()

    def draw_header(self):
        """Draw top header bar"""
        header_rect = p.Rect(0, 0, WINDOW_WIDTH, HEADER_HEIGHT)
        p.draw.rect(self.screen, COLORS['bg_secondary'], header_rect)
        p.draw.line(self.screen, COLORS['border'], (0, HEADER_HEIGHT - 1), (WINDOW_WIDTH, HEADER_HEIGHT - 1))

        # Title
        title = self.font_header.render("♔ Chess Desktop", True, COLORS['text_primary'])
        self.screen.blit(title, (20, 20))

        # Game status in header
        status = "White to move" if self.gs.whiteToMove else "Black to move"
        if self.gs.checkMate:
            winner = "Black" if self.gs.whiteToMove else "White"
            status = f"Checkmate! {winner} wins! 🏆"
        elif self.gs.staleMate:
            status = "Stalemate - Draw! 🤝"
        elif self.gs.inCheck():
            status += " - Check! ⚠️"

        status_text = self.font_small.render(status, True, COLORS['text_secondary'])
        status_x = BOARD_SIZE - status_text.get_width() - 20
        self.screen.blit(status_text, (status_x, 25))

    def draw_board(self):
        """Draw chess board with chess.com styling"""
        board_y = HEADER_HEIGHT

        for row in range(8):
            for col in range(8):
                # Get actual board position (handle flipping)
                display_row = 7 - row if self.board_flipped else row
                display_col = 7 - col if self.board_flipped else col

                # Determine square color
                is_light = (display_row + display_col) % 2 == 0
                base_color = COLORS['light_square'] if is_light else COLORS['dark_square']

                # Check for highlights (using actual board coordinates)
                square_pos = (row, col)

                # Last move highlight
                if (self.last_move and
                        (square_pos == (self.last_move.startRow, self.last_move.startCol) or
                         square_pos == (self.last_move.endRow, self.last_move.endCol))):
                    color = COLORS['last_move_light'] if is_light else COLORS['last_move_dark']

                # Selected square highlight
                elif self.sq_selected == square_pos:
                    color = COLORS['light_highlight'] if is_light else COLORS['dark_highlight']

                # Check highlight
                elif (self.gs.inCheck() and
                      square_pos == (self.gs.whiteKingLocation if self.gs.whiteToMove else self.gs.blackKingLocation)):
                    color = COLORS['check_square']

                else:
                    color = base_color

                # Draw square (using display coordinates for position)
                rect = p.Rect(display_col * SQ_SIZE, board_y + display_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                p.draw.rect(self.screen, color, rect)

                # Animation effect for recent moves
                if square_pos in self.animated_squares:
                    animation_alpha = max(0, 100 - int((time.time() - self.animation_time) * 200))
                    if animation_alpha > 0:
                        anim_surf = p.Surface((SQ_SIZE, SQ_SIZE))
                        anim_surf.set_alpha(animation_alpha)
                        anim_surf.fill(COLORS['accent'])
                        self.screen.blit(anim_surf, rect)

        # Draw board border
        board_rect = p.Rect(0, board_y, BOARD_SIZE, BOARD_SIZE)
        p.draw.rect(self.screen, COLORS['border'], board_rect, 2)

        # Draw coordinates (chess.com style)
        coord_font = p.font.Font(None, 20)
        for i in range(8):
            display_i = 7 - i if self.board_flipped else i

            # Files (a-h) at bottom
            file_char = chr(ord('a') + (7 - i if self.board_flipped else i))
            file_color = COLORS['text_muted']
            file_text = coord_font.render(file_char, True, file_color)
            self.screen.blit(file_text, (display_i * SQ_SIZE + SQ_SIZE - 15, board_y + BOARD_SIZE - 18))

            # Ranks (1-8) on left
            rank_char = str(i + 1 if self.board_flipped else 8 - i)
            rank_text = coord_font.render(rank_char, True, file_color)
            self.screen.blit(rank_text, (5, board_y + display_i * SQ_SIZE + 5))

    def draw_pieces(self):
        """Draw chess pieces"""
        board_y = HEADER_HEIGHT

        for row in range(8):
            for col in range(8):
                piece = self.gs.board[row][col]
                if piece != "--":
                    # Handle board flipping for piece display
                    display_row = 7 - row if self.board_flipped else row
                    display_col = 7 - col if self.board_flipped else col

                    piece_rect = p.Rect(display_col * SQ_SIZE, board_y + display_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                    self.screen.blit(IMAGES[piece], piece_rect)

    def draw_highlights(self):
        """Draw move hints and highlights (chess.com style)"""
        if not self.show_valid_moves or not self.sq_selected:
            return

        board_y = HEADER_HEIGHT

        # Show valid moves as dots/circles
        for move in self.valid_moves:
            if (move.startRow == self.sq_selected[0] and
                    move.startCol == self.sq_selected[1]):

                # Handle board flipping for move highlights
                display_row = 7 - move.endRow if self.board_flipped else move.endRow
                display_col = 7 - move.endCol if self.board_flipped else move.endCol

                center_x = display_col * SQ_SIZE + SQ_SIZE // 2
                center_y = board_y + display_row * SQ_SIZE + SQ_SIZE // 2

                # Different styles for different move types
                if move.pieceCaptured != "--":
                    # Capture moves - ring around the edge
                    p.draw.circle(self.screen, COLORS['valid_move'], (center_x, center_y), SQ_SIZE // 2 - 3, 4)
                else:
                    # Regular moves - small dot in center
                    p.draw.circle(self.screen, COLORS['valid_move'], (center_x, center_y), 8)
                    p.draw.circle(self.screen, COLORS['bg_primary'], (center_x, center_y), 8, 2)

    def draw_sidebar(self):
        """Draw right sidebar with chess.com styling"""
        sidebar_x = BOARD_SIZE
        sidebar_rect = p.Rect(sidebar_x, HEADER_HEIGHT, SIDEBAR_WIDTH, BOARD_SIZE)
        p.draw.rect(self.screen, COLORS['bg_secondary'], sidebar_rect)
        p.draw.line(self.screen, COLORS['border'], (sidebar_x, HEADER_HEIGHT), (sidebar_x, WINDOW_HEIGHT))

        # Draw buttons
        for button in self.buttons:
            color = button['hover_color'] if button['hovered'] else button['color']
            p.draw.rect(self.screen, color, button['rect'])
            p.draw.rect(self.screen, COLORS['border'], button['rect'], 1)

            # Button text
            text_color = COLORS['text_primary']
            if button['color'] == COLORS['accent']:
                text_color = COLORS['text_primary']

            text_surf = self.font_medium.render(button['text'], True, text_color)
            text_rect = text_surf.get_rect(center=button['rect'].center)
            self.screen.blit(text_surf, text_rect)

        # Game information section
        info_y = HEADER_HEIGHT + 200
        self.draw_game_info_section(sidebar_x + 20, info_y)

        # Games history section
        games_y = info_y + 120
        self.draw_games_section(sidebar_x, games_y)

    def draw_game_info_section(self, x, y):
        """Draw current game information"""
        # Section title
        title = self.font_medium.render("Current Game", True, COLORS['text_primary'])
        self.screen.blit(title, (x, y))
        y += 30

        # Game stats
        stats = [
            f"Move: {len(self.gs.moveLog) + 1}",
            f"Turn: {'White' if self.gs.whiteToMove else 'Black'}",
            f"Duration: {self.get_game_duration()}",
        ]

        for stat in stats:
            stat_surf = self.font_small.render(stat, True, COLORS['text_secondary'])
            self.screen.blit(stat_surf, (x, y))
            y += 20

        # Material count (simplified)
        white_material = self.count_material('w')
        black_material = self.count_material('b')

        material_text = f"Material: {white_material} - {black_material}"
        material_surf = self.font_small.render(material_text, True, COLORS['text_secondary'])
        self.screen.blit(material_surf, (x, y))

    def draw_games_section(self, sidebar_x, y):
        """Draw saved games list"""
        list_area = self.get_game_list_area()

        # Background
        p.draw.rect(self.screen, COLORS['bg_card'], list_area)
        p.draw.rect(self.screen, COLORS['border'], list_area, 1)

        # Section header
        header_y = list_area.top + 10
        title = self.font_medium.render("Game History", True, COLORS['text_primary'])
        self.screen.blit(title, (list_area.left + 15, header_y))

        # Games count
        games_count = len(self.game_manager.get_games())
        count_text = f"({games_count} games)"
        count_surf = self.font_small.render(count_text, True, COLORS['text_muted'])
        count_x = list_area.right - count_surf.get_width() - 15
        self.screen.blit(count_surf, (count_x, header_y + 2))

        # Games list
        games = self.game_manager.get_games()
        if not games:
            no_games = self.font_small.render("No saved games yet", True, COLORS['text_muted'])
            no_games_rect = no_games.get_rect(center=(list_area.centerx, list_area.centery))
            self.screen.blit(no_games, no_games_rect)
            return

        # Instructions
        instruction_text = "Click any game to load it"
        instruction_surf = self.font_tiny.render(instruction_text, True, COLORS['text_muted'])
        instruction_x = list_area.left + 15
        instruction_y = header_y + 20
        self.screen.blit(instruction_surf, (instruction_x, instruction_y))

        # Scrollable game list
        list_start_y = header_y + 45  # Adjusted for instruction text
        item_height = 50
        visible_items = (list_area.height - 55) // item_height  # Adjusted for instruction

        start_idx = self.game_list_scroll
        end_idx = min(start_idx + visible_items, len(games))

        for i, game in enumerate(games[start_idx:end_idx]):
            item_y = list_start_y + (i * item_height)
            actual_index = start_idx + i

            # Item background
            item_rect = p.Rect(list_area.left + 5, item_y, list_area.width - 10, item_height - 2)

            # Highlight selected game
            if self.selected_game_id == game['id']:
                p.draw.rect(self.screen, COLORS['accent'], item_rect)
                text_color = COLORS['text_primary']
            elif self.hovered_game_index == actual_index:
                # Hover effect
                p.draw.rect(self.screen, COLORS['accent_hover'], item_rect)
                text_color = COLORS['text_primary']
            else:
                p.draw.rect(self.screen, COLORS['bg_secondary'], item_rect)
                text_color = COLORS['text_secondary']

            p.draw.rect(self.screen, COLORS['border'], item_rect, 1)

            # Game info
            date_obj = datetime.fromisoformat(game['date'])
            date_str = date_obj.strftime("%m/%d %H:%M")

            # Main line: date and result
            main_line = f"{date_str} • {game['result']}"
            main_surf = self.font_small.render(main_line, True, text_color)
            self.screen.blit(main_surf, (item_rect.left + 10, item_y + 8))

            # Sub line: move count
            sub_line = f"{game['move_count']} moves • vs {game['black_player']}"
            sub_surf = self.font_tiny.render(sub_line, True, COLORS['text_muted'])
            self.screen.blit(sub_surf, (item_rect.left + 10, item_y + 28))

        # Scroll indicators
        if start_idx > 0:
            scroll_up = self.font_small.render("▲", True, COLORS['text_secondary'])
            self.screen.blit(scroll_up, (list_area.right - 25, list_start_y))

        if end_idx < len(games):
            scroll_down = self.font_small.render("▼", True, COLORS['text_secondary'])
            self.screen.blit(scroll_down, (list_area.right - 25, list_area.bottom - 25))

    def draw_footer(self):
        """Draw bottom status bar"""
        footer_rect = p.Rect(0, WINDOW_HEIGHT - FOOTER_HEIGHT, WINDOW_WIDTH, FOOTER_HEIGHT)
        p.draw.rect(self.screen, COLORS['bg_secondary'], footer_rect)
        p.draw.line(self.screen, COLORS['border'], (0, WINDOW_HEIGHT - FOOTER_HEIGHT),
                    (WINDOW_WIDTH, WINDOW_HEIGHT - FOOTER_HEIGHT))

        # Status message
        status_msg = "Ready to play"
        if self.gs.checkMate:
            status_msg = "Game Over - Checkmate!"
        elif self.gs.staleMate:
            status_msg = "Game Over - Stalemate!"
        elif self.gs.inCheck():
            status_msg = "Check!"
        elif self.last_move:
            status_msg = f"Last move: {self.last_move.getChessNotation()}"

        status_surf = self.font_small.render(status_msg, True, COLORS['text_secondary'])
        self.screen.blit(status_surf, (20, WINDOW_HEIGHT - 25))

        # Keyboard shortcuts hint
        shortcuts = "Ctrl+N: New | Ctrl+Z: Undo | Ctrl+S: Save"
        shortcuts_surf = self.font_tiny.render(shortcuts, True, COLORS['text_muted'])
        shortcuts_x = WINDOW_WIDTH - shortcuts_surf.get_width() - 20
        self.screen.blit(shortcuts_surf, (shortcuts_x, WINDOW_HEIGHT - 25))

    def count_material(self, color):
        """Count material for given color"""
        values = {'p': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}
        total = 0

        for row in self.gs.board:
            for piece in row:
                if piece != "--" and piece[0] == color:
                    total += values.get(piece[1], 0)

        return total

    def get_game_duration(self):
        """Get formatted game duration"""
        duration = int(time.time() - self.game_start_time)
        minutes = duration // 60
        seconds = duration % 60
        return f"{minutes:02d}:{seconds:02d}"

    def run(self):
        """Main game loop"""
        running = True

        # Play start sound
        if SOUNDS.get('game_start'):
            SOUNDS['game_start'].play()

        while running:
            running = self.handle_events()

            # Update game state if move was made
            if self.move_made:
                self.valid_moves = self.gs.getValidMoves()
                self.move_made = False

            # Draw everything
            self.draw_everything()

            # Update display
            self.clock.tick(MAX_FPS)
            p.display.flip()

        # Auto-save on quit
        if len(self.gs.moveLog) > 0:
            result = self.get_game_result()
            moves = [move.getChessNotation() for move in self.gs.moveLog]
            self.game_manager.add_game(moves, result)

        p.quit()
        sys.exit()


def main():
    """Main function"""
    # Create necessary directories
    os.makedirs("images", exist_ok=True)
    os.makedirs("sounds", exist_ok=True)

    print("🎮 Starting Chess Desktop...")
    print("📁 Image/sound directories created")
    print("⌨️  Keyboard shortcuts: Ctrl+N (New), Ctrl+Z (Undo), Ctrl+S (Save)")

    game = ChessComGame()
    game.run()


if __name__ == "__main__":
    main()