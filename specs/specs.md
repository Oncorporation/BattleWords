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
- Words do not overlap or share letters.
- Radar screen indicates the location of the last letter of each word.

## Gameplay
- Players click grid squares to reveal letters or empty spaces.
- Blue squares turn black if empty; otherwise, a letter is revealed.
- Use radar pulses to locate word boundaries (first and last letters).
- After revealing a letter, players may guess a word by entering it in a text box.
- Only one guess per letter reveal; must uncover another letter before guessing again.

## Scoring
- Each correct word guess awards points:
  - 1 point per letter in the word
  - Bonus points for each hidden letter at the time of guessing
- Score tiers:
  - Good: 34-37
  - Great: 38-41
  - Fantastic: 42+

## Strategy
- Focus on finding word boundaries using radar.
- Guess words with hidden letters for higher scores.
- The game rewards strategy over speed.

## UI Elements
- 12x12 grid
- Radar screen (shows last letter locations)
- Text box for word guesses
- Score display (shows word, base points, bonus points, total score)

## Copyright
BattlewordsTM. All Rights Reserved. All content, trademarks and logos are copyrighted by the owner.
