# CONTRATO-tracks-r4: F4 (convergencia de caja de la camisa continua, caso i)

Hora de escritura: 2026-10-10, 10:02 UTC (lectura de `date -u` antes de escribir este documento y antes de ejecutar ningun calculo de esta ronda). Hora limite de entrega: 10:30 UTC.
Repositorio: D:/PROJECTS/.cognition/audit/silice-origin-main (rama auditoria-20261009). Carpeta: experimentos/tracks_claude/.
Naturaleza: MODELO NUMERICO ESCALAR IDEAL en CPU. No es un dispositivo, no es una medida, no es fabricacion. Ninguna cifra es un dato de laboratorio.
Predicciones y calculos se separan: las predicciones de la seccion 7 no son criterios de paso.
Base: CONTRATO-tracks-r3.md y CONTRATO-tracks-r2.md (umbrales citados como tales), run_tracks.py (ronda 1, modulo), solver2d_claude/solver2d.py. Solo lectura de los archivos de rondas anteriores.

Estado de la ronda 3: sin corridas (status blocked). Esta ronda 4 reemplaza el bloque F31 de la ronda 3 con una serie de cuatro cajas en lugar de dos.

## 1. Problema (F4)

- F4(a): n_eff del caso (i), camisa continua n = 1,439 (r 6 a 12 um), nucleo y fondo n = 1,444, lam = 1,55 um, con L en {60, 80, 100, 120} um, h = 0,25 um. Se reporta la sucesion completa.
- F4(b): efecto de malla: mismo calculo con h = 0,2 um, para L en {60, 80} (y L = 100, 120 solo si el tiempo y la RAM lo permiten; si no, se declara).
- F4(c): criterio de convergencia de caja: |Delta n| < 1e-6 entre las dos ultimas L (L = 100 y L = 120, h = 0,25).
- F4(d): trazos N en {8, 16, 24, 32, 48, 64, 96} y continua equivalente, SOLO si F4(c) pasa. Si no pasa, no se ejecutan. Si pasa pero no hay tiempo, se declara no ejecutado. Los criterios de trazos se fijan aqui para que no cambien despues.

Hipotesis (no criterios): en la ronda 1 la serie n(L) para el caso i fue 1,4421952 (L = 40), 1,4421935 (L = 50), 1,4421891 (L = 60, K = 60), y el verificador V8 cita 1,4421908 (L = 80). La diferencia entre L = 60 y L = 80 es 1,7e-6, que no cumple 1e-6. Esa cifra del verificador no se usa como dato: se recalcula.

## 2. Geometria, malla y metodo (fijados ahora, sin cambios de rondas 1 a 3)

- a = 6 um (nucleo), t = 6 um (camisa 6 < r < 12 um), n_nucleo = n_fondo = 1,444, n_camisa = 1,439, lam = 1,55 um, k0 = 2 pi / lam, s_sub = 8.
- Caja: L = semilado, dominio [-L, L]^2, Dirichlet psi = 0 en el contorno, Laplaciano de 5 puntos, promediado subpixel. Misma discretizacion que solve_near de run_tracks.py (ronda 1).
- Incognitas (h = 0,25): L = 60, 229 441; L = 80, 408 321; L = 100, 638 401; L = 120, 919 681. Para h = 0,2: L = 60, 358 801; L = 80, 638 401; L = 100, 999 001 (solo si cabe); L = 120, 1 437 601 (solo si cabe).
- Shift-invert en sigma = (k0 sigma)^2, sigma = 1,44219587036024 (raiz analitica del caso i, ronda 1). K = 30 modos en todas las cajas de esta ronda. (La ronda 1 uso K = 60 en L = 60; se verifica en L = 60 que K = 30 y K = 60 seleccionan el mismo modo, ver F4-C5.)
- Seleccion del modo de nucleo: primer modo, en orden de n_eff descendente, con P(r <= 12 um) >= 0,5 (select_core de run_tracks.py). Se marca ligado si ademas |n - sigma| <= 0,002. Si no se selecciona, n_core = null.
- Perdidas: no se calculan.
- Analitica (control): Re n_an(i) = 1,44219587036 (ronda 1, G_leaky). Solo control.

## 3. Criterios numericos (umbrales fijados AHORA)

Umbrales de rondas anteriores que se citan: 1e-6 (F31-C1 de la ronda 3, F21-C1 de la ronda 2, C2 de la ronda 1), 1e-4 (C3 de la ronda 1, F31-C3 de la ronda 3), 1e-5 (C1 y C6 de la ronda 1, F33-C1 de la ronda 3), 0,002 y 0,5 (ventana y umbral de potencia de la ronda 1).

