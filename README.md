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

For a 3x2 macro keyboard rotated 180 degrees:

| Key | Braille dot |
|---|---:|
| 1 | 1 |
| 4 | 2 |
| 8 | 3 |
| 2 | 4 |
| 5 | 5 |
| 7 | 6 |

Examples: `D` = `125`; `Z` = `5817`.

### One-hand keyboard

Uses `W`, `A`, `X`, `E`, `D` for dots 1–5. `C` enters dots 3 and 6
together. Examples: `D` = `WED`; `Z` = `CDW`.

### Inline keyboard

Uses `W`, `Q`, `X`, `E`, `R` for dots 1–5. `C` enters dots 3 and 6
together. Examples: `D` = `WER`; `Z` = `CRW`.

Shortcuts use the single keys assigned to dots 3, 6, and 2. In normal mode
these are `1` = Space, `2` = Backspace, and `4` = toggle Ctrl. In reverse
mode they are `8`, `7`, and `4` respectively. Double-click Space for Enter,
Ctrl for Caps Lock, or Backspace for number mode (`a` = `1`, ..., `z` = `26`).
- `Esc` = quit the program

Ctrl is a toggle. Press its layout key, enter a Braille letter, and the program
sends the corresponding shortcut, such as `Ctrl+F`. Press it again to release Ctrl.
The Ctrl key still acts as Braille dot 2 when it is part of a multi-key chord.
In the alphabetic keyboard modes, use the regular Backspace key; `X` is Space
and `A` (one-hand) or `Q` (inline) toggles Ctrl.

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
