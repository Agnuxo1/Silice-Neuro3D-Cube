# RESULTADOS curvas ronda 3 (Tarea I3): seguimiento del modo de nucleo por continuacion en R

MODELO NUMERICO. No es un dispositivo ni una medida. Ninguna cifra es dato de laboratorio. Perdida por radiacion y dB/cm NO calculadas.

Contrato: `CONTRATO-curvas-r3.md` (escrito a las 07:17 UTC, antes del calculo; umbrales fijados). Codigo: `curvas_r3.py`. Salidas: `resultados_curvas_r3.json` (pass calculado por el codigo), `log_curvas_r3.txt`, `ckpt_curvas_r3_L{40,60,80,100}.json`. Tiempo de calculo: 827 s, CPU, OMP_NUM_THREADS=1.

## Estado y resumen de criterios

Estado: **done** (todos los criterios evaluados por el codigo).

| criterio | descripcion | resultado | pass |
|---|---|---|---|
| I3.0 | verificacion del metodo (a-e) | PASS | true |
| I3.1 | convergencia en L de n_eff, R = 10, 20, 50 mm, h = 0,25 | PASS (3/3) | true |
| I3.2 | informativo: signo de n_eff frente a R | observado: crece al bajar R | null |
| I3.3 | radio critico (P_out = 1 %, L = 100) | no establecido: sin cruce en [10; 50] mm | false |

Resumen: 2 de 3 criterios con pass (I3.0, I3.1), I3.3 falla por la regla fijada, I3.2 es informativo.

## Verificacion del metodo (I3.0)

- (a) Operador: |wrapper - solver2d| = 0,000e+00 sobre los 12 autovalores (L = 40, h = 0,5, recto). Umbral 1e-10. PASS.
- (b) Seleccion por sigma: |nucleo por sigma en la analitica - solver2d| = 0,000e+00 (L = 40, h = 0,5). Umbral 1e-10. PASS.
- (c) Contraste con la ronda 2 (L = 40, h = 0,25, sigma distinto y n_modes = 40 en r2): diferencias 9,8e-15 (R = 50), 5,6e-15 (R = 20), 2,5e-13 (R = 10). Umbral 1e-9. PASS.
- (d) Recto frente a la analitica de Snyder-Love (1,442192165457): error -2,936e-07 en L = 40, 60, 80 y 100. Umbral 1e-6. PASS. Es el mismo error de discretizacion que en la ronda 2.
- (e) Eigenpares: residuo relativo maximo 1,3e-15 (umbral 1e-8); error de normalizacion maximo 4,4e-16 (umbral 1e-10). PASS.

## Cadena de continuacion: n_eff del modo de nucleo (h = 0,25 um, n_modes = 12)

Recto (paso 0): n_eff = 1,442191871838 en todos los L.

| R (mm) | L = 40 | L = 60 | L = 80 | L = 100 |
|---|---|---|---|---|
| 50 | 1,442194819527 | 1,442194819527 | 1,442194819527 | 1,442194819527 |
| 30 | 1,442200063830 | 1,442200063831 | 1,442200063831 | 1,442200063831 |
| 20 | 1,442210322525 | 1,442210322531 | 1,442210322528 | 1,442210322527 |
| 15 | 1,442224725637 | 1,442224725257 | 1,442224725759 | 1,442224727362 |
| 10 | 1,442266248115 | 1,442266188956 | 1,442266315212 | 1,442266302764 |

Solapes de paso (S = (sum psi psi_prev h^2)^2), todos > 0,9 en todos los L. Minimo en L = 100: S_prev = 0,9879 (R = 10 mm), S_rec = 0,9611. En el paso R = 10 mm, L = 100, el segundo mejor S entre los 12 modos es 0,0073: la eleccion del nucleo es inequivoca.

Posicion del modo elegido por cercania a sigma (rank 0 = el mas cercano): mayoritariamente 0. Los pasos mas alejados son R = 15 mm, L = 100 (rank 3) y R = 10 mm, L = 100 (rank 4). Ninguno cambia la identidad del modo.

## I3.1: convergencia en L (|n(L = 100) - n(L = 80)| < 1e-6, S_rec > 0,9 en ambos L)

| R (mm) | n(L = 80) | n(L = 100) | abs(diferencia) | S_rec (L = 80) | S_rec (L = 100) | pass |
|---|---|---|---|---|---|---|
| 50 | 1,442194819527 | 1,442194819527 | 0 | 0,998787 | 0,998787 | true |
| 20 | 1,442210322528 | 1,442210322527 | 8,2e-13 | 0,992406 | 0,992406 | true |
| 10 | 1,442266315212 | 1,442266302764 | 1,24e-08 | 0,968026 | 0,961102 | true |

Lectura honesta del caso R = 10 mm: el criterio se cumple con margen de dos ordenes de magnitud (1,2e-8 frente a 1e-6), pero el par 40-60 da 5,9e-8 y el par 60-80 da 1,26e-7. La convergencia en L se ve en el par 80-100, no en un limite L -> infinito. Ademas P_out a R = 10 mm no esta convergido en L (ver I3.3).

## I3.2 (informativo): signo de n_eff frente a R

