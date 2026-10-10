# F3 · ablación: detección intermedia frente a activación MZM · resultados (2026-10-10, 03:43 UTC)

Contrato: [`CONTRATO-ABLACION.md`](CONTRATO-ABLACION.md), publicado antes de calcular. Código: `ablacion.py` (`python -B`, `OMP_NUM_THREADS=1`, solo CPU, unos 160 s). Datos: `ablacion_resultados.json`. Modelo numérico, no un dispositivo. Ninguna cifra es una medida.

## Veredicto

- **Controles E0, E1 y E2 pasan.** El análisis reproduce exactamente las cifras de F3 y F3-b (exactitud y pérdida de entrenamiento, 0 discrepancias de predicción). El análisis es válido.
- **H-A1 no se cumple, con signo contrario al previsto.** Con V_π = 1 y θ_b = 0, quitar la activación MZM sube la exactitud de prueba de 64,25 % a 86,20 %.
- **H-A2 se cumple.** La detección intermedia |·|² aporta +27,15 puntos frente a una cascada de dos mallas sin detección.
- **H-A3 se cumple.** M_det_off y la malla de una capa M1 dan las mismas predicciones de prueba (0 discrepancias) y el mismo óptimo.
- **C-CONV no se cumple para M_real.** 7 de sus 8 reinicios agotan las 300 iteraciones. Su cifra de referencia (84,55 %) no está convergida.
- **Corrección a F3-b.** La frase "La segunda capa y la activación aportan capacidad" de `RESULTADOS-F3-B.md` no queda respaldada por esta ablación (ver Lectura). Lo corrige el coordinador: este archivo no modifica los existentes.

## Hipótesis

Puntual = diferencia de exactitudes de prueba sobre las 2000 muestras. IC 95 % = bootstrap pareado, 1000 remuestreos, semilla 20261013.

| Hipótesis | Criterio (fijado en el contrato) | Δ puntual | IC 95 % | Veredicto |
|---|---|---|---|---|
| H-A1: M_full − M_nonlin_off | IC inferior > 0 | −0,2195 | [−0,2385; −0,1980] | **No cumple** |
| H-A2: M_nonlin_off − M_det_off | IC inferior > 0 | +0,2715 | [+0,2440; +0,2990] | **Cumple** |
| H-A3: M_det_off − M1 | IC contiene 0 | 0,0000 | [0,0000; 0,0000] | **Cumple** |

## Modelos (8 reinicios, semillas 1..8, seleccionados por pérdida de entrenamiento)

| Modelo | Parámetros | Exactitud train | Exactitud prueba | Reinicio sel. | Pérdida train | Convergencia (reinicio sel.) | Prueba en los 8 reinicios |
|---|---|---|---|---|---|---|---|
| M_full (A de F3-b) | 32 | 0,6530 | 0,6425 | 5 | 0,962343 | sí (131 it.) | 0,6240 – 0,6465 |
| M_nonlin_off | 32 | 0,8490 | 0,8620 | 2 | 0,689713 | sí (55 it.) | 0,8580 – 0,8620 |
| M_det_off | 32 | 0,5795 | 0,5905 | 7 | 1,095343 | sí (21 it.) | 0,5805 – 0,5905 |
| M_real (B de F3-b) | 32 | 0,8470 | 0,8455 | 7 | 0,390158 | **no** (300 it.) | 0,6720 – 0,8455 |
| M1 (F3, reentrenada) | 16 | 0,5795 | 0,5905 | 8 | 1,095343 | — | — |

## Controles

| Control | Resultado | Veredicto |
|---|---|---|
| E0: M_full frente a F3-b | semilla 5; exactitud prueba 0,6425 (|Δ| = 0); pérdida de las 8 semillas |Δ| = 0; 0 discrepancias | **Pasa** |
| E1: M1 frente a F3 | exactitud prueba 0,5905 (|Δ| = 0); pérdida 1,0953434253 idéntica; 0 discrepancias | **Pasa** |
| E2: M_real frente a F3-b | semilla 7; exactitud prueba 0,8455 (|Δ| = 0); 0 discrepancias | **Pasa** |

## Verificaciones analíticas

