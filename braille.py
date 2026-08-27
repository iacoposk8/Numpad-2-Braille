import keyboard
import threading
import sys

# Complete six-dot Braille mapping -> Characters
BRAILLE_MAP = {
    # Basic alphabet (a-z)
    frozenset({'7'}): 'a',
    frozenset({'7', '4'}): 'b',
    frozenset({'7', '8'}): 'c',
    frozenset({'7', '8', '5'}): 'd',
    frozenset({'7', '5'}): 'e',
    frozenset({'7', '4', '8'}): 'f',
    frozenset({'7', '4', '8', '5'}): 'g',
    frozenset({'7', '4', '5'}): 'h',
    frozenset({'4', '8'}): 'i',
    frozenset({'4', '8', '5'}): 'j',
    frozenset({'7', '1'}): 'k',
    frozenset({'7', '4', '1'}): 'l',
    frozenset({'7', '1', '8'}): 'm',
    frozenset({'7', '1', '8', '5'}): 'n',
    frozenset({'7', '1', '5'}): 'o',
    frozenset({'7', '4', '1', '8'}): 'p',
    frozenset({'7', '4', '1', '8', '5'}): 'q',
    frozenset({'7', '4', '1', '5'}): 'r',
    frozenset({'4', '1', '8'}): 's',
    frozenset({'4', '1', '8', '5'}): 't',
    frozenset({'7', '1', '2'}): 'u',
    frozenset({'7', '4', '1', '2'}): 'v',
    frozenset({'4', '8', '5', '2'}): 'w',
    frozenset({'7', '1', '8', '2'}): 'x',
    frozenset({'7', '1', '8', '5', '2'}): 'y',
    frozenset({'7', '1', '5', '2'}): 'z',
    
    # Italian accented vowels
    frozenset({'7', '4', '1', '5', '2'}): 'à',
    frozenset({'4', '1', '8', '2'}): 'è',
    frozenset({'7', '4', '1', '8', '2'}): 'é',
    frozenset({'1', '8'}): 'ì',
    frozenset({'4', '8', '2'}): 'ò',
    frozenset({'4', '1', '8', '5', '2'}): 'ù',
}

NUMPAD_SCANCODES = {
    71: '7', 72: '8', 75: '4', 76: '5', 79: '1', 80: '2',
    82: '0', 83: '.'
}
BRAILLE_KEYS = {'7', '8', '4', '5', '1', '2'}

# Shortcuts on the six Braille keys (no need to move fingers to 0 or .)
SPECIAL_CHORDS = {
    frozenset({'1'}): 'space',
    frozenset({'2'}): 'backspace',
}

pressed_keys = set()
current_chord = set()
chord_timer = None
commit_lock = threading.Lock()

# Tolerance window in seconds (80 ms: ideal for manual synchronization)
GRACE_PERIOD = 0.08

def commit_chord():
    global current_chord
    with commit_lock:
        if not current_chord:
            return
        chord = frozenset(current_chord)
        detected = sorted(list(current_chord))
        current_chord.clear()

        if chord in SPECIAL_CHORDS:
            action = SPECIAL_CHORDS[chord]
            if action == 'space':
                print(f"\n[OK] Detected keys: {detected}  ==>  Space")
                keyboard.write(' ')
            elif action == 'backspace':
                print(f"\n[OK] Detected keys: {detected}  ==>  Backspace")
                keyboard.send('backspace')
        elif chord in BRAILLE_MAP:
            char = BRAILLE_MAP[chord]
            print(f"\n[OK] Detected keys: {detected}  ==>  Written: '{char}'")
            keyboard.write(char)
        else:
            print(f"\n[!] Unmapped combination: {detected}")

def restart_release_timer():
    """Start or restart the release timer when a finger lands or lifts."""
    global chord_timer
    if chord_timer is not None:
        chord_timer.cancel()
    chord_timer = threading.Timer(GRACE_PERIOD, commit_chord)
    chord_timer.daemon = True
    chord_timer.start()

def get_numpad_key(event):
    # The same scan code can identify arrows, Home/End, and Delete on the
    # main keyboard. Make sure the event actually comes from the keypad.
    if getattr(event, 'is_keypad', False) and event.scan_code in NUMPAD_SCANCODES:
        return NUMPAD_SCANCODES[event.scan_code]
    if getattr(event, 'is_keypad', False):
        name = str(event.name).lower().replace('num ', '').replace('numpad ', '')
        if name in ('7', '8', '4', '5', '1', '2', '0', '.', 'decimal', 'del', 'delete'):
            return '.' if name in ('.', 'decimal', 'del', 'delete') else name
    return None

def handle_keyboard_event(event):
    global chord_timer
    key = get_numpad_key(event)
    
    # Let regular main keyboard keys pass through.
    if key is None:
        return True

    # Keypad 0 = Space
    if key == '0':
        if event.event_type == 'up':
            keyboard.write(' ')
        return False

    # Keypad . = Backspace
    if key == '.':
        if event.event_type == 'up':
            keyboard.send('backspace')
        return False

    # Braille keys (7, 8, 4, 5, 1, 2)
    if key in BRAILLE_KEYS:
        if event.event_type == 'down':
            if key in pressed_keys:
                return False  # Ignore Windows auto-repeat when held down.
            
            pressed_keys.add(key)
            current_chord.add(key)
            
            # Reset the timer if a late key arrives while it is about to fire.
            if chord_timer is not None and chord_timer.is_alive():
                restart_release_timer()

            sys.stdout.write(f"\r[Live Monitor] Dita sui tasti: {sorted(list(pressed_keys))}       ")
            sys.stdout.flush()

        elif event.event_type == 'up':
            pressed_keys.discard(key)
            
            # Start the 80 ms tolerance window as soon as release begins.
            if current_chord:
                restart_release_timer()

        return False

    return True

def main():
    print("=" * 60)
    print("      BRAILLE NUMPAD KEYBOARD (80 ms tolerance)")
    print("=" * 60)
    print("- Type freely in Word, Chrome, Notepad, etc.")
    print("- Press 'Esc' to exit the program.\n")
    print("Shortcuts:")
    print("  1  ==>  Space")
    print("  2  ==>  Backspace")
    print("  Keypad 0  ==>  Space")
    print("  Keypad .  ==>  Backspace\n")

    hook = keyboard.hook(handle_keyboard_event, suppress=True)
    try:
        keyboard.wait('esc')
    finally:
        if chord_timer is not None:
            chord_timer.cancel()
        keyboard.unhook(hook)
        print("\nProgram terminated.")

if __name__ == '__main__':
    main()
