from __future__ import annotations

from typing import Iterable, Tuple, Optional

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

from .generator import generate_puzzle, load_word_list
from .logic import build_letter_map, reveal_cell, guess_word, is_game_over, compute_tier
from .models import Coord, GameState, Puzzle


CoordLike = Tuple[int, int]


def _coord_to_xy(c) -> CoordLike:
    # Supports dataclass Coord(x, y) or a 2-tuple/list.
    if hasattr(c, "x") and hasattr(c, "y"):
        return int(c.x), int(c.y)
    if isinstance(c, (tuple, list)) and len(c) == 2:
        return int(c[0]), int(c[1])
    raise TypeError(f"Unsupported Coord type: {type(c)!r}")


def _normalize_revealed(revealed: Iterable) -> set[CoordLike]:
    return {(_coord_to_xy(c) if not (isinstance(c, tuple) and len(c) == 2 and isinstance(c[0], int)) else c) for c in revealed}


def _build_letter_map(puzzle) -> dict[CoordLike, str]:
    letters: dict[CoordLike, str] = {}
    for w in getattr(puzzle, "words", []):
        text = getattr(w, "text", "")
        cells = getattr(w, "cells", [])
        for i, c in enumerate(cells):
            xy = _coord_to_xy(c)
            if 0 <= i < len(text):
                letters[xy] = text[i]
    return letters


def inject_styles() -> None:
    st.markdown(
        """
        <style>
          .bw-row { display: flex; gap: 4px; }
          .bw-cell {
            width: 100%;
            aspect-ratio: 1 / 1;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            font-weight: 700;
            user-select: none;
          }
          .bw-cell.letter { background: #1e1e1e; color: #eaeaea; }
          .bw-cell.empty  { background: #0f0f0f; } /* requested "empty" class */
          /* Make grid buttons fill their column cleanly */
          div[data-testid="stButton"] button {
            width: 100%;
            aspect-ratio: 1 / 1;
            border-radius: 4px;
            border: 1px solid #3a3a3a;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _init_session() -> None:
    if "initialized" in st.session_state and st.session_state.initialized:
        return

    words = load_word_list()
    puzzle = generate_puzzle(grid_size=12, words_by_len=words)

    st.session_state.puzzle = puzzle
    st.session_state.grid_size = 12
    st.session_state.revealed = set()
    st.session_state.guessed = set()
    st.session_state.score = 0
    st.session_state.last_action = "Welcome to Battlewords! Reveal a cell to begin."
    st.session_state.can_guess = False
    st.session_state.points_by_word = {}
    st.session_state.letter_map = build_letter_map(puzzle)
    st.session_state.initialized = True


def _new_game() -> None:
    st.session_state.clear()
    _init_session()


def _to_state() -> GameState:
    return GameState(
        grid_size=st.session_state.grid_size,
        puzzle=st.session_state.puzzle,
        revealed=st.session_state.revealed,
        guessed=st.session_state.guessed,
        score=st.session_state.score,
        last_action=st.session_state.last_action,
        can_guess=st.session_state.can_guess,
        points_by_word=st.session_state.points_by_word,
    )


def _sync_back(state: GameState) -> None:
    st.session_state.revealed = state.revealed
    st.session_state.guessed = state.guessed
    st.session_state.score = state.score
    st.session_state.last_action = state.last_action
    st.session_state.can_guess = state.can_guess
    st.session_state.points_by_word = state.points_by_word


def _render_header():
    st.title("Battlewords (POC)")
    st.subheader("Reveal cells, then guess the hidden words.")
    st.markdown(
        "- Grid is 12×12 with 6 words (two 4-letter, two 5-letter, two 6-letter).\n"
        "- After each reveal, you may submit one guess.\n"
        "- Scoring: length + unrevealed letters of that word at guess time.")


def _render_sidebar():
    with st.sidebar:
        st.header("Controls")
        st.button("New Game", width="stretch", on_click=_new_game)
        st.markdown("Radar pulses show the last letter position of each hidden word.")


def _render_radar(puzzle: Puzzle, size: int):
    fig, ax = plt.subplots(figsize=(4, 4))
    xs = [c.y + 1 for c in puzzle.radar]  # columns on x-axis
    ys = [c.x + 1 for c in puzzle.radar]  # rows on y-axis
    ax.scatter(xs, ys, c="red", s=60, marker="o")
    ax.set_xlim(0.5, size + 0.5)
    ax.set_ylim(size, 0)
    ax.set_xticks(range(1, size + 1))
    ax.set_yticks(range(1, size + 1))
    ax.grid(True, which="both", linestyle="--", alpha=0.3)
    ax.set_title("Radar")
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def _render_grid(state: GameState, letter_map):
    size = state.grid_size
    clicked: Optional[Coord] = None

    # Inject CSS for grid lines and button styling
    st.markdown(
        """
        <style>
        div[data-testid="column"] {
            padding: 0 !important;
        }
        button[data-testid="stButton"] {
            width: 32px !important;
            height: 32px !important;
            min-width: 32px !important;
            min-height: 32px !important;
            padding: 0 !important;
            margin: 0 !important;
            border: 1px solid #888 !important;
            background: #fff !important;
            font-weight: bold;
            font-size: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    grid_container = st.container()
    with grid_container:
        for r in range(size):
            cols = st.columns(size, gap="small")
            for c in range(size):
                coord = Coord(r, c)
                revealed = coord in state.revealed
                label = letter_map.get(coord, " ") if revealed else " "
                key = f"cell_{r}_{c}"
                if cols[c].button(label, key=key, help=f"({r+1},{c+1})"):
                    if not revealed:
                        clicked = coord

    if clicked is not None:
        reveal_cell(state, letter_map, clicked)
        st.session_state.letter_map = build_letter_map(st.session_state.puzzle)
        _sync_back(state)
        st.rerun()


def _render_guess_form(state: GameState):
    with st.form("guess_form"):
        guess_text = st.text_input("Your guess", value="", max_chars=12)
        submitted = st.form_submit_button("OK", disabled=not state.can_guess, width="stretch")
        if submitted:
            correct, _ = guess_word(state, guess_text)
            _sync_back(state)
            st.rerun()  # Immediately rerun to reflect guess result in UI


def _render_score_panel(state: GameState):
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Score", state.score)
    with col2:
        st.markdown(f"Last action: {state.last_action}")


def _render_game_over(state: GameState):
    st.subheader("Game Over")
    tier = compute_tier(state.score)
    st.markdown(f"Final score: {state.score} — Tier: **{tier}**")

    with st.expander("Game summary", expanded=True):
        for w in state.puzzle.words:
            pts = state.points_by_word.get(w.text, 0)
            st.markdown(f"- {w.text} ({len(w.text)}): +{pts} points")
        st.markdown(f"**Total**: {state.score}")

    st.stop()


def run_app():
    _init_session()
    _render_header()
    _render_sidebar()

    state = _to_state()

    left, right = st.columns([3, 1], gap="large")
    with left:
        _render_grid(state, st.session_state.letter_map)
    with right:
        _render_radar(state.puzzle, size=state.grid_size)
        _render_score_panel(state)

    st.divider()
    _render_guess_form(state)

    # End condition
    state = _to_state()
    if is_game_over(state):
        _render_game_over(state)