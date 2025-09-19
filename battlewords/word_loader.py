from __future__ import annotations

import re
from typing import Dict, List

import streamlit as st
from importlib import resources


# Minimal built-ins used if the external file is missing or too small
FALLBACK_WORDS: Dict[int, List[str]] = {
    4: [
        "TREE", "BOAT", "WIND", "FROG", "LION", "MOON", "FORK", "GLOW", "GAME", "CODE",
        "DATA", "BLUE", "GOLD", "ROAD", "STAR",
    ],
    5: [
        "APPLE", "RIVER", "STONE", "PLANT", "MOUSE", "BOARD", "CHAIR", "SCALE", "SMILE", "CLOUD",
    ],
    6: [
        "ORANGE", "PYTHON", "STREAM", "MARKET", "FOREST", "THRIVE", "LOGGER", "BREATH", "DOMAIN", "GALAXY",
    ],
}


@st.cache_data(show_spinner=False)
def load_word_list() -> Dict[int, List[str]]:
    """
    Load the word list from battlewords/words/wordlist.txt, filter to uppercase A–Z,
    lengths in {4,5,6}, and dedupe while preserving order.

    If fewer than 500 entries exist for any required length, fall back to built-ins
    for that length (per specs). Sets quick status in session_state for visibility.
    """
    words_by_len: Dict[int, List[str]] = {4: [], 5: [], 6: []}
    used_source = "fallback"

    def _finalize(wbl: Dict[int, List[str]], source: str) -> Dict[int, List[str]]:
        try:
            st.session_state.wordlist_source = source
            st.session_state.word_counts = {k: len(v) for k, v in wbl.items()}
        except Exception:
            pass
        return wbl

    try:
        # Read packaged resource
        text = resources.files("battlewords.words").joinpath("wordlist.txt").read_text(encoding="utf-8")

        seen = {4: set(), 5: set(), 6: set()}
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "#" in line:
                line = line.split("#", 1)[0].strip()
            word = line.upper()
            if not re.fullmatch(r"[A-Z]+", word):
                continue
            L = len(word)
            if L in (4, 5, 6) and word not in seen[L]:
                words_by_len[L].append(word)
                seen[L].add(word)

        counts = {k: len(v) for k, v in words_by_len.items()}
        if all(counts[k] >= 500 for k in (4, 5, 6)):
            used_source = "file"
            return _finalize(words_by_len, used_source)

        # Per spec: fallback for any length below threshold
        mixed: Dict[int, List[str]] = {
            4: words_by_len[4] if counts[4] >= 500 else FALLBACK_WORDS[4],
            5: words_by_len[5] if counts[5] >= 500 else FALLBACK_WORDS[5],
            6: words_by_len[6] if counts[6] >= 500 else FALLBACK_WORDS[6],
        }
        used_source = "file+fallback" if any(counts[k] >= 500 for k in (4, 5, 6)) else "fallback"
        return _finalize(mixed, used_source)

    except Exception:
        # Missing file or read error
        used_source = "fallback"
        return _finalize(FALLBACK_WORDS, used_source)