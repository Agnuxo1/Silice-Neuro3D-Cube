# CONTRATO-tracks-r3: F3 (tracks con fraccion de area real y caja convergida)

Hora de escritura: 2026-10-10, 07:15 UTC (lectura de `date -u` antes de escribir este documento y antes de ejecutar ningun calculo de esta ronda). Plazo de entrega: 08:20 UTC.
Repositorio: D:/PROJECTS/.cognition/audit/silice-origin-main (rama auditoria-20261009). Carpeta: experimentos/tracks_claude/.
Naturaleza: MODELO NUMERICO ESCALAR IDEAL en CPU. No es un dispositivo, no es una medida, no es fabricacion. Ninguna cifra es un dato de laboratorio.
Predicciones y calculos se separan: las predicciones de la seccion 7 no son criterios de paso.

Base: CONTRATO-tracks-r2.md, run_tracks.py (ronda 1, modulo), run_tracks_r2.py, resultados_tracks_r2.json (solo lectura). Solver: experimentos/solver2d_claude/solver2d.py via solve_near de run_tracks.py.
Estado de la ronda 2 (hecho publico): resultados_tracks_r2.json tiene una sola corrida (i|L40|h0.25, n = 1,4421952407) y status null. La ronda 2 no completo sus bloques. Esta ronda no reutiliza sus corridas salvo la lectura de sus fracciones.

## 1. Problema (F3)

- F3.1: la camisa continua (caso i) ya no debe depender de la caja: se exige convergencia en L entre 60 y 80 um.
- F3.2: los trazos (ii_N) y la continua equivalente (iii_N) se comparan en la misma caja L = 80 um, con la fraccion de area REAL medida (no f = N/48).
- F3.3: la separacion Delta(N) = n_eff(trazos) - n_eff(continua equivalente) frente a N.

Hipotesis (no criterios): en la ronda 2 la fraccion real satura en 0,497 (N = 96), no crece hasta 2 como suponia f = N/48. El diseno f = N/48 queda descartado.

## 2. Geometria, caja y malla (fijadas ahora, sin cambios de la ronda 1 y 2)

- a = 6 um (nucleo), t = 6 um (camisa 6 < r < 12), radio medio 9 um, r_t = 1,5 um.
- n_nucleo = n_fondo = 1,444. n_camisa = 1,439 (caso i y trazos). lam = 1,55 um. k0 = 2 pi / lam. s_sub = 8.
- Trazos: N cilindros de radio 1,5 um centrados en radio 9 um, con angulos equiespaciados (sin cambio respecto a la ronda 2).
- Caja: L = semilado, caja [-L, L]^2 (lado 2L). Solo L = 60 y L = 80 um; h = 0,25 um en todo el calculo de esta ronda. h = 0,125 a L = 80 NO se ejecuta (RAM libre 4,9 GB de 23,7 GB a 07:15 UTC; L = 80, h = 0,125 da unas 1,6 M incognitas).
- Incognitas: L = 60, h = 0,25: 229 441. L = 80, h = 0,25: 408 321.

## 3. Fraccion de area real (usada en F3.2 y F3.3)

- f_real(N) = area de union de trazos / area del anillo 6 < r < 12, medida en malla fina dx = 0,01 um (ronda 2, valores de resultados_tracks_r2.json, campo fracs.N*.f_union_grid, precision completa). Redondeados a tres decimales coinciden con la tarea: 0,167; 0,333; 0,441; 0,469; 0,487; 0,492; 0,497 (N = 8, 16, 24, 32, 48, 64, 96).
- n_eq(N)^2 = f_real(N) 1,439^2 + (1 - f_real(N)) 1,444^2. Para N = 96, f_real < 1: la formula es valida.

## 4. Metodo (fijado ahora)

- Problema: (d2/dx2 + d2/dy2 + k0^2 n^2) psi = beta^2 psi, n_eff = beta/k0, Dirichlet en la caja, promediado subpixel (s_sub = 8).
- Shift-invert en sigma = (k0 sigma)^2, sigma = 1,44219587036024 (raiz analitica del caso i de la ronda 1, resultados.json, analytic.i.Re_neff). K = 30 modos. Igual que la ronda 2.
- Modo de nucleo ligado (igual que ronda 2, sin cambio de umbrales): entre los K modos, el de mayor n_eff con P(r <= 12 um) >= 0,5 y |n_eff - sigma| <= 0,002. Si no existe, la corrida queda "no ligada" con n_core = null.
- Modo recto (interpretacion fijada ahora): modo de nucleo del caso (i), camisa continua de n = 1,439, misma caja L = 80, h = 0,25. Se llama psi_i. Los psi se normalizan con sum psi^2 h^2 = 1.
- Solape con el modo recto: S = |sum psi_N psi_i h^2|^2, con psi_N el modo de nucleo seleccionado del caso N. Umbral: S > 0,9.
- Regla de cuenta (de la tarea): un caso de trazos o de continua equivalente CUENTA solo si es modo de nucleo ligado y S > 0,9. Si no cuenta, se marca "no ligado" (n_core = null) y no entra en ningun criterio de diferencia. Se aplica la misma regla a ii_N y iii_N.
- Analitica (verificacion): Re n_an(i) = 1,44219587036 (ronda 1, G_leaky). Se usa como control de la caja, no como criterio de la tarea.
- Perdidas: no se calculan.

## 5. Criterios numericos (umbrales fijados AHORA)

Los umbrales de rondas anteriores se mantienen y se citan: 1e-6 (F21-C1 de ronda 2 y C2 de ronda 1), 1e-5 (C1 y C6 de ronda 1), 1e-4 (C3 de ronda 1 y F21-C3 de ronda 2). El umbral 1e-5 de F3.3 es el de la tarea.

