"""
Professional Desktop Chess Game
Clean UI with evaluation bar and game management
"""

import pygame as p
import os
import sys
import json
import time
from datetime import datetime
from Chess import ChessEngine

# Initialize pygame mixer FIRST
p.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
p.mixer.init()
p.init()

# Professional Desktop Dimensions
BOARD_SIZE = 720  # Large, crisp board
EVAL_BAR_WIDTH = 60  # Evaluation bar
SIDE_PANEL_WIDTH = 350  # Game info and controls
GAME_LIST_HEIGHT = 300  # Saved games list

WINDOW_WIDTH = BOARD_SIZE + EVAL_BAR_WIDTH + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = max(BOARD_SIZE, 800)  # Ensure minimum height

DIMENSION = 8
SQ_SIZE = BOARD_SIZE // DIMENSION
MAX_FPS = 60

# Professional Color Scheme
COLORS = {
    'light_square': p.Color("#f0d9b4"),
    'dark_square': p.Color("#b58863"),
    'highlight': p.Color("#ffff7f"),
    'last_move': p.Color("#7fff7f"),
    'check': p.Color("#ff4444"),
    'selected': p.Color("#00aaff"),
    'bg_panel': p.Color("#2c3e50"),
    'bg_dark': p.Color("#1a252f"),
    'text_primary': p.Color("#ecf0f1"),
    'text_secondary': p.Color("#bdc3c7"),
    'button': p.Color("#3498db"),
    'button_hover': p.Color("#2980b9"),
    'button_active': p.Color("#1f639a"),
    'eval_white': p.Color("#ffffff"),
    'eval_black': p.Color("#333333"),
    'eval_neutral': p.Color("#7f7f7f"),
    'border': p.Color("#34495e")
}

IMAGES = {}
SOUNDS = {}


class ChessEvaluator:
    """Chess position evaluator without AI - uses material and basic positional evaluation"""

    def __init__(self):
        # Piece values (standard)
        self.piece_values = {
            'p': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 0
        }

        # Position bonus tables (centipawns)
        self.pawn_table = [
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [ 5,  5, 10, 25, 25, 10,  5,  5],
            [ 0,  0,  0, 20, 20,  0,  0,  0],
            [ 5, -5,-10,  0,  0,-10, -5,  5],
            [ 5, 10, 10,-20,-20, 10, 10,  5],
            [ 0,  0,  0,  0,  0,  0,  0,  0]
        ]

        self.knight_table = [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ]

        self.bishop_table = [
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10, 10, 10, 10, 10, 10, 10,-10],
            [-10,  5,  0,  0,  0,  0,  5,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20]
        ]

        self.rook_table = [
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [ 5, 10, 10, 10, 10, 10, 10,  5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [ 0,  0,  0,  5,  5,  0,  0,  0]
        ]

        self.queen_table = [
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [ -5,  0,  5,  5,  5,  5,  0, -5],
            [  0,  0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20]
        ]

        self.king_table = [
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
            [ 20, 20,  0,  0,  0,  0, 20, 20],
            [ 20, 30, 10,  0,  0, 10, 30, 20]
        ]

    def evaluate_position(self, game_state):
        """Evaluate current position and return score in centipawns"""
        if game_state.checkMate:
            return -10000 if game_state.whiteToMove else 10000
        elif game_state.staleMate:
            return 0

        score = 0
        white_material = 0
        black_material = 0

        for row in range(8):
            for col in range(8):
                piece = game_state.board[row][col]
                if piece != "--":
                    piece_color = piece[0]
                    piece_type = piece[1]

                    # Material value
                    piece_value = self.piece_values[piece_type]

                    # Positional value
                    pos_value = self.get_positional_value(piece_type, row, col, piece_color)

                    total_value = piece_value + pos_value

                    if piece_color == 'w':
                        score += total_value
                        white_material += piece_value
                    else:
                        score -= total_value
                        black_material += piece_value

        # Additional evaluation factors
        score += self.evaluate_special_factors(game_state)

        return score, white_material, black_material

    def get_positional_value(self, piece_type, row, col, color):
        """Get positional bonus for piece"""
        tables = {
            'p': self.pawn_table,
            'N': self.knight_table,
            'B': self.bishop_table,
            'R': self.rook_table,
            'Q': self.queen_table,
            'K': self.king_table
        }

        if piece_type not in tables:
            return 0

        table = tables[piece_type]

        # Flip table for black pieces
        if color == 'b':
            table_row = 7 - row
        else:
            table_row = row

        return table[table_row][col]

    def evaluate_special_factors(self, game_state):
        """Evaluate special positional factors"""
        score = 0

        # Mobility bonus (simplified)
        valid_moves = len(game_state.getValidMoves())

        # Switch to opponent to count their moves
        game_state.whiteToMove = not game_state.whiteToMove
        opponent_moves = len(game_state.getValidMoves())
        game_state.whiteToMove = not game_state.whiteToMove

        mobility_score = (valid_moves - opponent_moves) * 2
        score += mobility_score if game_state.whiteToMove else -mobility_score

        return score


class GameManager:
    """Manages saved games and game history"""

    def __init__(self):
        self.games_file = "saved_games.json"
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
            'move_count': len(moves)
        }

        self.games.insert(0, game_data)  # Add to beginning
        self.save_games()

    def get_games(self):
        """Get list of games"""
        return self.games

    def delete_game(self, game_id):
        """Delete a game by ID"""
        self.games = [g for g in self.games if g['id'] != game_id]
        self.save_games()


