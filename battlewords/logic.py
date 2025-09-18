from __future__ import annotations

from typing import Dict, Tuple

from .models import Coord, Puzzle, GameState, Word


def build_letter_map(puzzle: Puzzle) -> Dict[Coord, str]:
    mapping: Dict[Coord, str] = {}
    for w in puzzle.words:
        for idx, c in enumerate(w.cells):
            mapping[c] = w.text[idx]
    return mapping


def reveal_cell(state: GameState, letter_map: Dict[Coord, str], coord: Coord) -> None:
    if coord in state.revealed:
        state.last_action = "Already revealed."
        return
    state.revealed.add(coord)
    state.can_guess = True
    ch = letter_map.get(coord, "·")
    if ch == "·":
        state.last_action = f"Revealed empty at ({coord.x+1},{coord.y+1})."
    else:
        state.last_action = f"Revealed '{ch}' at ({coord.x+1},{coord.y+1})."


def guess_word(state: GameState, guess_text: str) -> Tuple[bool, int]:
    if not state.can_guess:
        state.last_action = "You must reveal a cell before guessing."
        return False, 0
    guess = (guess_text or "").strip().upper()
    if not (len(guess) in (4, 5, 6) and guess.isalpha()):
        state.last_action = "Guess must be A–Z and length 4, 5, or 6."
        state.can_guess = False
        return False, 0
    if guess in state.guessed:
        state.last_action = f"Already guessed {guess}."
        state.can_guess = False
        return False, 0

    # Find matching unguessed word
    target: Word | None = None
    for w in state.puzzle.words:
        if w.text == guess and w.text not in state.guessed:
            target = w
            break

    if target is None:
        state.last_action = f"'{guess}' is not in the puzzle."
        state.can_guess = False
        return False, 0

    # Scoring: base = length, bonus = unrevealed cells in that word
    unrevealed = sum(1 for c in target.cells if c not in state.revealed)
    points = target.length + unrevealed
    state.score += points
    state.points_by_word[target.text] = points

    # Reveal all cells of the word
    for c in target.cells:
        state.revealed.add(c)
    state.guessed.add(target.text)

    state.last_action = f"Correct! +{points} points for {target.text}."
    state.can_guess = False
    return True, points


def is_game_over(state: GameState) -> bool:
    return len(state.guessed) == 6


def compute_tier(score: int) -> str:
    if score >= 42:
        return "Fantastic"
    if 38 <= score <= 41:
        return "Great"
    if 34 <= score <= 37:
        return "Good"
    return "Keep practicing"