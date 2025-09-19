# Battlewords Game Requirements (specs.md)

## Overview
Battlewords is inspired by the classic Battleship game, but uses words instead of ships. The objective is to discover hidden words on a grid, earning points for strategic guessing before all letters are revealed.

## Game Board
- 12 x 12 grid.
- Six hidden words:
  - Two four-letter words
  - Two five-letter words
  - Two six-letter words
- Words are placed horizontally (left-right) or vertically (top-down), not diagonally.
- Entry point is `app.py`.

## Gameplay (Common)
- Players click grid squares to reveal letters or empty spaces.
- Empty revealed squares are styled with CSS class `empty`.
- After any reveal, the app immediately reruns (`st.rerun`) to show the change.
- Use radar pulses to locate word boundaries (first and last letters).
- After revealing a letter, players may guess a word by entering it in a text box.
- Guess submission triggers an immediate rerun to reflect results.
- Only one guess per letter reveal; must uncover another letter before guessing again.

## Scoring
- Each correct word guess awards points:
  - 1 point per letter in the word
  - Bonus points for each hidden letter at the time of guessing
- Score tiers:
  - Good: 34-37
  - Great: 38-41
  - Fantastic: 42+

## POC (0.1.0) Rules
- No overlaps: words do not overlap or share letters.
- UI: basic grid, radar, and guess form.
- No keyboard interaction requirement.
- Seed is optional and not standardized.

## Beta (0.5.0) Additions
- Overlaps allowed on shared letters: words may cross only where letters match; still forbid conflicting letters in the same cell.
- Optional validation pass to avoid unintended adjacent partial words (content curation rule).
- Cell rendering with consistent sizing and responsive layout (desktop/mobile).
- Keyboard support for navigation and guessing (custom JS via `st.html` or a component).
- Deterministic seed support to reproduce puzzles (e.g., daily seed derived from date).

## Full (1.0.0) Rules
- No overlaps: words do not overlap or share letters.   
- Enhanced UX polish (animations, accessibility, themes).
- Persistence, leaderboards, and additional modes as specified in requirements.
- Deterministic daily mode and practice mode supported.

## UI Elements
- 12x12 grid
- Radar screen (shows last letter locations); y-axis inverted so (0,0) is top-left
- Text box for word guesses
- Score display (shows word, base points, bonus points, total score)

## Word List
- External list at `battlewords/words/wordlist.txt`.
- Loaded by `battlewords.word_loader.load_word_list()` with caching.
- Filtered to uppercase A–Z, lengths in {4,5,6}; falls back if < 500 per length.

## Generator
- Centralized word loader.
- No duplicate word texts are selected.

## Entry Point
- The Streamlit entry point is `app.py`.

## Copyright
BattlewordsTM. All Rights Reserved. All content, trademarks and logos are copyrighted by the owner.
