import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from game.board import EMPTY, INVALID, PEG
from game.game import MANUAL, ManualGame, create_game


class TestManualGame(unittest.TestCase):
    def test_new_manual_game_state(self):
        game = create_game(MANUAL, "English", 7)
        self.assertIsInstance(game, ManualGame)
        self.assertEqual(game.mode, MANUAL)
        self.assertEqual(game.move_count, 0)
        self.assertEqual(game.peg_count(), 32)
        self.assertFalse(game.is_over())

    def test_move_counts_and_records(self):
        game = ManualGame("English", 7)
        game.make_move((1, 3), (3, 3))
        self.assertEqual(game.move_count, 1)
        self.assertEqual(game.recording.events, [("move", (1, 3), (3, 3))])

    def test_illegal_move_changes_nothing(self):
        game = ManualGame("English", 7)
        with self.assertRaises(ValueError):
            game.make_move((1, 2), (3, 2))
        self.assertEqual(game.move_count, 0)
        self.assertEqual(game.recording.events, [])
        self.assertEqual(game.peg_count(), 32)

    def test_manual_game_ends_on_hexagon_board(self):
        game = ManualGame("Hexagon", 7, random.Random(1))
        while not game.is_over():
            game.make_move(*game.board.get_legal_moves()[0])
        self.assertTrue(game.is_over())
        self.assertEqual(game.board.get_legal_moves(), [])

    def test_manual_game_ends_on_english_board(self):
        game = ManualGame("English", 7)
        while not game.is_over():
            game.make_move(*game.board.get_legal_moves()[-1])
        self.assertEqual(game.peg_count(), 32 - game.move_count)

    def test_randomize_keeps_peg_count_and_shape(self):
        game = ManualGame("English", 7, random.Random(5))
        before_shape = [[c == INVALID for c in row] for row in game.board.cells]
        before_pegs = game.peg_count()
        game.randomize()
        self.assertEqual(game.peg_count(), before_pegs)
        self.assertEqual([[c == INVALID for c in row] for row in game.board.cells], before_shape)
        self.assertFalse(game.is_over())

    def test_randomize_changes_arrangement(self):
        game = ManualGame("English", 7, random.Random(5))
        before = game.board.to_rows()
        game.randomize()
        self.assertNotEqual(game.board.to_rows(), before)

    def test_randomize_is_recorded(self):
        game = ManualGame("Diamond", 7, random.Random(2))
        game.randomize()
        self.assertEqual(game.recording.events, [("randomize", game.board.to_rows())])

    def test_randomize_rejected_when_game_over(self):
        game = ManualGame("English", 7)
        for r in range(7):
            for c in range(7):
                if game.board.cells[r][c] == PEG:
                    game.board.cells[r][c] = EMPTY
        game.board.cells[3][3] = PEG
        with self.assertRaises(ValueError):
            game.randomize()

    def test_play_continues_after_randomize(self):
        game = ManualGame("English", 7, random.Random(3))
        game.make_move((1, 3), (3, 3))
        game.randomize()
        moves = game.board.get_legal_moves()
        self.assertTrue(moves)
        game.make_move(*moves[0])
        self.assertEqual(game.move_count, 2)


if __name__ == "__main__":
    unittest.main()
