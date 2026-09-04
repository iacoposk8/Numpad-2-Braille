import keyboard
import argparse
import threading
import sys
import time

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
    71: '7', 72: '8', 75: '4', 76: '5', 79: '1', 80: '2'
}
INPUT_MODES = {
    'normal': {
        'label': 'Normal numpad',
        'keys': {'7': {'7'}, '4': {'4'}, '1': {'1'},
                 '8': {'8'}, '5': {'5'}, '2': {'2'}},
    },
    'reverse': {
        'label': 'Reverse numpad (rotated 180 degrees)',
        'keys': {'1': {'7'}, '4': {'4'}, '8': {'1'},
                 '2': {'8'}, '5': {'5'}, '7': {'2'}},
    },
    'one-hand': {
        'label': 'One-hand keyboard (AWEDXC)',
        'keys': {'w': {'7'}, 'a': {'4'}, 'x': {'1'},
                 'e': {'8'}, 'd': {'5'}, 'c': {'1', '2'}},
    },
    'inline': {
        'label': 'Inline keyboard (QWERXC)',
        'keys': {'w': {'7'}, 'q': {'4'}, 'x': {'1'},
                 'e': {'8'}, 'r': {'5'}, 'c': {'1', '2'}},
    },
}

active_mode = 'normal'

# Shortcuts on the six Braille keys.
SPECIAL_CHORDS = {
    frozenset({'1'}): 'space',
    frozenset({'2'}): 'backspace',
    frozenset({'4'}): 'ctrl',
}

pressed_keys = set()
current_chord = set()
chord_timer = None
commit_lock = threading.Lock()
single_action_timers = {}
last_click_times = {}
ctrl_active = False
caps_lock_active = False
numbers_active = False

# Tolerance window in seconds (80 ms: ideal for manual synchronization)
GRACE_PERIOD = 0.08
DOUBLE_CLICK_WINDOW = 0.30

NUMBER_MAP = {chr(ord('a') + index): str(index + 1) for index in range(26)}

def perform_single_action(action):
    global ctrl_active, numbers_active
    if action == 'space':
        keyboard.write(' ')
    elif action == 'backspace':
        keyboard.send('backspace')
    elif action == 'ctrl':
        ctrl_active = not ctrl_active
        print(f"\n[MODE] Ctrl {'active' if ctrl_active else 'released'}")

def perform_double_action(action):
    global caps_lock_active, numbers_active, ctrl_active
    if action == 'ctrl':
        caps_lock_active = not caps_lock_active
        ctrl_active = False
        print(f"\n[MODE] Caps Lock {'active' if caps_lock_active else 'released'}")
    elif action == 'space':
        keyboard.send('enter')
    elif action == 'backspace':
        numbers_active = not numbers_active
        print(f"\n[MODE] Numbers {'active' if numbers_active else 'released'}")

def handle_special_action(action, detected):
    """Delay single-key actions long enough to recognize a double click."""
    now = time.monotonic()
    previous = last_click_times.get(action, 0)
    pending = single_action_timers.get(action)
    if now - previous <= DOUBLE_CLICK_WINDOW:
        if pending is not None:
            pending.cancel()
        single_action_timers.pop(action, None)
        last_click_times.pop(action, None)
        print(f"\n[OK] Detected keys: {detected}  ==>  Double-click: {action}")
        perform_double_action(action)
        return

    last_click_times[action] = now
    print(f"\n[OK] Detected keys: {detected}  ==>  {action.title()}")
    if action == 'ctrl':
        # Ctrl must be available immediately for the following Braille chord.
        perform_single_action(action)
        return
    timer = threading.Timer(DOUBLE_CLICK_WINDOW, perform_single_action, args=(action,))
    timer.daemon = True
    single_action_timers[action] = timer
    timer.start()

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
            handle_special_action(action, detected)
        elif chord in BRAILLE_MAP:
            char = BRAILLE_MAP[chord]
            output = NUMBER_MAP.get(char, char) if numbers_active else char
            if caps_lock_active and output.isalpha():
                output = output.upper()
            print(f"\n[OK] Detected keys: {detected}  ==>  Written: '{output}'")
            if ctrl_active:
                keyboard.send(f'ctrl+{char}')
            else:
                keyboard.write(output)
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
        if name in ('7', '8', '4', '5', '1', '2'):
            return name
    return None

