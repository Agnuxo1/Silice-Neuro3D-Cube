# RESULTADOS tracks ronda 3 (F3)

Modelo numerico escalar ideal. No es dispositivo, medida ni fabricacion. Contrato: `CONTRATO-tracks-r3.md`. Pass calculado por `run_tracks_r3.py eval`.

Estado: **blocked**. Corridas ok: 0, con error: 0, que cuentan: 0. Criterios evaluados: 0/8, pass: 0.

## Corridas (L = 80 um salvo caso i a L = 60; h = 0,25 um)

| caso | L (um) | incognitas | ligado | S (solape con modo recto) | cuenta | n_eff | P(r<=12) | f_real | n_eq | t (s) |
|---|---|---|---|---|---|---|---|---|---|---|

## Criterios (pass calculado por el codigo)

| id | descripcion | pass | evaluable | valor |
|---|---|---|---|---|
| F31-C1 | |n(i;L=80)-n(i;L=60)| < 1e-6 (h=0,25) | false | false | `null` |
| F31-C2 | caso i ligado (P>=0,5 y |n-sigma|<=0,002) en L=60 y L=80 (h=0,25) | false | false | `{"60.0": null, "80.0": null}` |
| F31-C3 | |Re n(i;L=80,h=0,25) - Re n_an(i)| <= 1e-4 | false | false | `null` |
| F32-C1 | 14 casos (ii_N, iii_N) con resultado del solver, L=80, h=0,25 | false | false | `{"faltan_o_fallan": ["ii_N8|L80|h0.25", "ii_N16|L80|h0.25", "ii_N24|L80|h0.25", "ii_N32|L80|h0.25", "ii_N48|L80|h0.25", "ii_N64|L80|h0.25", "ii_N96|L80|h0.25", "iii_N8|L80|h0.25", "iii_N16|L80|h0.25", "iii_N24|L80|h0.25", "iii_N32|L80|h0.25", "iii_N48|L80|h0.25", "iii_N64|L80|h0.25", "iii_N96|L80|h0.25"]}` |
| F32-C2 | 7 trazos ii_N cuentan (ligados y S>0,9), L=80, h=0,25 | false | false | `{"8": false, "16": false, "24": false, "32": false, "48": false, "64": false, "96": false}` |
| F32-C3 | 7 continuas equivalentes iii_N cuentan (ligadas y S>0,9), L=80, h=0,25 | false | false | `{"8": false, "16": false, "24": false, "32": false, "48": false, "64": false, "96": false}` |
| F33-C1 | |Delta(N)| < 1e-5 para N=48, 64 y 96, L=80, h=0,25 (ambos casos contados) | false | false | `{"48": {"delta": null, "abs": null, "nota": "par no contado (no ligado o S<=0,9)"}, "64": {"delta": null, "abs": null, "nota": "par no contado (no ligado o S<=0,9)"}, "96": {"delta": null, "abs": null, "nota": "par no contado (no ligado o S<=0,9)"}}` |
| F33-C2 | |Delta(48)| < 1e-5, L=80, h=0,25 | false | false | `null` |
| INF-solape | S = |<psi_N, psi_i>|^2 y cuenta por caso (informativo) | null (informativo) | true | `{}` |
| INF-delta | Delta(N) frente a N y pendiente sobre pares contados (informativo) | null (informativo) | true | `{"filas": {"8": {"n_ii": null, "n_iii": null, "delta": null}, "16": {"n_ii": null, "n_iii": null, "delta": null}, "24": {"n_ii": null, "n_iii": null, "delta": null}, "32": {"n_ii": null, "n_iii": null, "delta": null}, "48": {"n_ii": null, "n_iii": null, "delta": null}, "64": {"n_ii": null, "n_iii": null, "delta": null}, "96": {"n_ii": null, "n_iii": null, "delta": null}}, "pendiente_delta_por_N": ...` |
| INF-caja | caso i: n y P(r<=12) frente a L (informativo) | null (informativo) | true | `{}` |

## Limites y estado (fijados antes de calcular)

- Solo CPU, un proceso a la vez, un hilo (OMP_NUM_THREADS=1). RAM libre 4,9 GB de 23,7 GB a 07:15 UTC.
- h = 0,125 a L = 80 no se ejecuta (1,6 M incognitas no caben con la RAM disponible). No hay convergencia en h a L = 80.
- La ronda 2 no completo sus bloques (un solo resultado, status null). Esta ronda no reutiliza sus corridas.
- Fracciones f_real: area de union medida en malla fina (ronda 2). No es f = N/48 (descartado).
- Modo recto: modo de nucleo del caso i a L = 80, h = 0,25 (interpretacion fijada en el contrato, seccion 4).
- JEV: la consulta devolvio error de esquema local (`remote_decision` false). Decisiones con fallback local explicito (contrato, seccion 10).
- Lo calculado: n_eff, P, S y las diferencias de la tabla. Lo supuesto: sigma de la ronda 1, modo recto, f_real, geometria, umbrales.
- No afirmo vectorial, perdidas, fabricacion ni convergencia mas alla de L = 80.
