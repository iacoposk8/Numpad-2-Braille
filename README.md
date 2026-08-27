# Braille Numpad

Strumento per scrivere ed esercitarsi con il Braille a 6 punti usando il tastierino numerico.

## Componenti

- `braille.py`: intercetta gli accordi Braille e scrive il carattere nell’applicazione attiva.

## Mappatura del tastierino

| Tasto | Punto Braille |
|---|---:|
| 7 | 1 |
| 4 | 2 |
| 1 | 3 |
| 8 | 4 |
| 5 | 5 |
| 2 | 6 |

Scorciatoie:

- `1` = spazio
- `2` = Backspace
- `0` = spazio
- `.` = Backspace
- `Esc` = termina il programma

## Avvio del programma Python

Richiede Python e Windows. Installare la dipendenza:

```bash
pip install -r requirements.txt
```

Avviare con:

```bash
python braille.py
```

In alternativa, su Windows è possibile usare `avvia_braille.bat`.

Il programma usa un hook globale della tastiera: avviarlo solo quando si desidera attivare la scrittura Braille.

## Licenza

Nessuna licenza è stata ancora definita.
