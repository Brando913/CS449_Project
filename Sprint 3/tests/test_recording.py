import os
import random
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from game.game import AutomatedGame, ManualGame, game_from_recording
from game.recording import Recording


def replay(recording):
    game = game_from_recording(recording)
    for event in recording.events:
        game.apply_event(event)
    return game


class TestRecording(unittest.TestCase):
    def test_text_round_trip(self):
        game = ManualGame("Hexagon", 7, random.Random(1))
        game.make_move(*game.board.get_legal_moves()[0])
        game.randomize()
        game.make_move(*game.board.get_legal_moves()[0])
        loaded = Recording.from_text(game.recording.to_text())
        self.assertEqual(loaded.board_type, "Hexagon")
        self.assertEqual(loaded.size, 7)
        self.assertEqual(loaded.mode, "manual")
        self.assertEqual(loaded.events, game.recording.events)

    def test_file_round_trip(self):
        game = AutomatedGame("English", 7, random.Random(3))
        game.play_to_end()
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "game.txt")
            game.recording.save(path)
            loaded = Recording.load(path)
        self.assertEqual(loaded.events, game.recording.events)

    def test_replay_reproduces_automated_game(self):
        game = AutomatedGame("Diamond", 7, random.Random(8))
        game.play_to_end()
        copy = replay(Recording.from_text(game.recording.to_text()))
        self.assertEqual(copy.board.to_rows(), game.board.to_rows())
        self.assertEqual(copy.move_count, game.move_count)
        self.assertTrue(copy.is_over())

    def test_replay_reproduces_manual_game_with_randomize(self):
        game = ManualGame("English", 7, random.Random(6))
        for _ in range(3):
            game.make_move(*game.board.get_legal_moves()[0])
        game.randomize()
        while not game.is_over():
            game.make_move(*game.board.get_legal_moves()[0])
        copy = replay(Recording.from_text(game.recording.to_text()))
        self.assertEqual(copy.board.to_rows(), game.board.to_rows())

    def test_replay_of_game_in_progress(self):
        game = ManualGame("English", 7)
        game.make_move((1, 3), (3, 3))
        copy = replay(game.recording)
        self.assertEqual(copy.peg_count(), 31)
        self.assertFalse(copy.is_over())

    def test_bad_files_rejected(self):
        for text in ("", "hello", "PEG_SOLITAIRE_RECORDING 1\nsize=7\n",
                     "PEG_SOLITAIRE_RECORDING 1\nboard_type=English\nsize=7\nmode=manual\nmove 1 x 3 3\n",
                     "PEG_SOLITAIRE_RECORDING 1\nboard_type=English\nsize=7\nmode=manual\njump 1 2\n"):
            with self.assertRaises(ValueError):
                Recording.from_text(text)

    def test_illegal_recorded_move_fails_on_replay(self):
        text = ("PEG_SOLITAIRE_RECORDING 1\nboard_type=English\nsize=7\nmode=manual\n"
                "move 0 2 2 2\n")
        with self.assertRaises(ValueError):
            replay(Recording.from_text(text))

    def test_randomize_snapshot_must_match_board_shape(self):
        game = ManualGame("English", 7)
        with self.assertRaises(ValueError):
            game.board.set_rows(["PPPPPPP"] * 7)


if __name__ == "__main__":
    unittest.main()