| Verificación | Resultado | Veredicto |
|---|---|---|
| V1 unitariedad de la parametrización | error máx 1,8e-15 (umbral 1e-12) | Pasa |
| V2 M_det_off = \|X (U₂U₁)ᵀ\|² | diferencia máx 8,9e-15 (umbral 1e-10) | Pasa |
| V2b M1 representa U₂U₁ | error de reconstrucción 2,6e-15; diferencia de logits 4,4e-14 (umbral 1e-8) | Pasa |
| V3 bootstrap con predicciones idénticas | [0, 0] exacto | Pasa |
| V4 activación T(0) = 1, T(1) = 0 | exacto | Pasa |
| V5 reproducción del IC de F3-b (A − M1) | diferencia +0,0523535 e IC [0,0190; 0,0840] idénticos (|Δ| = 0) | Pasa |
| C-CONV convergencia del reinicio seleccionado | M_full, M_nonlin_off y M_det_off convergen; **M_real no** | **No pasa** |

## Lectura

1. **La activación MZM, con los parámetros de control, resta capacidad.** M_full pierde 21,95 puntos frente a M_nonlin_off. La pérdida es también de entrenamiento (exactitud 65,3 % frente a 84,9 %; pérdida 0,962 frente a 0,690). No es sobreajuste: la red con activación no ajusta ni los datos de entrenamiento.
2. **La ganancia viene de la detección intermedia.** Con la misma cascada de dos mallas, la detección |·|² con reemisión de amplitud aporta +27,15 puntos (M_nonlin_off frente a M_det_off).
3. **La segunda malla sin detección no aporta nada.** M_det_off es la misma función que una sola malla unitaria, porque U₂U₁ ∈ U(4). V2 y V2b lo comprueban numéricamente. El mejor reinicio de M_det_off y el de M1 dan las mismas 2000 predicciones de prueba, y sus pérdidas de entrenamiento difieren en 2e-12. Los 32 parámetros de M_det_off son redundantes.
4. **Descomposición de F3-b.** A − M1 = (A − M_nonlin_off) + (M_nonlin_off − M1) = −0,2195 + 0,2715 = **+0,052**. Es una identidad algebraica sobre las exactitudes de prueba, no un contraste. La ganancia de A frente a una capa (+5,2 puntos, V5) es la suma de una ganancia grande por detección intermedia y una pérdida grande por activación MZM en este punto de control.
5. **La referencia electrónica de F3-b no está convergida.** M_real agota 300 iteraciones en 7 de 8 reinicios. Su 84,55 % es el de un reinicio no convergido. Por eso la brecha de H-F2 de F3-b (−20,2 puntos) no puede atribuirse a la red unitaria: la referencia podría mejorar con más iteraciones. Tampoco es concluyente que M_nonlin_off (86,2 %) supere a M_real (84,55 %).
6. **Hipótesis, no probada, para la pérdida de la activación.** T(I) = (1 + cos(πI))/2 tiene periodo 2 en I. Con V_π = 1 y θ_b = 0, el 31,6 % de las intensidades de entrenamiento I₁ es ≥ 1 y el 14,9 % es ≥ 2 (mediana 0,497; p95 3,668; máx 15,09). En el intervalo [1, 2] la transmisión vuelve a subir: T(0,5) = T(1,5) = 0,5. Así, intensidades distintas producen la misma transmisión y se pierde información. Esta explicación es plausible, pero aquí no está probada.
7. **Sobre la realizabilidad.** M_nonlin_off descarta la fase en la detección intermedia y reemite la amplitud √I₁ con fase cero. Esto exige detección y reemisión coherente con fase conocida, y por tanto electrónica. Es una red optoelectrónica, como A. No es una red fotónica pasiva.

## Límites

- Tarea sintética congelada, una muestra de datos. El IC solo captura el muestreo de la prueba, no la variabilidad entre semillas de entrenamiento ni entre tareas.
- V_π y θ_b están fijados en el punto de control (1, 0). H-A1 vale para ese punto. No se buscó otro punto sobre la prueba.
- M_real no está convergida (C-CONV falla). Las comparaciones con M_real son informativas, no concluyentes.
- M_nonlin_off asume reemisión con fase cero (ver punto 7).
- `ablacion.py` reutiliza la parametrización unitaria, los datos y `paired_ci` de `run_f3.py` y `run_f3b.py`, por diseño del protocolo. Las verificaciones V1, V2 y V2b comprueban identidades, no la implementación.
- No hay medidas, energía ni fabricación. No se afirma nada sobre un dispositivo.

## Siguiente paso propuesto (no ejecutado)

Un contrato nuevo, a registrar antes de calcular, con: (a) reentrenar M_full y M_nonlin_off en una rejilla de (V_π, θ_b) seleccionando por una partición de validación interna del entrenamiento, nunca por la prueba; (b) reentrenar M_real con iteraciones suficientes para converger; (c) criterio de convergencia en todos los modelos. Ese contrato dirá si la pérdida de la activación es del punto de control o intrínseca a la activación MZM.
