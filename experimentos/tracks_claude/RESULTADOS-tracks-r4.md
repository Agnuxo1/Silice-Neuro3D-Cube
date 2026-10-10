# RESULTADOS tracks ronda 4 (F4: convergencia de caja, caso i)

Modelo numerico escalar ideal. No es dispositivo, medida ni fabricacion. Contrato: `CONTRATO-tracks-r4.md`. Pass calculado por `run_tracks_r4.py eval`.

Estado: **partial**. Corridas: 6, con n_eff: 4, ligadas: 4. Criterios evaluados: 4/6, pass: 2.

## Corridas (caso i, camisa continua n = 1,439; fondo y nucleo n = 1,444; lam = 1,55 um; s_sub = 8)

| caso | h (um) | L (um) | K | incognitas | n_eff seleccionado | P(r<=12) | ligado | Delta n frente a L anterior (mismo h, K=30) | t (s) |
|---|---|---|---|---|---|---|---|---|---|
| i | 0.25 | 60 | 30 | 229441 | 1.4421891015 | 0.5385 | si |  | 46.52 |
| i | 0.25 | 80 | 30 | 408321 | 1.4421908377 | 0.5902 | si | +1.736e-06 | 111.01 |
| i | 0.25 | 100 | 30 | 638401 | null | null | no |  | 174.63 |
| i | 0.25 | 120 | 30 | 919681 | 1.4421895179 | 0.7286 | si |  | 160.56 |
| i | 0.25 | 60 | 60 | 229441 | 1.4421891015 | 0.5385 | si |  | 69.26 |
| i | 0.25 | 100 | 60 | 638401 | null | null | no |  | 179.1 |

## Sucesion n_eff(L) con h = 0,25 y K = 30

| L (um) | n_eff | Delta n frente a L anterior | P(r<=12) |
|---|---|---|---|
| 60 | 1.4421891015 |  | 0.5385 |
| 80 | 1.4421908377 | +1.736e-06 | 0.5902 |
| 100 | null |  | null |
| 120 | 1.4421895179 |  | 0.7286 |

## Diagnostico de seleccion (datos guardados por corrida, sin recalcular)

| corrida | max P(r<=12) entre los K modos | indice del max | n del modo mas cercano a sigma | P de ese modo |
|---|---|---|---|---|
| i|L60|h0.25|K30 | 0.5385 | 15 | 1.4423690895 (indice 6 entre los 8 primeros) | 0.0012 |
| i|L80|h0.25|K30 | 0.5902 | 16 | 1.4422863209 (indice 7 entre los 8 primeros) | 0.0002 |
| i|L100|h0.25|K30 | 0.4332 | 13 | 1.4422409640 (indice 7 entre los 8 primeros) | 0.0103 |
| i|L120|h0.25|K30 | 0.7286 | 19 | 1.4422397804 (indice 6 entre los 8 primeros) | 0.0005 |
| i|L60|h0.25|K60 | 0.5385 | 29 | 1.4426326977 (indice 6 entre los 8 primeros) | 0.0030 |
| i|L100|h0.25|K60 | 0.4332 | 30 | 1.4423613305 (indice 6 entre los 8 primeros) | 0.0004 |

## Criterios (pass calculado por el codigo)

| id | descripcion | pass | evaluable | valor |
|---|---|---|---|---|
| F4-C1 | |n(i;L=120)-n(i;L=100)| < 1e-6 (h=0,25) | False | False | `null` |
| F4-C2 | caso i ligado (P>=0,5 y |n-sigma|<=0,002) en L=60,80,100,120 (h=0,25) | False | True | `{"60": {"ligado": true, "P_in_sel": 0.538498356727384, "n_core": 1.442189101534691}, "80": {"ligado": true, "P_in_sel": 0.5901808393266028, "n_core": 1.4421908377412704}, "100": {"ligado": false, "P_in_sel": null, "n_core": null}, "120": {"ligado": true, "P_in_sel": 0.7285695125494775, "n_core": ...` |
| F4-C3 | |Re n(i;L=120,h=0,25) - Re n_an(i)| <= 1e-4 | True | True | `-6.352433972400817e-06` |
| F4-C4 | malla: n(h=0,2)-n(h=0,25) por L (informativo, sin umbral de paso) | None | True | `{"60": {"n_h025": 1.442189101534691, "n_h02": null, "delta": null, "nota": "h=0,2 no calculada"}, "80": {"n_h025": 1.4421908377412704, "n_h02": null, "delta": null, "nota": "h=0,2 no calculada"}, "100": {"n_h025": null, "n_h02": null, "delta": null, "nota": "h=0,2 no calculada"}, "120": {"n_h025"...` |
| F4-C5 | L=60,h=0,25: |n(K=60)-n(K=30)| < 1e-9 | True | True | `0.0` |
| F4-C6 | trazos (no aplicable: F4-C1 no pasa, F4(d) no se ejecuta) | None | False | `null` |

## Notas de estado (fijadas antes de calcular o de origen declarado)

- Lo calculado: n_eff, P(r<=12), las diferencias de la tabla y los criterios de la tabla. Lo supuesto: sigma de la ronda 1, geometria, umbrales (contrato r4, seccion 3).
- Reproduccion: L = 60, h = 0,25, K = 30 da n_eff = 1,442189101534691, igual que la ronda 1 (K = 60). El modo seleccionado tiene otro indice (15 frente a 5) con el mismo n_eff.
- Informativo (no es F4-C1, porque L = 100 no tiene modo ligado): n(L=120) - n(L=80) = -1.3198e-06 (h = 0,25, K = 30). Este par no se usa como criterio de convergencia.
- L = 100, K = 30: ningun modo de los 30 mas cercanos a sigma alcanza P(r<=12) >= 0,5; el maximo es 0,4332 (indice 13). Con la regla del contrato, la corrida queda 'no ligada' y n_core = null. F4-C1 no se puede evaluar: falta el L = 100 en el protocolo fijado.
- Diagnostico K = 60 en L = 100: fila 'L100|h0.25|K60' de la tabla de corridas, si existe. Es una desviacion de protocolo declarada (mas modos), solo informativa; no sustituye a F4-C1.
- Trazos (F4(d)): no ejecutados. F4-C1 no pasa ni se puede evaluar, asi que el limite de caja queda declarado y no se siguen los trazos.
- No afirmo vectorial, perdidas, fabricacion ni convergencia mas alla de L = 120 um.

