import unittest

from game.board import (
    EMPTY, INVALID, PEG, DiamondBoard, EnglishBoard, HexagonBoard, create_board,
)


class TestBoardCreation(unittest.TestCase):
    def test_english_7_has_32_pegs_and_empty_centre(self):
        board = EnglishBoard(7)
        self.assertEqual(board.peg_count(), 32)
        self.assertEqual(board.get_cell(3, 3), EMPTY)

    def test_english_corners_are_invalid(self):
        board = EnglishBoard(7)
        for pos in [(0, 0), (0, 6), (6, 0), (6, 6), (1, 1)]:
            self.assertEqual(board.get_cell(*pos), INVALID)

    def test_diamond_shape(self):
        board = DiamondBoard(7)
        self.assertEqual(board.get_cell(0, 3), PEG)
        self.assertEqual(board.get_cell(0, 0), INVALID)
        self.assertEqual(board.get_cell(3, 3), EMPTY)

    def test_hexagon_shape(self):
        board = HexagonBoard(7)
        self.assertEqual(board.get_cell(0, 0), INVALID)
        self.assertEqual(board.get_cell(0, 3), PEG)
        self.assertEqual(board.get_cell(3, 3), EMPTY)

    def test_invalid_sizes_rejected(self):
        for size in (4, 3, 0, -7, 8):
            with self.assertRaises(ValueError):
                EnglishBoard(size)

    def test_factory_and_unknown_type(self):
        self.assertIsInstance(create_board("Diamond", 9), DiamondBoard)
        with self.assertRaises(ValueError):
            create_board("Triangle", 7)


class TestMoves(unittest.TestCase):
    def test_valid_move_updates_board(self):
        board = EnglishBoard(7)
        board.make_move((1, 3), (3, 3))
        self.assertEqual(board.get_cell(1, 3), EMPTY)
        self.assertEqual(board.get_cell(2, 3), EMPTY)
        self.assertEqual(board.get_cell(3, 3), PEG)
        self.assertEqual(board.peg_count(), 31)

    def test_move_into_occupied_cell_rejected(self):
        board = EnglishBoard(7)
        with self.assertRaises(ValueError):
            board.make_move((1, 2), (3, 2))

    def test_diagonal_and_long_moves_rejected(self):
        board = EnglishBoard(7)
        self.assertFalse(board.is_valid_move((1, 2), (3, 4)))
        self.assertFalse(board.is_valid_move((0, 3), (3, 3)))

    def test_move_over_empty_cell_rejected(self):
        board = EnglishBoard(7)
        board.make_move((1, 3), (3, 3))
        # (1, 3) is now empty, so (0, 3) has nothing to jump over
        self.assertFalse(board.is_valid_move((0, 3), (2, 3)))

    def test_move_off_board_rejected(self):
        board = EnglishBoard(7)
        self.assertFalse(board.is_valid_move((2, 0), (2, -2)))

    def test_initial_english_has_four_legal_moves(self):
        self.assertEqual(len(EnglishBoard(7).get_legal_moves()), 4)


class TestGameOver(unittest.TestCase):
    def test_new_game_not_over(self):
        self.assertFalse(EnglishBoard(7).is_game_over())

    def test_game_over_when_one_peg_left(self):
        board = EnglishBoard(7)
        for r in range(7):
            for c in range(7):
                if board.cells[r][c] == PEG:
                    board.cells[r][c] = EMPTY
        board.cells[3][3] = PEG
        self.assertTrue(board.is_game_over())
        self.assertEqual(board.peg_count(), 1)

    def test_game_over_when_pegs_isolated(self):
        board = EnglishBoard(7)
        for r in range(7):
            for c in range(7):
                if board.cells[r][c] == PEG:
                    board.cells[r][c] = EMPTY
        board.cells[0][2] = PEG
        board.cells[6][4] = PEG
        self.assertTrue(board.is_game_over())


if __name__ == "__main__":
    unittest.main()
