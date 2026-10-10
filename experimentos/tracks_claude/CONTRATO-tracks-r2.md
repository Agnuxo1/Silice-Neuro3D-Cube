# CONTRATO-tracks-r2: F2 (camisa continua frente a trazos, ronda 2)

Hora de escritura: 2026-10-10, entre 04:55 y 04:57 UTC (lectura del reloj del sistema en 04:56:55, con el contrato ya escrito y antes de ejecutar ningun calculo de esta ronda). Plazo de entrega: 06:00 UTC.
Repositorio: D:/PROJECTS/.cognition/audit/silice-origin-main (rama auditoria-20261009). Carpeta: experimentos/tracks_claude/.
Naturaleza: MODELO NUMERICO ESCALAR IDEAL. No es un dispositivo, no es una medida, no es fabricacion. Ninguna cifra es un dato de laboratorio.
Predicciones y medidas se separan: las predicciones de la seccion 7 se escriben antes de calcular y no son criterios de paso.

Base: CONTRATO-camisa-trazos.md (ronda 1), run_tracks.py, resultados.json (no se modifican). Solver: experimentos/solver2d_claude/solver2d.py (Tarea A), via run_tracks.py (misma geometria, misma referencia analitica).

## 1. Problema que se ataca (F2)

La ronda 1 evaluo el modo de nucleo en caja sin comprobar si estaba ligado. V4 lo refuto: con fondo n_bg = 1,444 y trinchera 1,439, el modo (n_eff 1,44219) es cuasi-ligado con fuga (Im 1,3e-5 en la raiz analitica). Un solver de caja da un valor que depende de L.

Hipotesis de esta ronda:
- HF2.1: el valor de caja de la camisa continua (i) depende de L (no converge con el tamano de caja al nivel de 1e-6 en L = 40, 60, 80).
- HF2.2: el modo de nucleo de los casos de trazos (ii) no esta ligado (P(r<=12) < 0,5) en las cajas usadas, o lo esta solo en algunos N.
- HF2.3: n_ii(N) - n_iii(N) es no nulo para N >= 48, y su signo y magnitud cambian con N.

## 2. Convencion de caja y malla (fijada ahora)

- Solver: x_i = (i - (N-1)/2) h, N = 2 round(L/h) + 1. L es el SEMILADO: caja [-L, L]^2 con lado 2L (como en la Enmienda 1 de la ronda 1). Por tanto L = 40, 60, 80 um corresponden a lados 80, 120, 160 um.
- Geometria, indices y casos: identicos a la ronda 1 (a = 6, t = 6, r_t = 1,5, radio medio 9; n_core = n_bg = 1,444; n_camisa = 1,439; lam = 1,55 um; s_sub = 8).
- Casos: i (anillo 6 < r < 12, n = 1,439); ii_N (N trazos, N en {8, 16, 24, 32, 48, 64, 96}); iii_N (anillo con n_eq(N) = sqrt(f 1,439^2 + (1 - f) 1,444^2), f = N/48). Para N = 48, f = 1 y n_eq = 1,439, por tanto iii_48 = i exactamente. Para N = 64 y 96, f > 1: se calcula igual y se marca como no interpretable fisicamente.

## 3. Plan de calculo (bloques)

- Bloque A (F2.1, caja de tamano): caso i con L = 40, 60, 80 a h = 0,25; y caso i con L = 40 a h = 0,125 (comprobacion de h).
  - Motivo del h: L = 80 con h = 0,125 da ~1,6 M incognitas. En torno a las 04:53 UTC la RAM libre era de 3,9 GB de 23,7 GB. No se ejecuta. Tampoco L = 60 con h = 0,125 (919 k incognitas), por la misma razon. Se declara como no ejecutado.