class ProfessionalChessGame:
    """Main chess game class with professional desktop UI"""

    def __init__(self):
        self.screen = p.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        p.display.set_caption("Professional Chess - Desktop Edition")
        self.clock = p.time.Clock()

        # Game state
        self.gs = ChessEngine.GameState()
        self.valid_moves = self.gs.getValidMoves()
        self.move_made = False

        # UI state
        self.sq_selected = ()
        self.player_clicks = []
        self.last_move = None

        # Components
        self.evaluator = ChessEvaluator()
        self.game_manager = GameManager()

        # Current evaluation
        self.current_eval = 0
        self.white_material = 0
        self.black_material = 0

        # UI elements
        self.buttons = []
        self.game_list_scroll = 0
        self.selected_game = None

        # Load resources
        self.load_images()
        self.load_sounds()

        # Fonts
        self.font_large = p.font.Font(None, 28)
        self.font_medium = p.font.Font(None, 22)
        self.font_small = p.font.Font(None, 18)
        self.font_tiny = p.font.Font(None, 16)

        # Create UI elements
        self.create_buttons()

        # Initial evaluation
        self.update_evaluation()

    def load_images(self):
        """Load piece images with fallback"""
        pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']

        for piece in pieces:
            try:
                img_path = os.path.join("images", f"{piece}.png")
                if os.path.exists(img_path):
                    IMAGES[piece] = p.transform.scale(p.image.load(img_path), (SQ_SIZE, SQ_SIZE))
                else:
                    # Create elegant fallback pieces
                    self.create_fallback_piece(piece)
            except Exception as e:
                self.create_fallback_piece(piece)
                print(f"Using fallback for {piece}: {e}")

    def create_fallback_piece(self, piece):
        """Create elegant fallback piece graphics"""
        surf = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)

        # Colors
        piece_color = COLORS['eval_white'] if piece[0] == 'w' else COLORS['eval_black']
        border_color = COLORS['eval_black'] if piece[0] == 'w' else COLORS['eval_white']

        # Draw piece base
        center = SQ_SIZE // 2
        radius = SQ_SIZE // 3

        # Piece-specific shapes
        if piece[1] == 'p':  # Pawn
            p.draw.circle(surf, piece_color, (center, center + 10), radius - 10)
            p.draw.circle(surf, border_color, (center, center + 10), radius - 10, 2)
        elif piece[1] == 'K':  # King
            p.draw.circle(surf, piece_color, (center, center), radius)
            p.draw.circle(surf, border_color, (center, center), radius, 3)
            # Crown
            crown_points = [(center-15, center-15), (center, center-25), (center+15, center-15)]
            p.draw.polygon(surf, border_color, crown_points)
        else:  # Other pieces
            p.draw.circle(surf, piece_color, (center, center), radius)
            p.draw.circle(surf, border_color, (center, center), radius, 2)

        # Add piece letter
        text = self.font_medium.render(piece[1], True, border_color)
        text_rect = text.get_rect(center=(center, center))
        surf.blit(text, text_rect)

        IMAGES[piece] = surf

    def load_sounds(self):
        """Load sound effects"""
        sound_files = {
            'move': 'move.wav',
            'capture': 'capture.wav',
            'check': 'check.wav',
            'checkmate': 'checkmate.wav',
            'castle': 'castle.wav',
            'promotion': 'promotion.wav'
        }

        for sound_name, filename in sound_files.items():
            try:
                sound_path = os.path.join("sounds", filename)
                if os.path.exists(sound_path):
                    SOUNDS[sound_name] = p.mixer.Sound(sound_path)
            except Exception as e:
                pass  # Silent fallback

    def create_buttons(self):
        """Create UI buttons"""
        self.buttons = []
        button_x = BOARD_SIZE + EVAL_BAR_WIDTH + 20
        button_y = 20
        button_width = 150
        button_height = 35
        button_spacing = 10

        button_data = [
            ("New Game", self.new_game),
            ("Undo Move", self.undo_move),
            ("Save Game", self.save_current_game),
            ("Export PGN", self.export_pgn),
            ("Import PGN", self.import_pgn),
            ("Clear History", self.clear_games)
        ]

        for text, callback in button_data:
            button = {
                'rect': p.Rect(button_x, button_y, button_width, button_height),
                'text': text,
                'callback': callback,
                'hovered': False
            }
            self.buttons.append(button)
            button_y += button_height + button_spacing

    def update_evaluation(self):
        """Update position evaluation"""
        self.current_eval, self.white_material, self.black_material = self.evaluator.evaluate_position(self.gs)

    def handle_events(self):
        """Handle all pygame events"""
        for event in p.event.get():
            if event.type == p.QUIT:
                return False

            elif event.type == p.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_mouse_click(event.pos)
                elif event.button == 4:  # Scroll up
                    self.game_list_scroll = max(0, self.game_list_scroll - 1)
                elif event.button == 5:  # Scroll down
                    self.game_list_scroll += 1

            elif event.type == p.MOUSEMOTION:
                self.handle_mouse_motion(event.pos)

            elif event.type == p.KEYDOWN:
                self.handle_key_press(event.key)

        return True

    def handle_mouse_click(self, pos):
        """Handle mouse clicks"""
        # Check button clicks
        for button in self.buttons:
            if button['rect'].collidepoint(pos):
                button['callback']()
                return

        # Check game list clicks
        if self.handle_game_list_click(pos):
            return

        # Handle board clicks
        if pos[0] < BOARD_SIZE and pos[1] < BOARD_SIZE:
            col = pos[0] // SQ_SIZE
            row = pos[1] // SQ_SIZE

            if self.sq_selected == (row, col):
                self.sq_selected = ()
                self.player_clicks = []
            else:
                self.sq_selected = (row, col)
                self.player_clicks.append(self.sq_selected)

            if len(self.player_clicks) == 2:
                self.attempt_move()

    def handle_game_list_click(self, pos):
        """Handle clicks in the game list"""
        list_x = BOARD_SIZE + EVAL_BAR_WIDTH + 20
        list_y = 400
        list_width = SIDE_PANEL_WIDTH - 40

        if (list_x <= pos[0] <= list_x + list_width and
            list_y <= pos[1] <= list_y + GAME_LIST_HEIGHT):

            # Calculate which game was clicked
            relative_y = pos[1] - list_y
            game_index = (relative_y // 25) + self.game_list_scroll

            games = self.game_manager.get_games()
            if 0 <= game_index < len(games):
                self.selected_game = games[game_index]
                self.load_selected_game()
                return True

        return False

    def handle_mouse_motion(self, pos):
        """Handle mouse motion for hover effects"""
        for button in self.buttons:
            button['hovered'] = button['rect'].collidepoint(pos)

    def handle_key_press(self, key):
        """Handle keyboard input"""
        if key == p.K_z and p.key.get_pressed()[p.K_LCTRL]:  # Ctrl+Z
            self.undo_move()
        elif key == p.K_n and p.key.get_pressed()[p.K_LCTRL]:  # Ctrl+N
            self.new_game()
        elif key == p.K_s and p.key.get_pressed()[p.K_LCTRL]:  # Ctrl+S
            self.save_current_game()

    def attempt_move(self):
        """Attempt to make a move"""
        move = ChessEngine.Move(self.player_clicks[0], self.player_clicks[1], self.gs.board)

        for valid_move in self.valid_moves:
            if move == valid_move:
                self.make_move(valid_move)
                break
        else:
            self.player_clicks = [self.sq_selected]

    def make_move(self, move):
        """Make a move and update game state"""
        self.gs.makeMove(move)
        self.last_move = move
        self.move_made = True
        self.sq_selected = ()
        self.player_clicks = []
        self.play_sound(move)
        self.update_evaluation()

    def play_sound(self, move):
        """Play appropriate sound for move"""
        if self.gs.checkMate:
            sound = SOUNDS.get('checkmate')
        elif self.gs.inCheck:
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
        # Save current game if it has moves
        if self.gs.moveLog:
            result = self.get_game_result()
            moves = [move.getChessNotation() for move in self.gs.moveLog]
            self.game_manager.add_game(moves, result)

        self.gs = ChessEngine.GameState()
        self.valid_moves = self.gs.getValidMoves()
        self.sq_selected = ()
        self.player_clicks = []
        self.last_move = None
        self.move_made = True
        self.update_evaluation()
        self.selected_game = None

    def undo_move(self):
        """Undo the last move"""
        if self.gs.moveLog:
            self.gs.undoMove()
            self.move_made = True
            self.sq_selected = ()
            self.player_clicks = []
            self.update_evaluation()

    def save_current_game(self):
        """Save the current game"""
        if self.gs.moveLog:
            result = self.get_game_result()
            moves = [move.getChessNotation() for move in self.gs.moveLog]
            self.game_manager.add_game(moves, result)
            print("Game saved!")

    def get_game_result(self):
        """Get the result of the current game"""
        if self.gs.checkMate:
            return "1-0" if not self.gs.whiteToMove else "0-1"
        elif self.gs.staleMate:
            return "1/2-1/2"
        else:
            return "*"  # Game in progress

    def load_selected_game(self):
        """Load the selected game from the list"""
        if not self.selected_game:
            return

        # Start fresh game
        self.gs = ChessEngine.GameState()

        # Replay moves
        for move_notation in self.selected_game['moves']:
            # This is a simplified loader - you'd need proper PGN parsing for full compatibility
            valid_moves = self.gs.getValidMoves()
            # For now, just reset to new game when clicking on saved games
            break

        self.valid_moves = self.gs.getValidMoves()
        self.update_evaluation()
        self.move_made = True

    def clear_games(self):
        """Clear all saved games"""
        self.game_manager.games = []
        self.game_manager.save_games()
        self.selected_game = None
        print("Game history cleared!")

    def export_pgn(self):
        """Export current game as PGN"""
        if not self.gs.moveLog:
            print("No moves to export!")
            return

        # Simple PGN export
        pgn_content = f'[Date "{datetime.now().strftime("%Y.%m.%d")}"]\n'
        pgn_content += '[White "Human"]\n'
        pgn_content += '[Black "Human"]\n'
        pgn_content += f'[Result "{self.get_game_result()}"]\n\n'

        move_pairs = []
        for i, move in enumerate(self.gs.moveLog):
            if i % 2 == 0:
                move_pairs.append(f"{i//2 + 1}. {move.getChessNotation()}")
            else:
                move_pairs[-1] += f" {move.getChessNotation()}"

        pgn_content += " ".join(move_pairs)
        pgn_content += f" {self.get_game_result()}"

        filename = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn"
        try:
            with open(filename, 'w') as f:
                f.write(pgn_content)
            print(f"Game exported to {filename}")
        except Exception as e:
            print(f"Export failed: {e}")

    def import_pgn(self):
        """Import PGN file (placeholder)"""
        print("PGN import - would open file dialog")

    def draw_game(self):
        """Draw the entire game interface"""
        self.screen.fill(COLORS['bg_dark'])

        self.draw_board()
        self.draw_pieces()
        self.draw_highlights()
        self.draw_evaluation_bar()
        self.draw_side_panel()
        self.draw_game_info()
        self.draw_game_list()

    def draw_board(self):
        """Draw the chess board"""
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                color = COLORS['light_square'] if (row + col) % 2 == 0 else COLORS['dark_square']
                rect = p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                p.draw.rect(self.screen, color, rect)

        # Draw coordinates
        for i in range(DIMENSION):
            # Files (a-h)
            file_text = self.font_small.render(chr(ord('a') + i), True, COLORS['text_secondary'])
            self.screen.blit(file_text, (i * SQ_SIZE + 5, BOARD_SIZE - 20))

            # Ranks (1-8)
            rank_text = self.font_small.render(str(8 - i), True, COLORS['text_secondary'])
            self.screen.blit(rank_text, (5, i * SQ_SIZE + 5))

        # Board border
        p.draw.rect(self.screen, COLORS['border'], (0, 0, BOARD_SIZE, BOARD_SIZE), 3)

    def draw_pieces(self):
        """Draw pieces on the board"""
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                piece = self.gs.board[row][col]
                if piece != "--":
                    rect = p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                    self.screen.blit(IMAGES[piece], rect)

    def draw_highlights(self):
        """Draw square highlights"""
        # Highlight selected square
        if self.sq_selected:
            row, col = self.sq_selected
            self.draw_highlight(row, col, COLORS['selected'], 100)

        # Highlight last move
        if self.last_move:
            self.draw_highlight(self.last_move.startRow, self.last_move.startCol, COLORS['last_move'], 80)
            self.draw_highlight(self.last_move.endRow, self.last_move.endCol, COLORS['last_move'], 80)

        # Highlight king in check
        if self.gs.inCheck:
            king_pos = self.gs.whiteKingLocation if self.gs.whiteToMove else self.gs.blackKingLocation
            self.draw_highlight(king_pos[0], king_pos[1], COLORS['check'], 120)

        # Show valid moves for selected piece
        if self.sq_selected:
            for move in self.valid_moves:
                if move.startRow == self.sq_selected[0] and move.startCol == self.sq_selected[1]:
                    # Draw small circles on valid destination squares
                    center_x = move.endCol * SQ_SIZE + SQ_SIZE // 2
                    center_y = move.endRow * SQ_SIZE + SQ_SIZE // 2
                    p.draw.circle(self.screen, COLORS['highlight'], (center_x, center_y), 8)

    def draw_highlight(self, row, col, color, alpha):
        """Draw highlight on specific square"""
        highlight_surf = p.Surface((SQ_SIZE, SQ_SIZE))
        highlight_surf.set_alpha(alpha)
        highlight_surf.fill(color)
        self.screen.blit(highlight_surf, (col * SQ_SIZE, row * SQ_SIZE))

    def draw_evaluation_bar(self):
        """Draw the evaluation bar"""
        bar_x = BOARD_SIZE
        bar_y = 0
        bar_height = BOARD_SIZE

        # Background
        bar_rect = p.Rect(bar_x, bar_y, EVAL_BAR_WIDTH, bar_height)
        p.draw.rect(self.screen, COLORS['bg_panel'], bar_rect)
        p.draw.rect(self.screen, COLORS['border'], bar_rect, 2)

        # Calculate evaluation percentage (clamp between -1000 and +1000 centipawns)
        clamped_eval = max(-1000, min(1000, self.current_eval))
        eval_percentage = (clamped_eval + 1000) / 2000  # 0 to 1

        # White advantage (bottom part)
        white_height = int(bar_height * eval_percentage)
        white_rect = p.Rect(bar_x + 2, bar_y + bar_height - white_height - 2, EVAL_BAR_WIDTH - 4, white_height)
        p.draw.rect(self.screen, COLORS['eval_white'], white_rect)

        # Black advantage (top part)
        black_height = bar_height - white_height
        black_rect = p.Rect(bar_x + 2, bar_y + 2, EVAL_BAR_WIDTH - 4, black_height)
        p.draw.rect(self.screen, COLORS['eval_black'], black_rect)

        # Center line (equality)
        center_y = bar_y + bar_height // 2
        p.draw.line(self.screen, COLORS['border'],
                   (bar_x + 5, center_y), (bar_x + EVAL_BAR_WIDTH - 5, center_y), 2)

        # Evaluation text
        eval_text = f"{abs(self.current_eval/100):.1f}"
        if self.current_eval > 0:
            eval_text = "+" + eval_text
        elif self.current_eval < 0:
            eval_text = "-" + eval_text
        else:
            eval_text = "0.0"

        text_surf = self.font_small.render(eval_text, True, COLORS['text_primary'])
        text_rect = text_surf.get_rect(center=(bar_x + EVAL_BAR_WIDTH//2, center_y - 20))

        # Background for text
        text_bg = p.Rect(text_rect.x - 2, text_rect.y - 1, text_rect.width + 4, text_rect.height + 2)
        p.draw.rect(self.screen, COLORS['bg_panel'], text_bg)
        self.screen.blit(text_surf, text_rect)

    def draw_side_panel(self):
        """Draw the side control panel"""
        panel_x = BOARD_SIZE + EVAL_BAR_WIDTH
        panel_rect = p.Rect(panel_x, 0, SIDE_PANEL_WIDTH, WINDOW_HEIGHT)
        p.draw.rect(self.screen, COLORS['bg_panel'], panel_rect)
        p.draw.rect(self.screen, COLORS['border'], panel_rect, 2)

        # Draw buttons
        for button in self.buttons:
            color = COLORS['button_hover'] if button['hovered'] else COLORS['button']
            p.draw.rect(self.screen, color, button['rect'])
            p.draw.rect(self.screen, COLORS['border'], button['rect'], 2)

            text_surf = self.font_medium.render(button['text'], True, COLORS['text_primary'])
            text_rect = text_surf.get_rect(center=button['rect'].center)
            self.screen.blit(text_surf, text_rect)

    def draw_game_info(self):
        """Draw current game information"""
        info_x = BOARD_SIZE + EVAL_BAR_WIDTH + 20
        info_y = 280

        # Title
        title = self.font_large.render("Game Information", True, COLORS['text_primary'])
        self.screen.blit(title, (info_x, info_y))
        info_y += 35

        # Game status
        status = "White to move" if self.gs.whiteToMove else "Black to move"
        if self.gs.checkMate:
            winner = "Black" if self.gs.whiteToMove else "White"
            status = f"Checkmate! {winner} wins!"
        elif self.gs.staleMate:
            status = "Stalemate - Draw!"
        elif self.gs.inCheck:
            status += " (In Check)"

        status_surf = self.font_medium.render(status, True, COLORS['text_primary'])
        self.screen.blit(status_surf, (info_x, info_y))
        info_y += 25

        # Move count
        move_text = f"Move: {len(self.gs.moveLog) // 2 + 1}"
        if len(self.gs.moveLog) % 2 == 1:  # Black's turn
            move_text += " (Black)"
        else:
            move_text += " (White)"

        move_surf = self.font_small.render(move_text, True, COLORS['text_secondary'])
        self.screen.blit(move_surf, (info_x, info_y))
        info_y += 20

        # Material count
        material_text = f"Material: White {self.white_material} - Black {self.black_material}"
        material_surf = self.font_small.render(material_text, True, COLORS['text_secondary'])
        self.screen.blit(material_surf, (info_x, info_y))
        info_y += 20

        # Evaluation
        eval_display = f"Evaluation: {self.current_eval/100:+.1f}"
        eval_surf = self.font_small.render(eval_display, True, COLORS['text_secondary'])
        self.screen.blit(eval_surf, (info_x, info_y))

    def draw_game_list(self):
        """Draw the list of saved games"""
        list_x = BOARD_SIZE + EVAL_BAR_WIDTH + 20
        list_y = 400
        list_width = SIDE_PANEL_WIDTH - 40
        list_height = GAME_LIST_HEIGHT

        # Background
        list_rect = p.Rect(list_x, list_y, list_width, list_height)
        p.draw.rect(self.screen, COLORS['bg_dark'], list_rect)
        p.draw.rect(self.screen, COLORS['border'], list_rect, 2)

        # Title
        title = self.font_medium.render("Saved Games", True, COLORS['text_primary'])
        self.screen.blit(title, (list_x + 5, list_y - 25))

        # Games list
        games = self.game_manager.get_games()
        if not games:
            no_games_text = self.font_small.render("No saved games", True, COLORS['text_secondary'])
            text_rect = no_games_text.get_rect(center=(list_x + list_width//2, list_y + list_height//2))
            self.screen.blit(no_games_text, text_rect)
            return

        # Calculate visible range
        visible_games = list_height // 25
        start_idx = self.game_list_scroll
        end_idx = min(start_idx + visible_games, len(games))

        # Draw games
        for i, game in enumerate(games[start_idx:end_idx]):
            game_y = list_y + 5 + (i * 25)

            # Highlight selected game
            if self.selected_game and game['id'] == self.selected_game['id']:
                highlight_rect = p.Rect(list_x + 2, game_y - 2, list_width - 4, 22)
                p.draw.rect(self.screen, COLORS['button'], highlight_rect)

            # Game info
            date_str = datetime.fromisoformat(game['date']).strftime("%m/%d %H:%M")
            game_text = f"{date_str} - {game['move_count']} moves - {game['result']}"

            # Truncate if too long
            if len(game_text) > 35:
                game_text = game_text[:32] + "..."

            text_surf = self.font_tiny.render(game_text, True, COLORS['text_primary'])
            self.screen.blit(text_surf, (list_x + 5, game_y))

        # Scroll indicators
        if self.game_list_scroll > 0:
            up_arrow = self.font_small.render("▲", True, COLORS['text_primary'])
            self.screen.blit(up_arrow, (list_x + list_width - 20, list_y + 5))

        if end_idx < len(games):
            down_arrow = self.font_small.render("▼", True, COLORS['text_primary'])
            self.screen.blit(down_arrow, (list_x + list_width - 20, list_y + list_height - 20))

        # Instructions
        if games:
            instruction = "Click game to view • Scroll to navigate"
            inst_surf = self.font_tiny.render(instruction, True, COLORS['text_secondary'])
            self.screen.blit(inst_surf, (list_x + 5, list_y + list_height + 5))

    def run(self):
        """Main game loop"""
        running = True

        while running:
            running = self.handle_events()

            if self.move_made:
                self.valid_moves = self.gs.getValidMoves()
                self.move_made = False

            self.draw_game()
            self.clock.tick(MAX_FPS)
            p.display.flip()

        # Save current game before quitting if it has moves
        if self.gs.moveLog:
            result = self.get_game_result()
            moves = [move.getChessNotation() for move in self.gs.moveLog]
            self.game_manager.add_game(moves, result)

        p.quit()
        sys.exit()


def main():
    """Main function"""
    # Ensure directories exist
    os.makedirs("images", exist_ok=True)
    os.makedirs("sounds", exist_ok=True)

    game = ProfessionalChessGame()
    game.run()


if __name__ == "__main__":
    main()