def get_input_key(event):
    """Return the physical key used by the selected input mode."""
    if active_mode in ('normal', 'reverse'):
        return get_numpad_key(event)
    key = str(event.name).lower()
    return key if key in INPUT_MODES[active_mode]['keys'] else None

def handle_keyboard_event(event):
    global chord_timer
    key = get_input_key(event)
    
    # Let regular main keyboard keys pass through.
    if key is None:
        return True

    if key in INPUT_MODES[active_mode]['keys']:
        if event.event_type == 'down':
            if key in pressed_keys:
                return False  # Ignore Windows auto-repeat when held down.
            
            pressed_keys.add(key)
            current_chord.update(INPUT_MODES[active_mode]['keys'][key])
            
            # Reset the timer if a late key arrives while it is about to fire.
            if chord_timer is not None and chord_timer.is_alive():
                restart_release_timer()

            sys.stdout.write(f"\r[Live Monitor] Fingers on keys: {sorted(list(pressed_keys))}       ")
            sys.stdout.flush()

        elif event.event_type == 'up':
            pressed_keys.discard(key)
            
            # Start the 80 ms tolerance window as soon as release begins.
            if current_chord:
                restart_release_timer()

        return False

    return True

def choose_mode(requested_mode=None):
    """Choose an input layout from the command line or an interactive menu."""
    if requested_mode:
        return requested_mode
    print("Choose an input mode:")
    mode_names = list(INPUT_MODES)
    for index, mode_name in enumerate(mode_names, 1):
        print(f"  {index}) {INPUT_MODES[mode_name]['label']}")
    while True:
        choice = input("Mode [1]: ").strip() or '1'
        if choice.isdigit() and 1 <= int(choice) <= len(mode_names):
            return mode_names[int(choice) - 1]
        print("Please enter a number from 1 to 4.")

def key_for_chord(chord):
    """Return the single physical key assigned to a canonical chord, if any."""
    return next((key for key, value in INPUT_MODES[active_mode]['keys'].items()
                 if value == set(chord)), None)

def main():
    global active_mode
    parser = argparse.ArgumentParser(description='Type six-dot Braille chords with different keyboard layouts.')
    parser.add_argument('-m', '--mode', choices=INPUT_MODES, help='skip the interactive mode menu')
    args = parser.parse_args()
    active_mode = choose_mode(args.mode)

    print("=" * 60)
    print("      BRAILLE KEYBOARD (80 ms tolerance)")
    print("=" * 60)
    print(f"- Input mode: {INPUT_MODES[active_mode]['label']}")
    print("- Type freely in Word, Chrome, Notepad, etc.")
    print("- Press 'Esc' to exit the program.")
    space_key = key_for_chord({'1'})
    backspace_key = key_for_chord({'2'})
    ctrl_key = key_for_chord({'4'})
    print(f"- {ctrl_key}: toggle Ctrl; double-click: Caps Lock.")
    print(f"- {space_key}: Space; double-click: Enter.")
    if backspace_key:
        print(f"- {backspace_key}: Backspace; double-click: number mode.")
    else:
        print("- Use regular Backspace (the number-mode shortcut is unavailable in this layout).")
    print()

    hook = keyboard.hook(handle_keyboard_event, suppress=True)
    try:
        keyboard.wait('esc')
    finally:
        if chord_timer is not None:
            chord_timer.cancel()
        for timer in single_action_timers.values():
            timer.cancel()
        keyboard.unhook(hook)
        print("\nProgram terminated.")

if __name__ == '__main__':
    main()
