import unittest

from battlewords.generator import generate_puzzle, validate_puzzle
from battlewords.models import Coord


class TestGenerator(unittest.TestCase):
    def test_generate_valid_puzzle(self):
        p = generate_puzzle(grid_size=12, seed=1234)
        validate_puzzle(p, grid_size=12)
        # Ensure 6 words and 6 radar pulses
        self.assertEqual(len(p.words), 6)
        self.assertEqual(len(p.radar), 6)
        # Ensure no overlaps
        seen = set()
        for w in p.words:
            for c in w.cells:
                self.assertNotIn(c, seen)
                seen.add(c)
                self.assertTrue(0 <= c.x < 12 and 0 <= c.y < 12)


if __name__ == "__main__":
    unittest.main()