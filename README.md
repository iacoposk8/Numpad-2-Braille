# Braille Numpad

A tool for writing and practicing six-dot Braille using the numeric keypad.

## Components

- `braille.py`: detects Braille chords and writes the character into the active application.

## Keypad Mapping

| Key | Braille dot |
|---|---:|
| 7 | 1 |
| 4 | 2 |
| 1 | 3 |
| 8 | 4 |
| 5 | 5 |
| 2 | 6 |

Shortcuts:

- `1` = Space
- `2` = Backspace
- `4` = toggle Ctrl (the key above `1`/Space)
- Double-click `4` = toggle Caps Lock
- Double-click `1` = Enter
- Double-click `2` = toggle numbers: `a` = `1`, `b` = `2`, ..., `z` = `26`
- `Esc` = quit the program

Ctrl is a toggle. Press `4`, enter a Braille letter, and the program sends the
corresponding Ctrl shortcut, such as `Ctrl+F`. Press `4` again to release Ctrl.
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

The program uses a global keyboard hook. Run it only when Braille input is needed.