- Bloque B (F2.2, caja primaria): L = 40, h = 0,25 (101 761 incognitas), casos i, ii_N, iii_N.
- Bloque C (F2.2, caja secundaria): L = 60, h = 0,25 (229 441 incognitas), mismos casos.
- Bloque D (comprobacion de h en trazos): L = 40, h = 0,125, casos ii_8 y ii_48.
- Bloque E (opcional, solo si hay tiempo): L = 80, h = 0,25, mismos casos que B. Si se ejecuta, sus criterios F22-C7 y F23-C3 entran en la evaluacion. Si no se ejecuta, no son criterios.
- Motivo de no usar una caja "convergida" fija: F2.1 puede no converger (ver F21-C1). Si F21-C1 falla, no hay caja convergida. Entonces las comparaciones (ii) frente a (iii) se hacen en la misma caja (B y C), y la dependencia con L se reporta.

## 4. Metodo (cambios respecto a la ronda 1, fijados ahora)

- Problema de autovalores: (d2/dx2 + d2/dy2 + k0^2 n^2) psi = beta^2 psi, n_eff = beta/k0, Dirichlet en el contorno, promediado subpixel (ronda 1 y solver).
- Shift-invert en sigma = (k0 sigma_i)^2, con sigma_i = 1,44219587036 (raiz analitica del caso i, ronda 1). Se piden K = 30 modos (ronda 1 uso K = 12 con L = 40). Motivo: en la ronda 1, con K = 12, ningun caso de trazos ni iii_8 a iii_32 encontraron un modo con P >= 0,5. La ventana de 12 modos cae dentro del continuo de modos del exterior (fondo 1,444).
- Modo de nucleo ligado: el modo de mayor n_eff entre los K modos que cumple P(r <= 12) >= 0,5 y |n_eff - sigma_i| <= 0,002. Si no hay ninguno, el caso se marca "no ligado" y n_core = null. Esto es la marca pedida en la tarea.
- Diagnostico sin umbral: el modo de mayor P(r <= 12) entre los K modos, con su n_eff y P.
- Analitica: misma funcion G = det F (ronda 1), con raices de los casos i, iii_N. Se usa Re n_an(i) como referencia de C-analitica.
- Perdida: NO se calcula perdida de trazos. Im(n_eff) analitico del caso i se reporta solo como dato de la referencia.
- Area de union de trazos: malla fina dx = 0,01 (ronda 1), con f_union(N) frente a f(N) = N/48.

## 5. Criterios numericos (umbrales fijados AHORA)

Los umbrales de la ronda 1 se mantienen y se citan: 1e-5 (C1, C6 de la ronda 1), 1e-6 (C2 de la ronda 1), 1e-4 (C3 de la ronda 1), 1e-6 y 0,5 % (C5 de la ronda 1). Un criterio es pass = true solo si lo evalua el codigo y no hay falta de datos. Si falta un dato, evaluable = false y pass = false.

- F21-C1 (convergencia de caja, criterio de la tarea): |n(L=80, h=0,25) - n(L=60, h=0,25)| < 1e-6, caso i.
- F21-C2 (modo ligado en las tres cajas): caso i ligado (P >= 0,5 y |n - sigma| <= 0,002) en L = 40, 60 y 80 a h = 0,25.
- F21-C3 (analitica): |Re n(i; L = 40, h = 0,125) - Re n_an(i)| <= 1e-4.
- F21-C4 (malla en h, caso i): |n(i; L = 40, h = 0,25) - n(i; L = 40, h = 0,125)| <= 1e-5.
- F22-C1 (marca completa, caja 40): los 15 casos (i, ii_N, iii_N) a L = 40, h = 0,25 tienen resultado del solver y bandera de ligado calculada por el codigo.
- F22-C2 (trazos ligados, caja 40): los 7 casos ii_N ligados en L = 40, h = 0,25.
- F22-C3 (continua equivalente ligada, caja 40): los 7 casos iii_N ligados en L = 40, h = 0,25.
- F22-C4 (malla en h, trazos): |n(ii_N; L = 40, h = 0,25) - n(ii_N; L = 40, h = 0,125)| <= 1e-5 para N = 8 y N = 48, si ambos estan ligados.
- F22-C5 (marca completa, caja 60): igual que F22-C1 a L = 60.
- F22-C6 (trazos ligados, caja 60): igual que F22-C2 a L = 60.
- F23-C1 (pregunta principal, umbral de la ronda 1 C6): |n_ii(N) - n_iii(N)| < 1e-5 para N = 48, 64, 96 en L = 40, h = 0,25, si ambos estan ligados. Para N = 64 y 96, el valor se marca como interpretacion no valida (f > 1).
- F23-C2 (la misma comprobacion en la caja 60): |n_ii(N) - n_iii(N)| < 1e-5 para N = 48, 64, 96 en L = 60.
- F23-G1 (geometria, exacta sin solapes): |f_union(N) - f(N)| <= 1e-6 para N = 8 y 16.
- F23-G2 (estimador de malla): error relativo <= 0,5 % en N = 16.
- F23-C3 (solo si se ejecuta el bloque E): |n_ii(N) - n_iii(N)| < 1e-5 para N = 48, 64, 96 en L = 80.
- Sin umbral (informativo, pass = null): Delta(N) = n_ii(N) - n_iii(N) para todo N y ambas cajas; pendiente de Delta frente a N; f_union(N) frente a f(N); n_eq'(N) con f_union (diagnostico); modo de mayor P entre los K; n_top8; n_eff de F2.1 frente a L.

