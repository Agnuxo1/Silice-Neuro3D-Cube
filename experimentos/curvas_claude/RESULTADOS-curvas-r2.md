# RESULTADOS curvas ronda 2 (Tarea I2): convergencia de dominio

MODELO NUMERICO. No es un dispositivo ni una medida. Ninguna cifra es dato de laboratorio. Perdida por radiacion y dB/cm NO calculadas.

Contrato: `CONTRATO-curvas-r2.md` (escrito antes del calculo, umbrales fijados). Codigo: `curvas_r2.py`. Salidas: `resultados_curvas_r2.json` (pass calculado por el codigo), `log_curvas_r2.txt`.

Estado del calculo de criterios: **parcial**. La ejecucion se hizo en dos procesos por limite de RAM libre: proceso 1 para L = 40, 60 y 80 (detenido al iniciar L = 100, que quedo duplicado) y proceso 2 para L = 100; el parametro y el codigo son los mismos. La malla h = 0,125 no se ejecuto (ver limites).

## Correcciones y hallazgos previos

- solver2d usa dominio [-L, +L] (L es la semidimension). El contrato de la ronda 1 decia +-20 um para L = 40; el codigo usa +-40 um.
- Ronda 1 con n_modes = 12 no encontraba el modo nucleo a R = 5 mm (S = 0). El barrido de radio critico de la ronda 1 para R < 7,5 mm no es valido.
- Ronda 1, R = 10 mm, h = 0,5: n_eff 1,442267 (L = 40) frente a 1,448733 (L = 80). El valor de L = 80 es un modo espurio de caja en la region exterior permitida.

## Verificacion del metodo (I2.0)

Recto LP01 frente a la analitica de Snyder-Love, h = 0,25:

| L (um) | n_eff recto | error vs analitica |
|---|---|---|
| 40 | 1.442191871838 | -2.936e-07 |
| 60 | 1.442191871838 | -2.936e-07 |
| 80 | 1.442191871838 | -2.936e-07 |
| 100 | 1.442191871838 | -2.936e-07 |

Analitica: n_eff = 1.442192165457. I2.0 PASS (max |error| = 2.936e-07; max error de normalizacion = 2.220e-16).

## Convergencia de dominio (I2.1), h = 0,25

| R (mm) | n_eff L=40 | n_eff L=60 | n_eff L=80 | n_eff L=100 | abs(n100 - n80) | S (L=80) | S (L=100) | I2.1 (R) |
|---|---|---|---|---|---|---|---|---|
| 10 | 1.442266248115 | 1.442266188956 | 1.446320995419 | 1.449204697052 | 2.884e-03 | 0.000000 | 0.000000 | FAIL |
| 20 | 1.442210322525 | 1.442210322531 | 1.442210322528 | 1.443552572192 | 1.342e-03 | 0.992406 | 0.000000 | FAIL |
| 50 | 1.442194819527 | 1.442194819527 | 1.442194819527 | 1.442194819527 | 0.000e+00 | 0.998787 | 0.998787 | PASS |

I2.1 global: **FAIL**. Criterio: |n(L=100) - n(L=80)| < 1e-6 con S > 0,90.

Diferencias informativas entre pares consecutivos (n_eff(Li) - n_eff(Lj)):

| R (mm) | 40-60 | 60-80 | 80-100 |
|---|---|---|---|
| 10 | +5.916e-08 | -4.055e-03 | -2.884e-03 |
| 20 | -5.829e-12 | +3.033e-12 | -1.342e-03 |
| 50 | -8.216e-15 | +0.000e+00 | +0.000e+00 |

## Identificacion del modo nucleo (I2.2)

