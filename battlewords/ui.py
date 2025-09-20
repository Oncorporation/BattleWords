from __future__ import annotations
from . import __version__ as version
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
          /* Base grid cell visuals */
          .bw-row { display: flex; gap: 4px; flex-wrap: nowrap; }
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
            padding: 0.25rem 0.75rem;
            min-height: 2.5rem;
            transition: background 0.2s ease;
          }
          .bw-cell.letter { background: #1e1e1e; color: #eaeaea; }
          .bw-cell.empty  { background: #0f0f0f; }
          .bw-cell.bw-cell-complete { background: #b7f7b7 !important; color: #1a1a1a !important; }

          /* Final score style */
          .bw-final-score { color: #1ca41c !important; font-weight: 800; }

          /* Make grid buttons square and fill their column */
          div[data-testid="stButton"] button {
            width: 100%;
            aspect-ratio: 1 / 1;
            border-radius: 4px;
            border: 1px solid #3a3a3a;
          }

          /* Ensure grid cell columns expand equally for both buttons and revealed cells */
          div[data-testid="column"], .st-emotion-cache-zh2fnc {
            width: auto !important;
            flex: 1 1 auto !important;
            min-width: 0 !important;
            max-width: 100% !important;
          }

          /* Ensure grid rows generated via st.columns do not wrap and can scroll horizontally. */
          .bw-grid-row-anchor + div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
          }
          .bw-grid-row-anchor + div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            flex: 0 0 auto !important;
          }

          /* Mobile styles */
          @media (max-width: 640px) {
            /* Reverse the main two-column layout (radar above grid) and force full width */
            #bw-main-anchor + div[data-testid="stHorizontalBlock"] {
              flex-direction: column-reverse !important;
              width: 100% !important;
              max-width: 100vw !important;
            }
            #bw-main-anchor + div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
              width: 100% !important;
              min-width: 100% !important;
              max-width: 100% !important;
              flex: 1 1 100% !important;
            }

            /* Keep grid rows on one line on small screens too */
            .bw-grid-row-anchor + div[data-testid="stHorizontalBlock"] {
              flex-wrap: nowrap !important;
              overflow-x: auto !important;
            }
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
    st.title(f"Battlewords (Proof Of Concept) v {version}")
    st.subheader("Reveal cells, then guess the hidden words.")
    st.markdown(
        "- Grid is 12×12 with 6 words (two 4-letter, two 5-letter, two 6-letter).\n"
        "- After each reveal, you may submit one word guess below.\n"
        "- Scoring: length + unrevealed letters of that word at guess time.\n"
        "- Score Board: radar of last letter of word, score and status.\n"
        "- Words do not overlap, but may be touching.")
    inject_styles()


def _render_sidebar():
    with st.sidebar:
        st.header("Controls")
        st.button("New Game", width="stretch", on_click=_new_game)
        st.markdown(  
            "- Radar pulses show the last letter position of each hidden word.\n"
            "- After each reveal, you may submit one word guess below.\n"
            "- Scoring: length + unrevealed letters of that word at guess time.")


def _render_radar(puzzle: Puzzle, size: int):
    st.markdown(
        """
        <style>
        h3 {
            margin: 0.25rem auto;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.subheader("Score Board")
    fig, ax = plt.subplots(figsize=(4, 4))
    xs = [c.y + 1 for c in puzzle.radar]  # columns on x-axis
    ys = [c.x + 1 for c in puzzle.radar]  # rows on y-axis
    ax.scatter(xs, ys, c="red", s=60, marker="o")
    ax.set_xlim(0.5, size)
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
            # Anchor to style the following st.columns row container
            st.markdown('<div class="bw-grid-row-anchor"></div>', unsafe_allow_html=True)
            cols = st.columns(size, gap="small")
            for c in range(size):
                coord = Coord(r, c)
                revealed = coord in state.revealed
                # Get label if revealed
                label = letter_map.get(coord, " ") if revealed else " "

                # If this coord belongs to a completed (guessed) word
                is_completed_cell = False
                if revealed:
                    for w in state.puzzle.words:
                        if w.text in state.guessed and coord in w.cells:
                            is_completed_cell = True
                            break

                key = f"cell_{r}_{c}"
                tooltip = f"({r+1},{c+1})"

                if is_completed_cell:
                    # Render a styled non-button cell with green background and native browser tooltip
                    safe_label = (label or " ")
                    cols[c].markdown(
                        f'<div class="bw-cell bw-cell-complete" title="{tooltip}">{safe_label}</div>',
                        unsafe_allow_html=True,
                    )
                elif revealed:
                    # Render a styled non-button cell showing the letter with native browser tooltip
                    safe_label = (label or " ")
                    cols[c].markdown(
                        f'<div class="bw-cell letter" title="{tooltip}">{safe_label}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    # Unrevealed: render a button to allow click/reveal with tooltip
                    if cols[c].button(" ", key=key, help=tooltip):
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
    # Final score in green
    st.markdown(
        f"<span class=\"bw-final-score\">Final score: {state.score}</span> — Tier: <strong>{tier}</strong>",
        unsafe_allow_html=True,
    )

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

    # Anchor to target the main two-column layout for mobile reversal
    st.markdown('<div id="bw-main-anchor"></div>', unsafe_allow_html=True)
    left, right = st.columns([3, 1], gap="medium")
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