Un criterio es pass = true solo si lo evalua el codigo y no falta ningun dato. Si falta un dato, evaluable = false y pass = false.

- F31-C1 (convergencia de la caja, tarea F3.1): |n(i; L=80, h=0,25) - n(i; L=60, h=0,25)| < 1e-6.
- F31-C2 (caso i ligado en las dos cajas): P >= 0,5 y |n - sigma| <= 0,002 en L = 60 y L = 80 (h = 0,25).
- F31-C3 (control analitico, umbral de la ronda 1 C3 = 1e-4): |Re n(i; L=80, h=0,25) - Re n_an(i)| <= 1e-4.
- F32-C1 (cobertura): los 14 casos ii_N y iii_N (N = 8, 16, 24, 32, 48, 64, 96), L = 80, h = 0,25, tienen resultado del solver y bandera de cuenta calculada por el codigo.
- F32-C2 (trazos que cuentan): los 7 casos ii_N cuentan (ligados y S > 0,9) en L = 80, h = 0,25.
- F32-C3 (continua equivalente que cuenta): los 7 casos iii_N cuentan en L = 80, h = 0,25.
- F33-C1 (pregunta principal de F3.3): |Delta(N)| < 1e-5 para N = 48, 64 y 96, L = 80, h = 0,25, con ambos casos contados. Pass solo si los tres pares cumplen.
- F33-C2 (pregunta principal con la fraccion real): igual que F33-C1 pero para N = 48 solo (N = 48 es el primer N con f_real cercano a 0,5 y no es el limite de f = 1).

Informativos (pass = null, sin umbral): S(N) para todo N; Delta(N) para todo N contado; pendiente de Delta frente a N para N contados; n_eff(ii_N) y n_eff(iii_N) con su bandera; P(r <= 12) del modo seleccionado; n_top8 del caso i; el resultado de L = 60 frente a L = 80 para el caso i (ya en F31-C1).

Estado: "done" solo si todos los criterios no informativos fueron evaluados. "partial" si falta alguno (por tiempo o memoria). "blocked" si el solver falla en todas las corridas.

## 6. Plan de calculo (orden)

1. Bloque F31: caso i a L = 60 y a L = 80 (h = 0,25). Se guarda psi_i de L = 80 para el solape.
2. Bloque F32, por pares (ii_N, iii_N) en el orden N = 48, 64, 96, 32, 24, 16, 8. Un proceso a la vez (RAM). Cada resultado se guarda al terminar, para reanudar.
3. Evaluacion y escritura de resultados_tracks_r3.json (pass calculados por el codigo) y RESULTADOS-tracks-r3.md.
4. Si a las 08:20 UTC no estan todos los N, se entrega parcial y se declara cuales faltan. No se extrapola ni se inventan cifras.

## 7. Predicciones (no son criterios; se escriben antes de calcular)

- P1: F31-C1 falla, es decir |n(80) - n(60)| >= 1e-6. Base: en la ronda 1 el caso i con L = 40, 50, 60 (h = 0,25) dio 1,4421952, 1,4421935 y 1,4421891, con P(r <= 12) = 0,82, 0,76, 0,54. La deriva crece con L y P baja.
- P2: S(N) < 0,9 para N = 8 (el modo de trazos con N pequeno es fuertemente acimutal, no es modo recto).
- P3: |Delta(N)| >= 1e-5 para N = 48. Base: la separacion entre trazos (distancia minima de centros 2 x 9 x sen(pi/N) = 1,18 um para N = 48) es comparable a la longitud de onda en el medio, lam / n = 1,07 um. La homogeneizacion por fraccion de area no es exacta. Es una prediccion de magnitud, no un criterio.

## 8. Lo que NO afirmo

- No afirmo nada vectorial (TE/TM), birrefringencia, contraste delta n = -0,003 frente a otra fraccion, ni perdidas.
- No afirmo convergencia en h a L = 80 (h = 0,125 no se ejecuta). No afirmo convergencia mas alla de L = 80.
- No afirmo fabricacion, escritura fs, rugosidad ni ninguna medida.
- No afirmo que el modo de la caja sea lo que produce un laser.
- No copio ni consulto codigo de src/silice/, tests/ ni scripts/. No toco coordinacion/ ni Docs/. No hago git add, commit ni push. Salidas solo en experimentos/tracks_claude/, y temporales en D:.

## 9. Entregables

- experimentos/tracks_claude/CONTRATO-tracks-r3.md (este documento; no se modifican umbrales despues de calcular).
- experimentos/tracks_claude/run_tracks_r3.py (usa run_tracks.py como modulo; no modifica sus archivos).
- experimentos/tracks_claude/resultados_tracks_r3.json (pass calculados por el codigo).
- experimentos/tracks_claude/log_run_r3.txt.
- experimentos/tracks_claude/RESULTADOS-tracks-r3.md (tablas generadas por el script y notas de estado).

## 10. Consulta a JEV (registro)

- Se intento `router.py jev` con cuatro preguntas agrupadas (interpretacion del modo recto, paralelismo y orden, parametros, limite de tiempo). La consulta devolvio `stage: local_schema` (error de esquema local) y `remote_decision: false`. No hay provenance=jev para esta ronda.
- Fallback local explicito: las cuatro decisiones se toman con la regla de este contrato. Ejecucion secuencial por RAM. Plan del router `router.py plan` (provenance del plan: remoto, ejecutor main_agent, sin paralelismo, sin segunda opinion) sigue como orientacion.
