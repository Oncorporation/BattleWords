---
title: BattleWords
emoji: 🎲
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.25.0
python_version: 3.10
app_file: app.py
tags:
  - game
  - vocabulary
  - streamlit
  - education
---

# BattleWords

> **This project is used by [huggingface.co](https://huggingface.co/spaces/Surn/BattleWords) as a demonstration of interactive word games in Python.**

BattleWords is a vocabulary learning game inspired by classic Battleship mechanics. The objective is to discover hidden words on a grid, earning points for strategic guessing before all letters are revealed.

## Features

- 12x12 grid with six hidden words (2x4-letter, 2x5-letter, 2x6-letter)
- Words placed horizontally or vertically
- Radar visualization to help locate word boundaries
- Reveal grid cells and guess words for points
- Scoring tiers: Good (34–37), Great (38–41), Fantastic (42+)
- Responsive UI built with Streamlit
- Deterministic seed support (Beta/Full)
- Keyboard navigation and guessing (Beta/Full)
- Overlapping words on shared letters (Beta)
- Daily and practice modes (Full)
- Leaderboards, persistence, and advanced features (Full)
- **Game ends when all words are guessed or all word letters are revealed**

## Installation
1. Clone the repository:
   ```
   git clone
    cd battlewords
   ```
   2. (Optional) Create and activate a virtual environment:
    ```
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3. Install dependencies:
    ```
    pip install -r specs/requirements.md
    ```


## Running BattleWords

You can run the app locally using either [uv](https://github.com/astral-sh/uv) or Streamlit directly:

```
uv run streamlit run app.py
```

or
```
streamlit run app.py
```

## Folder Structure

- `app.py` – Streamlit entry point
- `battlewords/` – Python package
  - `models.py` – data models and types
  - `word_loader.py` – word list loading and validation
  - `generator.py` – word placement logic
  - `logic.py` – game mechanics (reveal, guess, scoring)
  - `ui.py` – Streamlit UI composition
  - `words/wordlist.txt` – candidate words
- `specs/` – documentation (`specs.md`, `requirements.md`)
- `tests/` – unit tests

## How to Play

1. Click grid squares to reveal letters or empty spaces.
2. After revealing a letter, enter a guess for a word in the text box.
3. Earn points for correct guesses and bonus points for unrevealed letters.
4. **The game ends when all six words are found or all word letters are revealed. Your score tier is displayed.**

## Development Phases

- **Proof of Concept (0.1.0):** No overlaps, basic UI, single session.
- **Beta (0.5.0):** Overlaps allowed on shared letters, responsive layout, keyboard support, deterministic seed.
- **Full (1.0.0):** Enhanced UX, persistence, leaderboards, daily/practice modes, advanced features.

See `specs/requirements.md` and `specs/specs.md` for full details and roadmap.

## License

BattlewordsTM. All Rights Reserved. All content, trademarks and logos are copyrighted by the owner.

## Hugging Face Spaces Configuration

BattleWords is deployable as a Hugging Face Space. To configure your Space, add a YAML block at the top of your `README.md`:

```yaml
---
title: BattleWords
emoji: 🎲
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.25.0
python_version: 3.10
app_file: app.py
tags:
  - game
  - vocabulary
  - streamlit
  - education
---
```

**Key parameters:**
- `title`, `emoji`, `colorFrom`, `colorTo`: Visuals for your Space.
- `sdk`: Use `streamlit` for Streamlit apps.
- `sdk_version`: Latest supported Streamlit version.
- `python_version`: Python version (default is 3.10).
- `app_file`: Entry point for your app.
- `tags`: List of descriptive tags.

**Dependencies:**  
Add a `requirements.txt` with your Python dependencies (e.g., `streamlit`, etc.).

**Port:**  
Streamlit Spaces use port `8501` by default.

**Embedding:**  
Spaces can be embedded in other sites using an `<iframe>`:

```html
<iframe src="https://Surn-BattleWords.hf.space?embed=true" title="BattleWords"></iframe>
```

For full configuration options, see [Spaces Config Reference](https://huggingface.co/docs/hub/spaces-config-reference) and [Streamlit SDK Guide](https://huggingface.co/docs/hub/spaces-sdks-streamlit).

