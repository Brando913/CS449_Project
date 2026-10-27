PEG = "peg"
EMPTY = "empty"
INVALID = "invalid"

MIN_SIZE = 5


class Board:
    """Base class for peg solitaire boards.

    Subclasses only define which cells exist by overriding _is_playable().
    All move and end-of-game logic lives here and is shared by every board type.
    """

    DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))

    def __init__(self, size):
        if not isinstance(size, int) or size < MIN_SIZE or size % 2 == 0:
            raise ValueError(f"Board size must be an odd integer >= {MIN_SIZE}")
        self.size = size
        self.cells = [
            [PEG if self._is_playable(r, c) else INVALID for c in range(size)]
            for r in range(size)
        ]
        centre = size // 2
        self.cells[centre][centre] = EMPTY

    def _is_playable(self, row, col):
        raise NotImplementedError

    def in_bounds(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size

    def get_cell(self, row, col):
        if not self.in_bounds(row, col):
            return INVALID
        return self.cells[row][col]

    def peg_count(self):
        return sum(row.count(PEG) for row in self.cells)

    def is_valid_move(self, from_pos, to_pos):
        (r1, c1), (r2, c2) = from_pos, to_pos
        dr, dc = r2 - r1, c2 - c1
        if sorted((abs(dr), abs(dc))) != [0, 2]:
            return False
        mid = ((r1 + r2) // 2, (c1 + c2) // 2)
        return (
            self.get_cell(r1, c1) == PEG
            and self.get_cell(*mid) == PEG
            and self.get_cell(r2, c2) == EMPTY
        )

    def make_move(self, from_pos, to_pos):
        """Jump the peg at from_pos over its neighbour into to_pos, removing the neighbour."""
        if not self.is_valid_move(from_pos, to_pos):
            raise ValueError(f"Illegal move {from_pos} -> {to_pos}")
        (r1, c1), (r2, c2) = from_pos, to_pos
        self.cells[r1][c1] = EMPTY
        self.cells[(r1 + r2) // 2][(c1 + c2) // 2] = EMPTY
        self.cells[r2][c2] = PEG

    def get_legal_moves(self):
        moves = []
        for r in range(self.size):
            for c in range(self.size):
                if self.cells[r][c] != PEG:
                    continue
                for dr, dc in self.DIRECTIONS:
                    target = (r + 2 * dr, c + 2 * dc)
                    if self.is_valid_move((r, c), target):
                        moves.append(((r, c), target))
        return moves

    def is_game_over(self):
        return not self.get_legal_moves()


class EnglishBoard(Board):
    """Cross-shaped board; the four corner squares are removed."""

    def _is_playable(self, row, col):
        corner = (self.size - 1) // 3
        row_outside = row < corner or row >= self.size - corner
        col_outside = col < corner or col >= self.size - corner
        return not (row_outside and col_outside)


class HexagonBoard(Board):
    """Board with the corners trimmed more deeply than the English one."""

    def _is_playable(self, row, col):
        centre = self.size // 2
        return abs(row - centre) + abs(col - centre) <= centre + centre // 2


class DiamondBoard(Board):
    """Diamond: cells within Manhattan distance size//2 of the centre."""

    def _is_playable(self, row, col):
        centre = self.size // 2
        return abs(row - centre) + abs(col - centre) <= centre


BOARD_TYPES = {
    "English": EnglishBoard,
    "Hexagon": HexagonBoard,
    "Diamond": DiamondBoard,
}


def create_board(board_type, size):
    if board_type not in BOARD_TYPES:
        raise ValueError(f"Unknown board type: {board_type}")
    return BOARD_TYPES[board_type](size)
