# Battlewords: Implementation Requirements

This document breaks down the tasks to build Battlewords using the game rules described in `specs.md`. It is organized in phases: a minimal Proof of Concept (POC) and a Full Version with all features and polish.

Assumptions
- Tech stack: Python 3.10+, Streamlit for UI, standard library only for POC.
- Single-player, local state stored in Streamlit session state for POC.
- Grid is always 12x12 with exactly six words: two 4-letter, two 5-letter, two 6-letter words; horizontal/vertical only; no shared letters or overlaps.

Streamlit key components (API usage plan)
- State & caching
  - `st.session_state` for `puzzle`, `revealed`, `guessed`, `score`, `can_guess`, `last_action`.
  - `st.cache_data` to load and filter the word list.
- Layout & structure
  - `st.title`, `st.subheader`, `st.markdown` for headers/instructions.
  - `st.columns(12)` to render the 12×12 grid; `st.container` for grouping; `st.sidebar` for secondary controls/help.
  - `st.expander` for inline help/intel tips.
- Widgets (interaction)
  - `st.button` for each grid cell (144 total) with unique `key` to handle reveals.
  - `st.form` + `st.text_input` + `st.form_submit_button("OK")` for controlled word guessing.
  - `st.button("New Game")` or `st.link_button` to reset state.
  - `st.metric` to show score; `st.checkbox`/`st.toggle` for optional settings (e.g., show radar).
- Visualization
  - `st.pyplot` for the radar mini-grid (scatter on a 12×12 axes) or `st.plotly_chart` if interactive.
- Control flow
  - App reruns on interaction; optionally use `st.rerun()` after state resets; `st.stop()` after game over summary to freeze UI.

Folder Structure
- `app.py` – Streamlit entry point
- `battlewords/` – Python package
  - `__init__.py`
  - `models.py` – data models and types
  - `generator.py` – word placement and puzzle generation
  - `logic.py` – game mechanics (reveal, guess, scoring)
  - `ui.py` – Streamlit UI composition
  - `words/wordlist.txt` – candidate words
- `specs/` – documentation (existing)
- `tests/` – unit tests

Phase 1: Proof of Concept Version
Goal: A playable, single-session game demonstrating core rules, scoring, and radar without persistence or advanced UX.

1) Data Models
- Define `Coord(x:int, y:int)`.
- Define `Word(text:str, start:Coord, direction:str{"H","V"}, cells:list[Coord])`.
- Define `Puzzle(words:list[Word], radar:list[Coord])` – radar holds last-letter coordinates.
- Define `GameState(grid_size:int=12, puzzle:Puzzle, revealed:set[Coord], guessed:set[str], score:int, last_action:str, can_guess:bool)`.

Acceptance: Types exist and are consumed by generator/logic; simple constructors and validators.

2) Word List
- Add an English word list filtered to alphabetic uppercase, lengths in {4,5,6}.
- Ensure words contain no special characters; maintain reasonable difficulty.
- Streamlit: `st.cache_data` to memoize loading/filtering.

Acceptance: Loading function returns lists by length with >= 500 words per length or fallback minimal lists.

3) Puzzle Generation (Placement)
- Randomly place 2×4, 2×5, 2×6 letter words on a 12×12 grid.
- Constraints:
  - Horizontal (left→right) or Vertical (top→down) only.
  - No overlapping letters.
  - No shared letters between different words (cells must be unique; letters adjacent orthogonally are allowed).
- Compute radar pulses as the last cell of each word.
- Retry strategy with max attempts; raise a controlled error if generation fails.

Acceptance: Generator returns a valid `Puzzle` passing validation checks (no collisions, in-bounds, correct counts).

4) Game Mechanics
- Reveal:
  - Click a covered cell to reveal; if the cell is part of a word, show the letter; else mark empty.
  - After a reveal action, set `can_guess=True`.
  - Streamlit: 12×12 `st.columns` + `st.button(label, key=f"cell_{r}_{c}")` per cell; on click, update `st.session_state` and optionally `st.rerun()`.
- Guess:
  - Accept a guess only if `can_guess` is True and input length ∈ {4,5,6}.
  - Match guess case-insensitively against unguessed words in puzzle.
  - If correct: add base points = word length; bonus points = count of unrevealed cells in that word at guess time; mark all cells of the word as revealed; add to `guessed`.
  - If incorrect: no points awarded.
  - After any guess, set `can_guess=False` and require another reveal before next guess.
  - Streamlit: `with st.form("guess"):` + `st.text_input("Your guess", key="guess_text")` + `st.form_submit_button("OK", disabled=not st.session_state.can_guess)`.
- End of game when all 6 words are guessed; display summary and tier, then `st.stop()`.

Acceptance: Unit tests cover scoring, guess gating, and reveal behavior.

5) UI (Streamlit)
- Layout:
  - Title and brief instructions via `st.title`, `st.subheader`, `st.markdown`.
  - Left: 12×12 grid using `st.columns(12)` of `st.button`s.
  - Right: Radar mini-grid via `st.pyplot` (matplotlib scatter) or `st.plotly_chart`.
  - Bottom/right: Guess form using `st.form`, `st.text_input`, `st.form_submit_button`.
  - Score panel showing current score using `st.metric` and `st.markdown` for last action.
  - Optional `st.sidebar` to host reset/new game and settings.
