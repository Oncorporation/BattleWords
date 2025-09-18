from __future__ import annotations

import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import streamlit as st

from .models import Coord, Word, Puzzle


# Fallback minimal word pools if file missing or too small
_FALLBACK: Dict[int, List[str]] = {
    4: ["TREE", "BOAT", "WIND", "FROG", "LION", "MOON", "FORK", "GLOW", "GAME", "CODE"],
    5: ["APPLE", "RIVER", "STONE", "PLANT", "MOUSE", "BOARD", "CHAIR", "SCALE", "SMILE", "CLOUD"],
    6: ["ORANGE", "PYTHON", "STREAM", "MARKET", "FOREST", "THRIVE", "LOGGER", "BREATH", "DOMAIN", "GALAXY"],
}


@st.cache_data(show_spinner=False)
def load_word_list() -> Dict[int, List[str]]:
    """
    Loads and filters a word list for lengths 4, 5, 6.
    Returns a dict length->words (uppercase, A–Z only).
    """
    base = Path(__file__).parent / "words" / "wordlist.txt"
    words_by_len: Dict[int, List[str]] = {4: [], 5: [], 6: []}
    if base.exists():
        try:
            for line in base.read_text(encoding="utf-8").splitlines():
                w = line.strip().upper()
                if w.isalpha() and len(w) in (4, 5, 6):
                    words_by_len[len(w)].append(w)
        except Exception:
            pass

    # Ensure minimum pools; otherwise fallback
    for L in (4, 5, 6):
        if len(words_by_len[L]) < 500:
            words_by_len[L] = _FALLBACK[L].copy()

    return words_by_len


def _fits_and_free(cells: List[Coord], used: set[Coord], size: int) -> bool:
    for c in cells:
        if not c.in_bounds(size) or c in used:
            return False
    return True


def _build_cells(start: Coord, length: int, direction: str) -> List[Coord]:
    if direction == "H":
        return [Coord(start.x, start.y + i) for i in range(length)]
    else:
        return [Coord(start.x + i, start.y) for i in range(length)]


def generate_puzzle(
    grid_size: int = 12,
    words_by_len: Optional[Dict[int, List[str]]] = None,
    seed: Optional[int] = None,
    max_attempts: int = 5000,
) -> Puzzle:
    """
    Place exactly six words: 2x4, 2x5, 2x6, horizontal or vertical,
    no cell overlaps. Radar pulses are last-letter cells.
    """
    rng = random.Random(seed)
    words_by_len = words_by_len or load_word_list()
    target_lengths = [4, 4, 5, 5, 6, 6]

    used: set[Coord] = set()
    placed: List[Word] = []

    # Pre-shuffle the word pools for variety but deterministic with seed
    pools: Dict[int, List[str]] = {L: words_by_len[L][:] for L in (4, 5, 6)}
    for L in pools:
        rng.shuffle(pools[L])

    attempts = 0
    for L in target_lengths:
        placed_ok = False
        pool = pools[L]
        if not pool:
            raise RuntimeError(f"No words available for length {L}")

        # Try different source words and positions
        word_try_order = pool[:]  # copy
        rng.shuffle(word_try_order)

        for cand_text in word_try_order:
            if attempts >= max_attempts:
                break
            attempts += 1

            # Try a variety of starts/orientations for this word
            for _ in range(50):
                direction = rng.choice(["H", "V"])
                if direction == "H":
                    row = rng.randrange(0, grid_size)
                    col = rng.randrange(0, grid_size - L + 1)
                else:
                    row = rng.randrange(0, grid_size - L + 1)
                    col = rng.randrange(0, grid_size)

                cells = _build_cells(Coord(row, col), L, direction)
                if _fits_and_free(cells, used, grid_size):
                    w = Word(cand_text, Coord(row, col), direction)
                    placed.append(w)
                    used.update(cells)
                    placed_ok = True
                    break

            if placed_ok:
                break

        if not placed_ok:
            # Hard reset and retry whole generation if we hit a wall
            if attempts >= max_attempts:
                raise RuntimeError("Puzzle generation failed: max attempts reached")
            return generate_puzzle(grid_size=grid_size, words_by_len=words_by_len, seed=rng.randrange(1 << 30))

    puzzle = Puzzle(words=placed)
    validate_puzzle(puzzle, grid_size=grid_size)
    return puzzle


def validate_puzzle(puzzle: Puzzle, grid_size: int = 12) -> None:
    # Bounds and overlap checks
    seen: set[Coord] = set()
    counts: Dict[int, int] = {4: 0, 5: 0, 6: 0}
    for w in puzzle.words:
        if len(w.text) not in (4, 5, 6):
            raise AssertionError("Word length invalid")
        counts[len(w.text)] += 1
        for c in w.cells:
            if not c.in_bounds(grid_size):
                raise AssertionError("Cell out of bounds")
            if c in seen:
                raise AssertionError("Overlapping words detected")
            seen.add(c)
        # Last cell must match radar pulse for that word
        if w.last_cell not in puzzle.radar:
            raise AssertionError("Radar pulse missing for last cell")

    if counts[4] != 2 or counts[5] != 2 or counts[6] != 2:
        raise AssertionError("Incorrect counts of word lengths")