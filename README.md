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
- `0` = Space
- `.` = Backspace
- `Esc` = quit the program

## Running the Python Program

Requires Python and Windows. Install the dependency:

```bash
pip install -r requirements.txt
```

Run with:

```bash
python braille.py
```

The program uses a global keyboard hook. Run it only when Braille input is needed.

## License

No license has been defined yet.