Diferencias consecutivas n(R_{k+1}) - n(R_k) a lo largo de la cadena 50 -> 30 -> 20 -> 15 -> 10 mm:

| L (um) | 50->30 | 30->20 | 20->15 | 15->10 | observado |
|---|---|---|---|---|---|
| 40 | +5,24e-6 | +1,03e-5 | +1,44e-5 | +4,15e-5 | crece al bajar R |
| 60 | +5,24e-6 | +1,03e-5 | +1,44e-5 | +4,15e-5 | crece al bajar R |
| 80 | +5,24e-6 | +1,03e-5 | +1,44e-5 | +4,16e-5 | crece al bajar R |
| 100 | +5,24e-6 | +1,03e-5 | +1,44e-5 | +4,16e-5 | crece al bajar R |

Contraste con la ronda 1: el contrato de la ronda 1 (C2) esperaba n(50) > n(20) > n(10) > n(5), es decir, n_eff decreciente al bajar R. Este resultado es el contrario: en el modelo de indice equivalente n_eff crece al bajar R, en los cuatro L. El resultado es fisicamente coherente con n_eq = n (1 + X/R): el lado exterior tiene mayor indice al bajar R, y el modo se desplaza hacia el exterior y sube su n_eff. C2 de la ronda 1 queda no cumplido. Esto se publica tal cual.

## I3.3: radio critico (regla fijada: P_out = 1 % a L = 100, interpolacion log-log)

P_out (fraccion de potencia con x > x_t, x_t = R (n_eff/n2 - 1)) a L = 100:

| R (mm) | P_out (L = 100) | x_t (um) |
|---|---|---|
| 50 | 0 | 111,0 |
| 30 | 1,4e-13 | 66,7 |
| 20 | 4,4e-9 | 44,6 |
| 15 | 2,3e-4 | 33,6 |
| 10 | 7,7e-3 | 22,7 |

- No hay cruce de P_out = 1 % en [10; 50] mm. El valor mas alto es 0,77 % a R = 10 mm.
- Por la regla fijada, R_c no queda establecido y I3.3 = false. No se afirma ningun radio critico. El cruce podria estar por debajo de 10 mm; no se ha calculado.
- P_out a R = 10 mm depende de L: 9,9e-5 (L = 40), 6,9e-4 (L = 60), 8,3e-4 (L = 80), 7,7e-3 (L = 100). Es decir, n_eff converge en L pero P_out no converge en L. El valor de P_out a L = 100 es una cifra de la caja, no del modelo sin caja.
- Informativo (fuera de criterio): R_cA de la ronda 1 (A n2 / (n_eff - n2), recto, L = 100) = 2,705 mm. No se evalua; es una estimacion analitica citada.

## Diagnostico frente a la ronda 2

- La ronda 2 concluyo FAIL en I2.1 y I2.2 para R = 10 y 20 mm. Causa: sigma fijo en el maximo de n^2 devolvia 40 modos exteriores; el nucleo quedaba fuera de la lista (S = 0). Las cifras de R = 10 mm a L = 80 y 100 (1,446321 y 1,449205) y de R = 20 mm a L = 100 (1,443553) eran modos espurios.
- La ronda 3, con seguimiento por solape, recupera el nucleo a L = 80 y 100 para R = 10 y 20 mm (1,442266 y 1,442210), y reproduce los valores de la ronda 2 donde esta tenia el nucleo (L = 40 y 60) con diferencias de 1e-13 a 1e-12.
- Los FAIL de I2.1 e I2.2 de la ronda 2 se publican tal cual en RESULTADOS-curvas-r2.md. La ronda 3 corrige la identificacion del modo y cambia la conclusion de I2.1 para R = 10 y 20 mm (ahora cumplen I3.1). No se reescribe el resultado de la ronda 2.

## Decisiones de JEV (provenance = jev, router.py jev, 07:16 UTC)

- Solape: S_potencia (confianza 0,72).
- Fallo de cadena: parar_cadena (confianza 0,40, baja).
- Criterio I3.3 sin cruce: pass_false (confianza 0,38, baja). Una primera consulta compuesta devolvio B_radio_critico (0,64), pero la pregunta estaba mal formada (la clave mezclaba dos opciones); se usa la consulta limpia.

## Limites

- n_modes = 12 y seguimiento por solape. Sin h = 0,125 (no ejecutado: coste y RAM).
- Solo L en {40, 60, 80, 100} um. La convergencia se prueba en el par 80-100.
- No se calcula R < 10 mm ni R = 5 mm.
- Sin perdida por radiacion ni dB/cm. n_eff no es perdida; no se compara con Lee et al. (2021).
- La caja de Dirichlet no representa radiacion; los estados exteriores se identifican y se publican.
- Nada vectorial (TE/TM), ni acoplo, ni fabricacion, ni dispositivo fs, ni red 3D.

## Lo calculado frente a lo supuesto

- Calculado (codigo): todas las cifras de este documento, los pass de I3.0, I3.1, I3.3, las verificaciones (a)-(e) y el contraste con la ronda 2.
- Supuesto (decision fijada, no medida): la caja de semidimension L, el indice n_eq = n_xy (1 + X/R), el solape potencia S y el umbral 0,9, la regla de cadena, el umbral de P_out 1 %.
