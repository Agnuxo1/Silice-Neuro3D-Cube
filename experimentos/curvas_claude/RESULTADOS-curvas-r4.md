# RESULTADOS curvas ronda 4 (Tarea I4): signo de Delta n_eff y radio critico por continuacion

MODELO NUMERICO. No es un dispositivo ni una medida. Ninguna cifra es dato de laboratorio. Perdida por radiacion y dB/cm NO calculadas.

Contrato: `CONTRATO-curvas-r4.md` (escrito a las 10:02 UTC, antes del calculo; umbrales fijados). Codigo: `curvas_r4.py`. Salidas: `resultados_curvas_r4.json` (pass calculado por el codigo), `log_curvas_r4_L{40,80,100}.txt`, `ckpt_curvas_r4_L{40,80,100}.json`.

## Estado

**PARTIAL** (regla del contrato: las cadenas de L = 80 y 100 no llegan a R = 2 mm). L = 80 se detiene en 5 mm (S_prev = 0,150). L = 100 se detiene en 7 mm (S_prev = 0,690). Los tres criterios evaluados (I4.0, I4.1, I4.2) tienen pass = true por codigo; I4.2 es true solo como cota, no como valor de R_c.

## Resumen de criterios

| criterio | descripcion | resultado | pass |
|---|---|---|---|
| I4.0 | verificacion: (a) contraste con r3 L = 40; (b) coeficiente perturbativo frente a numerico, R = 10 mm; (c) eigenpares | (a) diferencia maxima 2,2e-16 frente a 1e-10; (b) diferencia relativa 0,955 % frente a 2 %; (c) residuo maximo 2,2e-15 frente a 1e-8 | true |
| I4.1 | signo: (i) Delta n > 0 en la cadena; (ii) primer orden nulo y c2 > 0; (iii) pendiente log-log en [-2,05; -1,95] a L = 100 | (i) positivo en todos los puntos evaluados de L = 40, 80 y 100; (ii) primer orden -3,8e-13, c2 = 7367 um^2 > 0; (iii) pendiente -2,0062 | true |
| I4.2 | radio critico con S_rec = 0,9 a L = 100 y convergencia en L para R >= R_a | R_a = 10 mm, R_b = 7 mm (paso fallido). Cota R_c en [7; 10] mm, sin interpolar. Convergencia |n(100) - n(80)| en 50, 20 y 10 mm: 0; 8,2e-13; 1,2e-8 (umbral 1e-6) | true (solo como cota) |
| I4.3 | perdida por radiacion | no calculada | null |

## I4.0: verificacion del metodo

- (a) Contraste con la ronda 3 (`ckpt_curvas_r3_L40.json`, mismo modelo, L = 40): diferencias de n_eff de 0 (recto, R = 50 y 20 mm) y 2,2e-16 (R = 10 mm). PASS frente a 1e-10.
- (b) Coeficiente de segundo orden a L = 40: c2 = 7367,285 um^2, prediccion Delta n = c2 / R^2 frente a la cadena numerica:

| R (mm) | Delta n numerico (L = 40) | Delta n perturbativo | cociente | diferencia relativa |
|---|---|---|---|---|
| 50 | 2,947689e-06 | 2,946914e-06 | 1,000263 | 0,026 % |
| 20 | 1,845069e-05 | 1,841821e-05 | 1,001763 | 0,176 % |
| 10 | 7,437628e-05 | 7,367285e-05 | 1,009548 | 0,955 % |

  La diferencia relativa crece como ~1/R^2 (factor 6,8 entre 50 y 20 mm; 5,4 entre 20 y 10 mm), lo que es coherente con que el siguiente termino de n_eff sea de orden 1/R^4 (ver I4.1). PASS frente a 2 %.
- (c) Residuo relativo maximo de todos los modos seleccionados (L = 40, 80 y 100): 2,2e-15. Error de normalizacion maximo: 2,2e-16. PASS.

## I4.1: signo y forma de Delta n_eff

Derivacion (analitica, fijada en el contrato): con n_eq = n_xy (1 + X/R), el cuadrado del indice es n_eq^2 = n_xy^2 (1 + 2 lam X + lam^2 X^2), con lam = 1/R. El operador discreto es exactamente P(lam) = P0 + lam D1 + lam^2 D2, con D1 = 2 k0^2 cavg(n^2 X) y D2 = k0^2 cavg(n^2 X^2).

- Paridad: X -> -X junto con lam -> -lam deja invariante el problema recto (nucleo centrado). Luego mu(lam) es par en lam y no hay termino en 1/R. Medido: <u0|D1|u0> = -3,8e-13, cero a precision de maquina.
- Segundo orden: mu(lam) - mu0 = lam^2 [<D2> + S2], con <D2> = 294,48 y S2 = sum_m |<m|D1|0>|^2 / (mu0 - mu_m) = 348 891,5. mu0 es el autovalor mas alto de P0, luego todos los denominadores son positivos y ambos terminos son positivos. Por tanto Delta mu > 0 y Delta n_eff = c2 / R^2 > 0, con c2 = (<D2> + S2) / (2 k0^2 n_eff0) = 7367 um^2.
- Predominio: S2 es ~1185 veces <D2>. El efecto dominante es el acoplo con los modos excitados de la caja.
- Lectura: n_eff sube al bajar R. Es el signo observado en la ronda 3 (I3.2). La expectativa de la ronda 1 (C2: decrece al bajar R) queda refutada de nuevo; C2 no se cambia.

