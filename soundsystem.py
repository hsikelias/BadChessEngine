import pygame
import os


def test_sound_system():
    """Debug function to test sound loading"""

    # Initialize pygame mixer BEFORE pygame.init()
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.mixer.init()
    pygame.init()

    print("Pygame mixer initialized:", pygame.mixer.get_init())
    print("Sound folder exists:", os.path.exists("sounds"))

    # List all files in sounds folder
    if os.path.exists("sounds"):
        sound_files = os.listdir("sounds")
        print("Files in sounds folder:", sound_files)

        # Try to load each sound file
        for file in sound_files:
            if file.endswith('.wav'):
                try:
                    sound_path = os.path.join("sounds", file)
                    sound = pygame.mixer.Sound(sound_path)
                    print(f"✓ Successfully loaded: {file}")

                    # Test playing the sound
                    sound.play()
                    pygame.time.wait(500)  # Wait 500ms

                except Exception as e:
                    print(f"✗ Failed to load {file}: {e}")
    else:
        print("Sounds folder not found!")


# Proper sound loading class
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.sound_enabled = True
        self.load_sounds()

    def load_sounds(self):
        """Load all chess sound effects"""
        try:
            # Make sure mixer is initialized
            if not pygame.mixer.get_init():
                pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
                pygame.mixer.init()

            sound_files = {
                'move': 'move.wav',
                'capture': 'capture.wav',
                'check': 'check.wav',
                'checkmate': 'checkmate.wav',
                'stalemate': 'stalemate.wav',
                'castle': 'castle.wav',
                'promotion': 'promotion.wav',
                'queen_sacrifice': 'queen_sacrifice.wav',
                'rook_sacrifice': 'rook_sacrifice.wav',
                'bishop_sacrifice': 'bishop_sacrifice.wav',
                'knight_sacrifice': 'knight_sacrifice.wav',
                'enpassant': 'enpassant.wav'
            }

            for sound_name, filename in sound_files.items():
                try:
                    sound_path = os.path.join("sounds", filename)
                    if os.path.exists(sound_path):
                        self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                        print(f"Loaded: {filename}")
                    else:
                        print(f"Warning: {sound_path} not found")

                except pygame.error as e:
                    print(f"Error loading {filename}: {e}")
                    self.sound_enabled = False

        except Exception as e:
            print(f"Sound system initialization failed: {e}")
            self.sound_enabled = False

    def play_sound(self, sound_name):
        """Play a sound effect"""
        if self.sound_enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"Error playing {sound_name}: {e}")

    def play_move_sound(self, move, game_state):
        """Play appropriate sound for the move made"""
        if not self.sound_enabled:
            return

        # Check for piece sacrifices (when you lose a valuable piece)
        if move.pieceCaptured != '--':
            captured_piece = move.pieceCaptured[1]  # Get piece type (R, Q, B, N, p)

            if captured_piece == 'Q':  # Queen captured - OH NO!
                self.play_sound('queen_sacrifice')
            elif captured_piece == 'R':  # Rook captured
                self.play_sound('rook_sacrifice')
            elif captured_piece == 'B':  # Bishop captured
                self.play_sound('bishop_sacrifice')
            elif captured_piece == 'N':  # Knight captured
                self.play_sound('knight_sacrifice')
            else:  # Regular capture (pawn)
                self.play_sound('capture')
        else:
            # Regular move
            self.play_sound('move')


# Test function - add this to your main file temporarily
if __name__ == "__main__":
    test_sound_system()