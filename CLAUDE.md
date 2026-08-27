# Progetto Braille

Due componenti indipendenti per scrivere ed esercitarsi con il Braille a 6 punti usando il tastierino numerico come "slate" a 6 tasti.

## File

- `braille.py` — listener di sistema (Windows) che intercetta i tasti del tastierino numerico, riconosce l'accordo Braille e scrive il carattere corrispondente in qualsiasi applicazione attiva (Word, Chrome, Blocco Note, ecc.).
- `index.html` — gioco/allenatore Braille a livelli, **standalone**: non richiede `braille.py` in esecuzione, replica in JavaScript la stessa logica di rilevamento accordo.
- `braille_backup_*.py` — copie di backup di `braille.py` fatte prima di modifiche (naming: `braille_backup_YYYY-MM-DD.py`).

## Mappatura tastierino numerico → punti Braille

Layout fisico a 2 colonne × 3 righe, letto per colonne (sinistra poi destra, dall'alto in basso):

| Tasto numpad | Punto Braille |
|---|---|
| 7 | 1 |
| 4 | 2 |
| 1 | 3 |
| 8 | 4 |
| 5 | 5 |
| 2 | 6 |

Questa mappatura è duplicata in due posti e va tenuta sincronizzata se cambia:
- `braille.py`: implicita nei `frozenset` di `BRAILLE_MAP` (es. `frozenset({'7'})` = punto 1 = `'a'`).
- `index.html`: esplicita in `NUMPAD_CODE_TO_DOT`.

Tasti numpad dedicati (fuori dal cluster 6 punti): `0` = Spazio, `.` = Backspace (solo in `braille.py`).

## `braille.py` — dettagli

- Usa la libreria `keyboard` con hook globale (`keyboard.hook(..., suppress=True)`) per intercettare gli eventi del tastierino prima che raggiungano il sistema, e `keyboard.write()` / `keyboard.send('backspace')` per iniettare l'output.
- **Rilevamento accordo**: ogni `down` aggiunge il tasto a `current_chord`; ogni `up` (ri)avvia un timer (`GRACE_PERIOD`) che, se non arrivano altri eventi entro quella finestra, "committa" l'accordo cercandolo in `BRAILLE_MAP` (o `SPECIAL_CHORDS`).
- `GRACE_PERIOD = 0.08` (80 ms) — finestra di tolleranza per dita non perfettamente sincrone. **Attenzione**: era stato erroneamente impostato a `0.8` (800 ms) per un refuso, causando un ritardo percepibile nella digitazione; corretto per allinearlo al commento originale nel codice.
- `SPECIAL_CHORDS`: scorciatoie sul cluster dei 6 tasti braille, per non dover spostare le dita su `0`/`.`:
  - `1 + 2` → Spazio
  - `1 + 5` → Backspace
- Mappa anche le vocali accentate italiane (à, è, é, ì, ò, ù) oltre all'alfabeto a-z.
- All'avvio stampa un banner con il riepilogo delle scorciatoie disponibili.
- `Esc` termina il programma.

## `index.html` — dettagli

- Gioco a 26 livelli (uno per lettera), 30 caratteri per livello, sbloccati in sequenza completando un livello a **0 errori**.
- Stato persistito in `localStorage`: `braille_max_unlocked` (livello massimo sbloccato), `braille_completed` (livelli completati a 0 errori).
- Due modalità di input accettate in parallelo:
  1. **Accordo Braille sul numpad** (standalone, non serve `braille.py`): ascolta `keydown`/`keyup` su `e.code` (`Numpad7/8/4/5/1/2`, indipendenti dallo stato di NumLock), accumula i punti premuti, e dopo `CHORD_GRACE_MS = 250` ms senza nuovi eventi risolve l'accordo tramite `DOTS_TO_LETTER` (tabella derivata da `BRAILLE_DOTS`).
  2. **Digitazione diretta di una lettera** (`a`-`z`) da tastiera normale — utile per test rapidi o senza tastierino numerico.
- `CHORD_GRACE_MS` è volutamente più alto che in `braille.py` (250 ms vs 80 ms): qui non serve reattività estrema come in un editor di testo reale.
- Genera le sequenze di livello con un algoritmo anti-streak (`shuffleAntiStreak`) che evita più di 2 ripetizioni consecutive della stessa lettera.
- Effetti sonori generati via Web Audio API (nessun asset audio esterno).
- Alla pressione di un tasto errato mostra la combinazione corretta evidenziando i punti sulla cella Braille visuale.

## Note per modifiche future

- Se si cambiano/aggiungono `SPECIAL_CHORDS` in `braille.py`, valutare se replicare l'equivalente in `index.html` (attualmente il gioco non ha bisogno di spazio/backspace, quindi non è implementato lì).
- Prima di modificare `braille.py`, fare un backup (`braille_backup_YYYY-MM-DD.py`) perché è il file "in produzione" usato per scrivere realmente nel sistema.
