import random

from .board import create_board
from .recording import MOVE, RANDOMIZE, Recording

MANUAL = "manual"
AUTOMATED = "automated"


class Game:
    """Behaviour shared by every game: owns a board, applies moves, detects the end, records.

    Subclasses decide *who* chooses the moves and which extra actions exist.
    """

    mode = None

    def __init__(self, board_type, size, rng=None):
        self.board_type = board_type
        self.board = create_board(board_type, size)
        self.rng = rng or random.Random()
        self.move_count = 0
        self.recording = Recording(board_type, size, self.mode)

    def make_move(self, frm, to):
        self.board.make_move(frm, to)  # raises ValueError if illegal, leaving state untouched
        self.move_count += 1
        self.recording.add_move(frm, to)

    def is_over(self):
        return self.board.is_game_over()

    def peg_count(self):
        return self.board.peg_count()

    def apply_event(self, event):
        """Apply one recorded event (used by replay); the event is re-recorded."""
        if event[0] == MOVE:
            self.make_move(event[1], event[2])
        elif event[0] == RANDOMIZE:
            self.board.set_rows(event[1])
            self.recording.add_randomize(event[1])
        else:
            raise ValueError(f"Unknown event {event[0]!r}")


class ManualGame(Game):
    """Human picks every move; may also randomize the board mid-game."""

    mode = MANUAL

    def randomize(self):
        if self.is_over():
            raise ValueError("Cannot randomize a finished game")
        self.board.randomize(self.rng)
        self.recording.add_randomize(self.board.to_rows())


class AutomatedGame(Game):
    """The computer picks every move."""

    mode = AUTOMATED

    def choose_move(self):
        moves = self.board.get_legal_moves()
        return self.rng.choice(moves) if moves else None

    def step(self):
        """Play one computer move. Returns the move, or None if the game is already over."""
        move = self.choose_move()
        if move is not None:
            self.make_move(*move)
        return move

    def play_to_end(self):
        while self.step() is not None:
            pass


GAME_MODES = {MANUAL: ManualGame, AUTOMATED: AutomatedGame}


def create_game(mode, board_type, size, rng=None):
    if mode not in GAME_MODES:
        raise ValueError(f"Unknown game mode: {mode}")
    return GAME_MODES[mode](board_type, size, rng)


def game_from_recording(recording):
    """Build a fresh game positioned at the start of a recording."""
    return create_game(recording.mode, recording.board_type, recording.size)
