import unittest

from battlewords.logic import build_letter_map, reveal_cell, guess_word, is_game_over
from battlewords.models import Coord, Word, Puzzle, GameState


class TestLogic(unittest.TestCase):
    def make_state(self):
        w1 = Word("TREE", Coord(0, 0), "H")
        w2 = Word("APPLE", Coord(2, 0), "H")
        w3 = Word("ORANGE", Coord(4, 0), "H")
        w4 = Word("WIND", Coord(0, 6), "V")
        w5 = Word("MOUSE", Coord(0, 8), "V")
        w6 = Word("PYTHON", Coord(0, 10), "V")
        p = Puzzle([w1, w2, w3, w4, w5, w6])
        state = GameState(
            grid_size=12,
            puzzle=p,
            revealed=set(),
            guessed=set(),
            score=0,
            last_action="",
            can_guess=False,
        )
        return state, p

    def test_reveal_and_guess_gating(self):
        state, puzzle = self.make_state()
        letter_map = build_letter_map(puzzle)
        # Can't guess before reveal
        ok, pts = guess_word(state, "TREE")
        self.assertFalse(ok)
        self.assertEqual(pts, 0)
        # Reveal one cell then guess
        reveal_cell(state, letter_map, Coord(0, 0))
        self.assertTrue(state.can_guess)
        ok, pts = guess_word(state, "TREE")
        self.assertTrue(ok)
        self.assertGreater(pts, 0)
        self.assertIn("TREE", state.guessed)
        self.assertFalse(state.can_guess)

    def test_game_over(self):
        state, puzzle = self.make_state()
        letter_map = build_letter_map(puzzle)
        # Guess all words after a reveal each time
        for w in puzzle.words:
            reveal_cell(state, letter_map, w.start)
            ok, _ = guess_word(state, w.text)
            self.assertTrue(ok)
        self.assertTrue(is_game_over(state))


if __name__ == "__main__":
    unittest.main()