from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, List, Set, Dict


Direction = Literal["H", "V"]


@dataclass(frozen=True, order=True)
class Coord:
    x: int  # row, 0-based
    y: int  # col, 0-based

    def in_bounds(self, size: int) -> bool:
        return 0 <= self.x < size and 0 <= self.y < size


@dataclass
class Word:
    text: str
    start: Coord
    direction: Direction
    cells: List[Coord] = field(default_factory=list)

    def __post_init__(self):
        self.text = self.text.upper()
        if self.direction not in ("H", "V"):
            raise ValueError("direction must be 'H' or 'V'")
        if not self.text.isalpha():
            raise ValueError("word must be alphabetic A–Z only")
        # compute cells based on start and direction
        length = len(self.text)
        cells: List[Coord] = []
        for i in range(length):
            if self.direction == "H":
                cells.append(Coord(self.start.x, self.start.y + i))
            else:
                cells.append(Coord(self.start.x + i, self.start.y))
        object.__setattr__(self, "cells", cells)

    @property
    def length(self) -> int:
        return len(self.text)

    @property
    def last_cell(self) -> Coord:
        return self.cells[-1]


@dataclass
class Puzzle:
    words: List[Word]
    radar: List[Coord] = field(default_factory=list)

    def __post_init__(self):
        pulses = [w.last_cell for w in self.words]
        self.radar = pulses


@dataclass
class GameState:
    grid_size: int
    puzzle: Puzzle
    revealed: Set[Coord]
    guessed: Set[str]
    score: int
    last_action: str
    can_guess: bool
    points_by_word: Dict[str, int] = field(default_factory=dict)