## 6. Estado y reglas de publicacion

- Se publican todos los casos, incluidos los que fallen, con sus cifras, y la bandera de ligado de cada uno.
- "done" solo si todos los criterios (no informativos) se evaluaron. "partial" si falta alguno (por ejemplo por tiempo o por memoria). "blocked" si el solver no funciona.
- Si un caso no esta ligado, su n_core es null y no se usa en ningun criterio de diferencia.

## 7. Predicciones (no son criterios; se escriben antes de calcular)

- P1: F21-C1 falla, es decir |n(80) - n(60)| >= 1e-6 a h = 0,25. Base: en la ronda 1, n(L = 40, 50, 60; h = 0,25) = 1,4421952, 1,4421935, 1,4421891, con P(r <= 12) = 0,82, 0,76, 0,54. P(r<=12) baja con L.
- P2: en la caja 40, algun caso de trazos con N >= 48 no esta ligado (P < 0,5), dado que en la ronda 1 con K = 12 ninguno lo estaba.
- P3: |n_ii(48) - n_iii(48)| = |n_ii(48) - n_i| >= 1e-4. Base: f_union(48) = 0,487, mientras la formula da f = 1. Esta prediccion es de magnitud, no un criterio.

## 8. Lo que NO afirmo

- No afirmo nada vectorial (TE/TM), ni contraste delta n = -0,003, ni birrefringencia.
- No afirmo que la camisa continua ideal sea equivalente a la discreta. El contraste mide cuanto se separan.
- No afirmo fabricacion, escritura fs, rugosidad, perdidas por cm ni ninguna medida. No calculo perdida de trazos.
- No afirmo convergencia mas alla de L = 80 (si se ejecuta) ni de N = 96. No afirmo el valor infinito de la caja.
- No afirmo que el modo de la caja sea lo que produce un laser. Es un resultado de modelo.
- No copio ni consulto codigo de src/silice/, tests/ ni scripts/. No toco coordinacion/ ni Docs/. No hago git add, commit ni push. Salidas solo en esta carpeta, en D:.

## 9. Entregables

- experimentos/tracks_claude/CONTRATO-tracks-r2.md (este documento, sin modificar umbrales despues de calcular).
- experimentos/tracks_claude/run_tracks_r2.py (usa run_tracks.py de la ronda 1 como modulo para geometria, solver y analitica; no modifica sus archivos).
- experimentos/tracks_claude/resultados_tracks_r2.json (pass calculado por el codigo).
- experimentos/tracks_claude/log_run_r2.txt.
- No se escribe un informe .md de resultados: el resultado va en resultados_tracks_r2.json y en la respuesta final.

## 10. Verificacion previa

- Referencia analitica del caso i (C-analitica), reproducida con la misma funcion de la ronda 1 (raiz 1,44219587 + i 1,30e-5).
- Convergencia en h del caso i (F21-C4) con L = 40.
- Los criterios F21-C1 y F21-C2 son la verificacion de caja; F23-G1 y F23-G2 son la verificacion geometrica.