| R (mm) | L (um) | indice del modo | S | corte espectral | n_eff | <x> (um) | P_out | P_core |
|---|---|---|---|---|---|---|---|---|
| 10 | 40 | 4 | 0.968946 | no | 1.442266248115 | +1.0479 | 9.931e-05 | 0.8707 |
| 10 | 60 | 39 | 0.968505 | si | 1.442266188956 | +1.0681 | 6.869e-04 | 0.8704 |
| 10 | 80 | 28 | 0.000000 | no | 1.446320995419 | +60.6235 | 9.123e-01 | 0.0000 |
| 10 | 100 | 35 | 0.000000 | no | 1.449204697052 | +80.6363 | 9.130e-01 | 0.0000 |
| 20 | 40 | 0 | 0.992406 | no | 1.442210322525 | +0.5123 | 0.000e+00 | 0.8837 |
| 20 | 60 | 0 | 0.992406 | no | 1.442210322531 | +0.5123 | 1.234e-07 | 0.8837 |
| 20 | 80 | 21 | 0.992406 | no | 1.442210322528 | +0.5123 | 6.107e-09 | 0.8837 |
| 20 | 100 | 28 | 0.000000 | no | 1.443552572192 | +75.5660 | 9.098e-01 | 0.0000 |
| 50 | 40 | 0 | 0.998787 | no | 1.442194819527 | +0.2043 | 0.000e+00 | 0.8870 |
| 50 | 60 | 0 | 0.998787 | no | 1.442194819527 | +0.2043 | 0.000e+00 | 0.8870 |
| 50 | 80 | 0 | 0.998787 | no | 1.442194819527 | +0.2043 | 0.000e+00 | 0.8870 |
| 50 | 100 | 0 | 0.998787 | no | 1.442194819527 | +0.2043 | 0.000e+00 | 0.8870 |

I2.2 FAIL (S_min = 0.000000; fallos publicados: 4).

## Tendencia con incertidumbre de dominio (I2.3)

No evaluado: I2.1 no converge para R = 10 mm (condicion del contrato).

## Radio critico (I2.4)

No evaluado en esta ronda. Decision JEV Q4 (opcion C, provenance = jev, confianza 0,89). Los umbrales de la ronda 1 (C7) quedan citados, no evaluados.

## Informativo (fuera de criterios)

Malla h = 0,125 a L = 40 y 60 (solo comprobacion de malla):

No ejecutado: no hubo tiempo de calculo dentro del plazo (pendiente para una ronda siguiente).

## Comprobacion informativa de corte espectral (fuera de criterios)

R = 10 mm, L = 80 um, h = 0,25, con n_modes = 80 (en vez de 40). Solo para diagnosticar la identificacion del nucleo; no sustituye a I2.1 ni a I2.2.

- n_modes = 80: el modo seleccionado (indice 66) tiene S = 0.000000 y n_eff = 1.444483422528; el indice no tiene sentido fisico porque S = 0. El nucleo no aparece entre los 80 modos.
- Maximo de S en los 80 modos: 0.000000. Con n_modes = 40 tampoco aparecia (S = 0).
- LP01 recto a L = 80: n_eff = 1.442191871838 (error vs analitica -2.936e-07).

## Lo que no se afirma

- No hay perdida por radiacion ni dB/cm. n_eff no es perdida.
- El modelo de caja Dirichlet no representa radiacion. Los estados espurios exteriores se publican, no se eliminan.
- Convergencia solo para el par L = 80-100 um (I2.1), no para L -> infinito.
- Sin radio critico (I2.4 no evaluado).
- Sin h = 0,125: no se ejecuto ni a L = 40 y 60 (informativo, pendiente) ni a L = 80 y 100 (1,6 M y 2,6 M incognitas; RAM libre ~2-4 GB).
- I2.1 no se puede establecer para R = 10 y 20 mm con n_modes = 40: el modo nucleo queda fuera de los 40 modos calculados a L = 80 y 100 (R = 10) y a L = 100 (R = 20). El valor de n_eff que aparece en esos casos es un modo espurio de caja, no el nucleo; por eso no se usan para convergencia.
- I2.3 y I2.4 no evaluados: I2.3 depende de I2.1 para R = 10 mm; I2.4 no se ejecuto por decision JEV Q4.

## Resumen de criterios (calculado por el codigo)

| criterio | evaluado | pass |
|---|---|---|
| I2.0 | si | PASS |
| I2.1 | si | FAIL |
| I2.2 | si | FAIL |
| I2.3 | no | no evaluado |
| I2.4 | no | no evaluado |

Pass: 1. Evaluados: 3 de 5.

