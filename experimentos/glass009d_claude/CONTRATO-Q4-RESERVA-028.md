# T96/Q4 · malla reservada dx = 0,28 µm · contrato prospectivo (2026-10-10)

Publicado antes de calcular la malla reservada. Continúa `CONTRACT.md` (GLASS-009d) sin cambiar su solver, geometría, dominio, dz ni pasos (`adi2d.py`, 800 pasos de 2,5 µm). Solo se añade la malla reservada.

## Por qué esta prueba

En GLASS-009d, el caso de 96 trazos dio P(0,625) = 0,332632, P(0,5) = 0,332237 y P(0,4) = 0,332674. La diferencia entre 0,4 y 0,5 (4,4·10⁻⁴) es mayor que la de 0,5 a 0,625 (3,9·10⁻⁴), así que Q4 de monotonía falla. El continuo sí es monótono (3,3·10⁻⁴ frente a 9,3·10⁻⁵). El contraste Q4 de monotonía es estricto y no mide directamente convergencia: la dispersión total de la serie de 96 trazos es de 0,13 %. Esta prueba separa las dos cuestiones.

## Criterios (los históricos no cambian; Q5 es nuevo y se fija aquí)

- **Q1** (integral de δn, `CONTRACT.md`): |Σ|δn|dx² − δn·área exacta| / (…) < 10⁻³ en el nuevo dx.
- **Q2/Q3** (históricos): |P(0,28) − P(0,4)| < 0,005 y < 10 %.
- **Q4** (histórico, monotonía): se reporta sin cambios. Se aplica como en `CONTRACT.md`, con los pares (0,5 y 0,625) frente a (0,4 y 0,5). No involucra el punto de 0,28.
- **Q5** (nuevo, fijado ahora): dispersión relativa max−mín de {P(0,5), P(0,4), P(0,28)} dividida por su media < **0,5 %**. Se declara antes de ver P(0,28). Responde a si la serie fina está dentro de una banda pequeña, sin exigir monotonía.

## Predicciones fijadas

- **P-R1.** P(0,28) ∈ [0,331793; 0,333118]. Es la banda de ±4,4·10⁻⁴ alrededor del intervalo definido por P(0,5) y P(0,4). Si P(0,28) cae fuera, el patrón de dispersión cambia de escala.
- **P-R2.** |P(0,28) − P(0,4)| ≤ 4,4·10⁻⁴, es decir, la dispersión no crece al refinar.
- **P-R3.** Q5 se cumple (dispersión ≤ 0,5 %). Con los valores ya conocidos la dispersión es de 0,13 % si P(0,28) se mantiene dentro de la banda.

## Ejecución

- Malla N = round(128/0,28) = 457 (dominio efectivo N·dx = 127,96 µm).
- Un hijo CPU de 200 pasos por proceso (4 trozos), para cumplir el límite de 30 s. La reanudación es exacta en coma flotante (estado guardado en `.npy`); el número de pasos y el solver no cambian.
- Salida: `out/T96d_dx3_c{0..3}.json` y `resultados_q4_reserva_028.json` con las cuatro mallas y los criterios.

## Lo que no hace

- No es la malla de POINT-03 (F1, de Codex); es la misma geometría de 96 trazos en el solver 2D de GLASS-009d.
- No prueba convergencia asintótica. Con tres o cuatro mallas no hay orden de convergencia estable.
- No sustituye el estudio de dominio, que se propone aparte.
