import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from game.game import AUTOMATED, AutomatedGame, ManualGame, create_game


class TestAutomatedGame(unittest.TestCase):
    def test_new_automated_game_state(self):
        game = create_game(AUTOMATED, "English", 7)
        self.assertIsInstance(game, AutomatedGame)
        self.assertEqual(game.move_count, 0)
        self.assertFalse(game.is_over())

    def test_step_makes_one_legal_move(self):
        game = AutomatedGame("English", 7, random.Random(1))
        legal = game.board.get_legal_moves()
        move = game.step()
        self.assertIn(move, legal)
        self.assertEqual(game.move_count, 1)
        self.assertEqual(game.peg_count(), 31)

    def test_play_to_end_reaches_game_over_on_each_board(self):
        for board_type in ("English", "Hexagon", "Diamond"):
            for seed in range(5):
                game = AutomatedGame(board_type, 7, random.Random(seed))
                game.play_to_end()
                self.assertTrue(game.is_over(), board_type)
                self.assertEqual(game.board.get_legal_moves(), [])
                self.assertGreaterEqual(game.peg_count(), 1)

    def test_step_after_game_over_returns_none(self):
        game = AutomatedGame("English", 7, random.Random(4))
        game.play_to_end()
        count = game.move_count
        self.assertIsNone(game.step())
        self.assertEqual(game.move_count, count)

    def test_same_seed_gives_same_game(self):
        a = AutomatedGame("English", 7, random.Random(42))
        b = AutomatedGame("English", 7, random.Random(42))
        a.play_to_end()
        b.play_to_end()
        self.assertEqual(a.recording.events, b.recording.events)

    def test_every_recorded_move_is_recorded_in_order(self):
        game = AutomatedGame("English", 7, random.Random(9))
        game.play_to_end()
        self.assertEqual(len(game.recording.events), game.move_count)
        self.assertTrue(all(e[0] == "move" for e in game.recording.events))

    def test_larger_board_runs_to_completion(self):
        game = AutomatedGame("English", 9, random.Random(0))
        game.play_to_end()
        self.assertTrue(game.is_over())

    def test_shares_base_behaviour_with_manual(self):
        self.assertIs(AutomatedGame.__mro__[1], ManualGame.__mro__[1])
        self.assertIsNot(AutomatedGame, ManualGame)

    def test_unknown_mode_rejected(self):
        with self.assertRaises(ValueError):
            create_game("co-op", "English", 7)


if __name__ == "__main__":
    unittest.main()