- Visuals:
  - Covered cell vs revealed styles: use button labels/emojis and background color hints; if needed, small custom `st.html`/CSS for color.

Acceptance: Users can play end-to-end in one session; UI updates consistently; radar shows exactly 6 pulses.

6) Scoring Tiers
- After game ends, compute tier:
  - Good: 34–37
  - Great: 38–41
  - Fantastic: 42+
- Display final summary with found words, per-word points, total.
- Streamlit: show results in a `st.container` or `st.expander("Game summary")`.

Acceptance: Tier text shown at game end; manual test with mocked states.

7) Basic Tests
- Unit tests for:
  - Placement validity (bounds, overlap, counts).
  - Scoring logic and bonus calculation.
  - Guess gating (must reveal before next guess).

Acceptance: Tests run and pass locally.

Phase 2: Full Version (All Features and Polish)
Goal: Robust app with polish, persistence, test coverage, and optional advanced features.

A) UX and Visual Polish
- Cell rendering with consistent sizing and responsive layout (desktop/mobile).
- Keyboard support for navigation and guessing (custom JS via `st.html` or a component if needed).
- Animations for reveals and correct guesses (CSS/JS via `st.html` or component).
- Color-blind friendly palette and accessible contrast.
- Configurable themes (light/dark) via Streamlit theme config.
- Streamlit: `st.tabs` for modes/help; `st.popover`/`st.expander` for tips; `st.toast`/`st.warning` for feedback.

B) Game Content and Generation
- Curated word lists by difficulty; exclude obscure/abusive words.
- Deterministic seed support to reproduce puzzles (e.g., daily seed based on date).
- Validation pass to ensure no unintended partial words formed adjacently (content curation rule, optional).
- Optional generator diagnostics panel for QA using `st.expander` and `st.dataframe`.
- Streamlit: `st.cache_data` for word lists; `st.cache_resource` if needed for heavier resources.

C) Game Modes and Settings
- Daily Puzzle mode (same seed for all players per day).
- Practice mode (random puzzles).
- Difficulty presets that tweak word selection (common vs. rare) but still keep 2×4, 2×5, 2×6.
- Optional hint system with limited uses (e.g., reveal a random letter in an unguessed word) with score penalty.
- Streamlit: mode selection via `st.radio`/`st.segmented_control`; settings via `st.sidebar` with `st.toggle`/`st.slider`.

D) Persistence and Profiles
- Save/Load local game state (browser cookie or Streamlit session + query params).
- Cloud persistence via lightweight backend API (FastAPI) or Streamlit secrets + hosted storage for:
  - User profiles (username only), completed puzzles, scores.
  - Leaderboards for Daily mode.
- Privacy notice and opt-in for storing data.
- Streamlit: `st.text_input` for username; `st.button` to save; call backend via `requests`.

E) Leaderboards and Sharing
- Global and friends leaderboards (score and completion time if captured; note: game is strategy-first, time is optional).
- Share result string with spoiler-free grid (similar to popular word games).
- Streamlit: `st.table`/`st.dataframe` for leaderboards; `st.download_button` or copy-to-clipboard via `st.text_area` + `st.button`.

F) Observability and Quality
- Logging for generator failures and gameplay events (anonymized).
- Error boundary UI with recover/retry.
- Test suite:
  - Unit: generator, logic, scoring, gating, radar.
  - Property-based tests for generator (e.g., Hypothesis) to stress placement constraints.
  - Integration tests that simulate a full game and validate scoring.
  - Visual regression snapshots of grid/radar (optional).
- CI/CD with linting (flake8/ruff), type checks (mypy/pyright), tests, and build.
- Streamlit: developer toggles in an `st.expander` to simulate states; optional `st.fragment` to limit rerenders in hotspots.

G) Performance
- Optimize generator to avoid excessive retries (precompute candidate slots, shuffle deterministically).
- Memoize derived UI state.
- Efficient grid rendering (batch updates or delta rendering where possible in Streamlit).
- Streamlit: consider `st.fragment` for the grid/radar to avoid full-page rerenders.

H) Internationalization (Optional)
- i18n-ready strings; language toggle.
- Locale-specific word lists.
- Streamlit: language toggle via `st.selectbox`.

I) Security and Abuse Prevention
- Validate all inputs (guess strings A–Z only).
- Rate-limit backend endpoints (if any) and sanitize stored data.
- Streamlit: enforce validation in the submit handler and sanitize displayed content with strict formatting.

J) Deployment
- Streamlit Community Cloud or containerized deployment (Dockerfile) to any cloud.
- Environment configuration via `.env` or Streamlit secrets.
- Streamlit: use `st.secrets` for API keys.

Milestones and Estimates (High-level)
- Phase 1 (POC): 2–4 days
  - Models + generator + logic: 1–2 days
  - UI + scoring + radar: 1 day
  - Tests and polish: 0.5–1 day
- Phase 2 (Full): 1–2 weeks depending on features selected

Definitions of Done (per task)
- Code merged with tests and docs updated.
- No regressions in existing tests; coverage maintained or improved for core logic.
- Manual playthrough validates rules: reveal/guess gating, scoring, radar pulses, end state and tiers.