Cadena numerica, Delta n_eff = n_eff(R) - n_eff(recto):

| R (mm) | L = 40: Delta n (S_rec) | L = 80: Delta n (S_rec) | L = 100: Delta n (S_rec) |
|---|---|---|---|
| 50 | +2,947689e-06 (0,998787) | +2,947689e-06 (0,998787) | +2,9477e-06 (0,998787) |
| 20 | +1,845069e-05 (0,992406) | +1,845069e-05 (0,992406) | +1,8451e-05 (0,992406) |
| 10 | +7,437628e-05 (0,968946) | +7,444316e-05 (0,968026) | +7,4431e-05 (0,961102) |
| 7 | +1,544501e-04 (0,929427) | +1,571046e-04 (0,890689) | +1,5709e-04 (0,651548, paso fallido, S_prev 0,690) |
| 5 | +3,265831e-04 (0,765638, paso fallido, S_prev 0,895) | +2,286114e-04 (0,162787, paso fallido, S_prev 0,150) | no evaluado |

Todos los puntos evaluados tienen Delta n > 0. Pendiente log-log entre 50 y 10 mm a L = 100: -2,0062 (intervalo [-2,05; -1,95]). Los puntos de 7 mm en L = 80 y 100 tienen n_eff casi identicos (1,442348976 frente a 1,442348959, diferencia 1,8e-8), pero solapes con el paso anterior muy distintos (0,951 frente a 0,690); ver I4.2.

## I4.2: radio critico por solape

Regla fijada: S_rec = (sum psi psi_recto h^2)^2. R_a = mayor R con S_rec > 0,9; R_b = primer paso con S_rec <= 0,9 o paso fallido. Si R_b es evaluado, R_c por log-log entre R_a y R_b; si el paso falla, cota [R_b; R_a].

| L (um) | cruce S_rec = 0,9 | R_c o cota |
|---|---|---|
| 40 | entre 7 y 5 mm (paso de 5 mm fallido) | cota [5; 7] mm |
| 80 | entre 10 y 7 mm (paso de 7 mm evaluado, S_rec = 0,890689) | 7,32 mm (interpolado; informativo, no evaluado en el criterio) |
| 100 | entre 10 y 7 mm (paso de 7 mm fallido, S_prev = 0,690) | cota [7; 10] mm, pass de I4.2 |

Convergencia en L para R >= R_a = 10 mm (regla I4.2 ii): |n(100) - n(80)| = 0 a 50 mm; 8,2e-13 a 20 mm; 1,2e-8 a 10 mm (umbral 1e-6). S_rec > 0,9 en ambos L para estos tres radios. Pass = true por la regla fijada.

Advertencias sobre I4.2 (no resueltas en esta ronda):

1. Esto es una cota, no un valor de R_c. Ningun paso de L = 100 cae dentro de (7; 10) mm.
2. El cruce no esta convergido en L: L = 40 da [5; 7] mm; L = 80 da 7,32 mm; L = 100 da [7; 10] mm. A 7 mm, L = 80 sigue la cadena con S_prev = 0,951 y L = 100 la pierde con S_prev = 0,690, aunque las n_eff coinciden hasta 2e-8. Esto apunta a que el modo a 7 mm se mezcla con estados de caja de forma sensible a L. Es un resultado de la cadena, no una propiedad fisica demostrada.
3. El criterio de convergencia de I4.2 comprueba Delta n para R >= R_a, pero no la posicion de R_c.

## Limites

- Estado PARTIAL: L = 80 se detiene en 5 mm y L = 100 en 7 mm. No se calcularon radios por debajo de 5 mm (L = 80) ni de 7 mm (L = 100), ni 4, 3, 2,5 o 2 mm en ningun L.
- La cadena no se refina: pasos de 10 a 7 mm son grandes para el solape (la continuacion falla con S_prev < 0,9). Un paso mas fino (por ejemplo 9, 8 mm) podria cambiar la cota; no se ejecuto.
- h = 0,125 no ejecutado. L = 60 no ejecutado en esta ronda.
- Radiacion no calculada: no hay perdida, no hay dB/cm, no hay comparacion con Lee et al. (2021). Delta n_eff no es perdida.
- La caja de Dirichlet no representa radiacion. Los estados exteriores aparecen como fallos de continuacion; no es un limite L -> infinito.
- Nada vectorial (TE/TM), ni acoplo, ni fabricacion, ni dispositivo fs, ni red 3D.

## Lo calculado frente a lo supuesto

- Calculado (codigo): todas las cifras de este documento, los pass de I4.0, I4.1 e I4.2, la perturbacion (c2, S2, <D2>), las verificaciones (a)-(c) y las cadenas de L = 40, 80 y 100.
- Calculado a mano (informativo, a partir de cifras del codigo): R_c = 7,32 mm a L = 80 por interpolacion log-log de S_rec entre 10 y 7 mm.
- Supuesto (fijado en el contrato): caja de semidimension L, n_eq = n_xy (1 + X/R), solape potencia S con umbral 0,9, pasos de la cadena, h = 0,25 um, n_modes = 12.
