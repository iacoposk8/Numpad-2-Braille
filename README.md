# Braille Numpad

A tool for writing and practicing six-dot Braille using the numeric keypad.

## Components

- `braille.py`: detects Braille chords and writes the character into the active application.

## Input Modes

The program asks which layout to use at startup. You can also pass it with
`--mode normal`, `--mode reverse`, `--mode one-hand`, or `--mode inline`.

### Normal numpad

| Key | Braille dot |
|---|---:|
| 7 | 1 |
| 4 | 2 |
| 1 | 3 |
| 8 | 4 |
| 5 | 5 |
| 2 | 6 |

### Reverse numpad

For a 3x2 macro keyboard rotated 180 degrees around the X axis. This flips
the top and bottom rows while keeping the left and right columns in place:

| Key | Braille dot |
|---|---:|
| 1 | 1 |
| 4 | 2 |
| 7 | 3 |
| 2 | 4 |
| 5 | 5 |
| 8 | 6 |

Examples: `D` = `1+2+5`; `Z` = `1+5+7+8`.

### One-hand keyboard

Uses `W`, `A`, `X`, `E`, `D` for dots 1–5. `C` enters dots 3 and 6
together. Examples: `D` = `WED`; `Z` = `CDW`.

### Inline keyboard

Uses `W`, `Q`, `X`, `E`, `R` for dots 1–5. `C` enters dots 3 and 6
together. Examples: `D` = `WER`; `Z` = `CRW`.

## Shortcuts

Shortcuts use the single keys assigned to dots 3, 6, and 2:

| Mode | Space | Backspace | Toggle Ctrl |
|---|---|---|---|
| Normal numpad | `1` | `2` | `4` |
| Reverse numpad | `7` | `8` | `4` |
| One-hand keyboard | `X` | regular Backspace | `A` |
| Inline keyboard | `X` | regular Backspace | `Q` |

Double-click Space for Enter, Ctrl for Caps Lock, or Backspace for number mode
(`a` = `1`, ..., `z` = `26`). Number mode is available in the numpad modes;
the alphabetic modes use the regular Backspace key.
- `Esc` = quit the program

Ctrl is a toggle. Press its layout key, enter a Braille letter, and the program
sends the corresponding shortcut, such as `Ctrl+F`. Press it again to release Ctrl.
The Ctrl key still acts as Braille dot 2 when it is part of a multi-key chord.

## Running the Python Program

Requires Python and Windows. The `keyboard` package must be installed:

```bash
pip install keyboard
```

Run with:

```bash
python braille.py
```

To skip the menu, for example:

```bash
python braille.py --mode one-hand
```

The program uses a global keyboard hook. Run it only when Braille input is needed.