Un criterio es pass = true solo si lo evalua el codigo y no falta ningun dato. Si falta un dato, evaluable = false y pass = false.

- F4-C1 (criterio de convergencia de caja, tarea (c)): |n(i; L = 120, h = 0,25) - n(i; L = 100, h = 0,25)| < 1e-6.
- F4-C2 (caso i ligado en las cuatro cajas, h = 0,25): para L = 60, 80, 100, 120, P(r <= 12) >= 0,5 y |n - sigma| <= 0,002.
- F4-C3 (control analitico, umbral 1e-4): |Re n(i; L = 120, h = 0,25) - Re n_an(i)| <= 1e-4.
- F4-C4 (malla): informativo, pass = null, sin umbral de paso. Se reporta |n(h = 0,2) - n(h = 0,25)| para cada L calculada con h = 0,2. Propuesta de protocolo (no criterio): 1e-5 como tolerancia de malla, que se evaluara en una ronda posterior.
- F4-C5 (independencia de K): en L = 60, h = 0,25, el modo seleccionado con K = 30 y con K = 60 tiene |Delta n| < 1e-9. Umbral fijado ahora.
- F4-C6 (trazos, solo si F4-C1 pasa y se ejecutan): |Delta(N)| < 1e-5 para N = 48, 64, 96 en la caja convergida, con ambos casos ligados y S > 0,9 (solape con el modo recto). Umbral del contrato r3 (F33-C1) y de la tarea.

Estado: "done" solo si F4-C1 a F4-C5 fueron evaluados y, si F4-C1 paso, F4(d) se ejecuto. "partial" si falta algun bloque (por tiempo o memoria). "blocked" si el solver falla en todas las corridas.

## 4. Plan de calculo (orden)

1. Caso i, h = 0,25: L = 60, 80, 100, 120 (un proceso a la vez, RAM libre ~6 GB a 10:00 UTC).
2. F4-C5: caso i, L = 60, h = 0,25, con K = 60.
3. Caso i, h = 0,2: L = 60, 80 (y 100, 120 si el tiempo y la RAM permiten).
4. Evaluacion por codigo, escritura de resultados_tracks_r4.json y RESULTADOS-tracks-r4.md.
5. Si F4-C1 pasa y hay tiempo: F4(d). Si no, no se ejecuta.
6. Si a las 10:30 UTC faltan bloques, se entrega parcial y se declara cuales faltan. No se extrapola ni se inventan cifras.
7. Si una corrida tarda mas de 10 minutos, se reduce la malla o el paso y se dice.

## 5. Predicciones (no son criterios; se escriben antes de calcular)

- P1: F4-C1 pasa o falla de forma marginal. Base: la diferencia entre L = 60 y L = 80 en la ronda 1 fue 1,7e-6 (sin K comparable). La convergencia en L se espera del orden de 1e-6 a 1e-7 entre L = 100 y L = 120.
- P2: F4-C2 pasa en las cuatro cajas, porque P(r <= 12) del caso i decrece con L en la ronda 1 (0,82, 0,76, 0,54 para L = 40, 50, 60) y puede caer por debajo de 0,5 en L >= 80. Si cae, F4-C2 falla en esa caja.
- P3: F4-C5 pasa (la seleccion no depende de K en L = 60).

## 6. Lo que NO afirmo

- No afirmo nada vectorial (TE/TM), birrefringencia, contraste delta n = -0,005 frente a otra fraccion, ni perdidas.
- No afirmo convergencia en h mas alla de lo que se reporte en F4-C4 (sin umbral de paso).
- No afirmo fabricacion, escritura fs, rugosidad ni ninguna medida.
- No afirmo que el modo de la caja sea lo que produce un laser.
- No copio ni consulto codigo de src/silice/, tests/ ni scripts/. No toco coordinacion/ ni Docs/. No hago git add, commit ni push. Salidas solo en experimentos/tracks_claude/, temporales en D:.

## 7. Entregables

- experimentos/tracks_claude/CONTRATO-tracks-r4.md (este documento; no se modifican umbrales despues de calcular).
- experimentos/tracks_claude/run_tracks_r4.py (usa run_tracks.py como modulo; no modifica sus archivos).
- experimentos/tracks_claude/resultados_tracks_r4.json (pass calculados por el codigo).
- experimentos/tracks_claude/log_run_r4.txt.
- experimentos/tracks_claude/RESULTADOS-tracks-r4.md.

## 8. Consulta a JEV (registro)

- Esta ronda se ejecuta como subagente del flujo de trabajo. No se ha ejecutado una consulta a `router.py jev` con provenance=jev en esta ronda: las decisiones de metodo (K = 30, seleccion, criterios, orden de cajas) se toman con las reglas de este contrato y se declaran como decision local.
