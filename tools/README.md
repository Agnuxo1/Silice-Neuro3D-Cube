# tools/ — generación de los GIF del README

Cada script lee los datos del repositorio (no hay cifras escritas a mano salvo rótulos) y escribe en `../assets/`.
Requiere matplotlib, Pillow y NumPy/SciPy ya instalados; no instala nada, sin GPU.

| Script | Salida |
|---|---|
| `gif_header.py` | `header.gif` (ilustración conceptual del cubo) |
| `gif_01_02_03.py 1 2 3` | escritura de la camisa, confinamiento (solver radial), fuga por túnel (GLASS-006a) |
| `gif_04_07.py 4 5 6 7` | malla DFT4, tolerancias Monte Carlo, camisa discreta (GLASS-007), método |
| `gif_08.py` | comparación BPM vs ADI (GLASS-009) |

Los GIF se regeneran con `python tools/<script>.py [números]`. `gifstyle.py` fija la paleta común.
