# VERIFICACION V3 · grupos D (frontera 009c en vacío) y E (ablación de la red F3)

Verificador independiente y adversarial. 2026-10-10, de 04:11 a 04:35 UTC. Solo CPU, `python -B`, `OMP_NUM_THREADS=1`. No se ha modificado ningún archivo ajeno; no hay git add/commit/push.
Todo es un modelo numérico. Ninguna cifra de este informe es una medida de un dispositivo.

Código y datos propios (en esta carpeta):
- `verif_ablacion.py` → `verif_ablacion_resultados.json`, `verif_ablacion_salida.txt` (reimplementación desde cero de la tarea, la parametrización unitaria y los cuatro modelos).
- `verif_vacio.py` (solvers `dst`, `fft`, `adi`), `verif_vacio_pad.py` → `verif_vacio_out/*.json`, `verif_vacio_out_*.txt`, `verif_pad_*.txt`.

## 0. Resumen

| Grupo | Veredicto de la verificación |
|---|---|
| E, preregistro | PASA (con una anotación menor sobre la hora de cabecera) |
| E, reproducción de F3-b (M_full = 0,6425, semillas 1..8) | PASA, diferencia exacta 0 |
| E, signos de H-A1 y H-A2 con otras semillas de bootstrap | PASA (H-A1 no se cumple, H-A2 se cumple, H-A3 se cumple) |
| D, preregistro | PASA con reservas (contrato enmendado en el sitio tras ver D1; sin git no se puede recuperar el texto original) |
| D, reflexión en vacío de D1 con otra malla | PASA: cifras reproducidas, con una discrepancia de 5 a 8 % por el esquema ADI en haz inclinado |
| D, atribución de causas (a) discretización y (b) frontera | PASA, con una corrección del orden de convergencia |

## 1. Preregistro (`ls -l --time-style=full-iso`; hora local CEST = UTC + 2)

El repositorio no es un repositorio git: la única evidencia temporal son las fechas de modificación.

Grupo E (carpeta `experimentos/f3_red_pequena/`):

| Archivo | Modificado (CEST) | UTC |
|---|---|---|
| `CONTRATO-ABLACION.md` | 05:31:35 | 03:31:35 |
| `ablacion.py` | 05:40:09 | 03:40:09 |
| `ablacion_resultados.json` | 05:42:57 | 03:42:57 |
| `RESULTADOS-ABLACION.md` | 05:43:29 | 03:43:29 |

El contrato es anterior al código (8 min 34 s) y a los resultados (11 min 22 s). No se ha editado después (su fecha de modificación es la primera). Los umbrales de H-A1, H-A2, H-A3 en `ablacion.py` coinciden con los del contrato (`ci95[0] > 0`, `ci95[0] > 0`, `ci95[0] <= 0 <= ci95[1]`). El tiempo de ejecución declarado (unos 160 s) coincide con la diferencia entre código y JSON (168 s).
Anotación menor: la cabecera del contrato dice "03:35 UTC", pero su última modificación es 03:31:35 UTC. Una cabecera posterior a la última modificación del archivo es inconsistente (probablemente una hora estimada a mano). No afecta a ningún criterio.

Grupo D (carpeta `experimentos/glass009c_claude/`):

| Archivo | Modificado (CEST) | UTC |
|---|---|---|
| `CONTRATO-VACIO.md` | 05:40:04 | 03:40:04 |
| primeras corridas nuevas (`vacio_estados/`, lote S1) | 05:37:00 a 05:37:34 | 03:37:00 a 03:37:34 |
| lote de dx 0,25 (D4) | 05:41:04 a 05:45:20 | 03:41:04 a 03:45:20 |
| controles de la enmienda 1 (sin esponja) | 05:42:32 a 05:42:33 | 03:42:32 |
| referencia 512 µm | hasta 05:53:44 | 03:53:44 |
| `validacion_vacio_analisis.py` | 05:46:22 | 03:46:22 |
| `resultados009c_vacio.json` | 05:53:58 | 03:53:58 |
| `RESULTADOS-009C-VACIO.md` | 05:56:54 | 03:56:54 |

- El contrato declara "redactado 03:33 UTC, antes de ejecutar ninguna corrida nueva". La primera corrida nueva es de las 03:37 UTC: coherente.
- La fecha de modificación del contrato (03:40:04 UTC) coincide con la hora de la Enmienda 1 (03:40 UTC). La enmienda se añadió en el mismo archivo tras ver D1 (lote S1, 03:37). El resultado, y los controles C-ref y C-sin, vienen después. El texto lo reconoce expresamente ("tras ver D1 y antes de ejecutar el control", "sin umbral nuevo").
- Reserva: sin git no se puede recuperar la versión anterior a la enmienda. Se acepta la declaración del autor. Los umbrales usados en `validacion_vacio_analisis.py` y guardados en el JSON (`K1_thr = 1e-4`, `K2_spread = 2`, `K5_tol = 1e-9`, `B1_thr = 1e-3`, `q` en [2,5; 6] y [0,67; 1,5]) coinciden con los del contrato. Ningún umbral se ha movido.
- Los datos de 128 y 256 µm de 009c (`out/`, `out2/`) son del 2026-10-09 14:36, anteriores al contrato. El contrato lo declara (se reutilizan sin re-ejecutar).

## 2. Grupo E · reproducción de M_full y de la ablación

Se ha reescrito la tarea congelada (semillas 20261009/10/11), la parametrización unitaria y los cuatro modelos sin importar `ablacion.py`. Comprobación cruzada de funciones con las del autor (solo para comparar): diferencia máxima 0 en `unpack_unitary`, `logits_A`, `logits_B` y `logits("m1")`; etiquetas de entrenamiento y prueba idénticas.

| Modelo | Mío: semilla | train | prueba | pérdida train | success / nit | Autor |
|---|---|---|---|---|---|---|
| M_full | 5 | 0,6530 | **0,6425** | 0,962343314 | sí / 131 | 5 / 0,6530 / 0,6425 / 0,962343 / 131 |
| M_nonlin_off | 2 | 0,8490 | 0,8620 | 0,689713059 | sí / 55 | 2 / 0,8490 / 0,8620 / 0,689713 / 55 |
| M_det_off | 7 | 0,5795 | 0,5905 | 1,095343425 | sí / 21 | 7 / 0,5795 / 0,5905 / 1,095343 / 21 |
| M_real | 7 | 0,8470 | 0,8455 | 0,390157917 | **no** / 300 | 7 / 0,8470 / 0,8455 / 0,390158 / 300 |
| M1 | 8 | 0,5795 | 0,5905 | 1,095343425 | sí / 40 | 8 / 0,5795 / 0,5905 |

- E0: M_full con semillas 1..8 reproduce 0,6425 con |Δ| = 0, semilla 5, pérdida de entrenamiento de las 8 semillas |Δ| = 0 frente a `f3b_seeds/a_s{1..8}.json`, y 0 discrepancias de predicción.
- E1 y E2 también exactas (0 discrepancias).
- C-CONV: M_real agota 300 iteraciones en 7 de 8 reinicios (solo 1 con success). Confirmado. Los otros tres modelos convergen en el reinicio seleccionado.
- Rangos de prueba en los 8 reinicios: M_full 0,6240–0,6465; M_nonlin_off 0,8580–0,8620; M_det_off 0,5805–0,5905; M_real 0,6720–0,8455. Idénticos a la tabla del autor.
- Unitariedad máxima 2,0e-15; M_det_off frente a |X(U₂U₁)ᵀ|²: 8,9e-15 (umbrales 1e-12 y 1e-10).
- Diagnóstico de la lectura 6: fracción I₁ ≥ 1 = 31,56 %, ≥ 2 = 14,90 %, mediana 0,497, p95 3,668, máx 15,09. Idéntico.

### Bootstrap con otras semillas (10 000 remuestreos pareados, sobre las 2000 muestras de prueba)

| Hipótesis | Δ puntual | IC 95 % semilla 777 | IC 95 % semilla 4242 | IC del autor (20261013, 1000) | IC normal pareado | McNemar exacto |
|---|---|---|---|---|---|---|
| H-A1 M_full − M_nonlin_off | −0,2195 | [−0,2400; −0,1995] | [−0,2395; −0,1995] | [−0,2385; −0,1980] | [−0,2396; −0,1994] | 39 frente a 478 discordantes, p = 3,8e-97 |
| H-A2 M_nonlin_off − M_det_off | +0,2715 | [+0,2450; +0,2985] | [+0,2450; +0,2985] | [+0,2440; +0,2990] | [+0,2444; +0,2986] | 728 frente a 185, p = 9,0e-77 |
| H-A3 M_det_off − M1 | 0,0000 | [0; 0] | [0; 0] | [0; 0] | [0; 0] | 0 discordantes |

Signos confirmados: el IC de H-A1 está entero por debajo de 0 (no se cumple, criterio `ci95[0] > 0`); el IC inferior de H-A2 es positivo (se cumple); H-A3 contiene 0 (se cumple). Los tres veredictos del autor se reproducen con tres métodos distintos.

Anotaciones de rigor (no cambian ningún veredicto):
- H-A3 pasa de forma trivial: las 2000 predicciones son idénticas, por lo que el IC es [0, 0]. El peso de la afirmación recae en V2/V2b (identidad analítica), que sí se reproducen. Es correcto, pero H-A3 no es un contraste estadístico informativo.
- V5 llama "diferencia +0,0523535" a la media del bootstrap de F3-b; la diferencia puntual es +0,0520. La lectura 4 usa +0,052 (puntual) y es coherente.
- Tarea: la clase mayoritaria de la prueba es el 52,5 % (recuentos de clases 701/242/1050/7). M1 (59,05 %) y M_det_off superan la línea base trivial por solo 6,55 puntos; M_full (64,25 %) por 11,75. La exactitud sin ajustar por desequilibrio no está en los criterios; conviene tenerlo presente al citar "+27 puntos".

### Sonda adicional no preregistrada (solo informativa; una sola tanda de semillas, sin valor de criterio)

La lectura 6 propone que la pérdida de la activación se debe a la periodicidad de T(I) con V_π = 1. Se entrenó M_full (semillas 1..8, mismo protocolo) con V_π mayor, donde casi toda la I₁ cae en el primer tramo monótono:

| V_π | prueba M_full | frente a M_nonlin_off (0,8620) | IC 95 % (10 000, semilla 777) |
|---|---|---|---|
| 4 | 0,6690 | −0,1930 | [−0,2115; −0,1745] |
| 8 | 0,6105 | −0,2515 | [−0,2705; −0,2315] |

M_full sigue muy por debajo con V_π = 4 y 8. La hipótesis "periodo 2 en I" no explica por sí sola la pérdida (el autor la marcó como no probada, y lo es). Con V_π grande la transmisión casi no cambia con la intensidad, lo que es otra causa posible. Esto no contradice H-A1 (que vale solo para el punto V_π = 1, θ_b = 0); acota la lectura 6.

## 3. Grupo D · reflexión en vacío de D1 con otra malla

Se ha reproducido con tres soluciones distintas la cifra de D1 (dominio 128 µm, f = 0,2, p = 4, σmax = 4·10⁴ m⁻¹, dz = 2,5 µm, w₀ = 6 µm, δn = 0):

- `adi`: el `adi2d.py` de 009c (solo lectura) con una malla nueva: dx = 0,4 µm (N = 320), que no estaba en el estudio.
- `dst`: solver propio. Mismo Laplaciano de diferencias finitas de 2.º orden con pared de Dirichlet, pero integración exacta en z por DST-I (Strang con el absorbente). Separa el error del esquema ADI del error espacial.
- `fft`: solver propio espectral periódico (error espacial despreciable). Y una variante `pad` (caja de 256 µm con el mismo perfil σ y σ = σmax constante fuera de ±64 µm, sin pared): el absorbente sin pared.

Máx. |ΔP_u|/P0 en la ventana W (z ≥ z_arr), muestreo cada 0,1 mm (mi z_arr coincide con el del autor en todos los casos):

| Caso | Autor (ADI) | Mío ADI | Mío DST | Diferencia DST frente al autor |
|---|---|---|---|---|
| 128 µm, θ = 0, dx 0,5 | 6,038e-3 (z = 2,0) | — | 6,0380e-3 | 0,0 % |
| 128 µm, θ = 0,02, dx 0,5 | 5,551e-3 | — | 5,5516e-3 | 0,0 % |
| 128 µm, θ = 0, **dx 0,4 (malla nueva)** | no calculado | **5,8805e-3** | 5,8804e-3 | — |
| 128 µm, θ = 0, dx 0,25 | 5,625e-3 | — | 5,6250e-3 | 0,0 % |
| 128 µm, θ = 0,05, dx 0,5 | 6,306e-3 (z = 0,5) | 6,3062e-3 | 5,9758e-3 | −5,2 % |
| 128 µm, θ = 0,08, dx 0,5 | 1,629e-2 (z = 0,4) | — | 1,4936e-2 | −8,3 % |
| 128 µm, θ = 0,05, dx 0,25 | 3,822e-3 (z = 2,0) | — | 3,8212e-3 | 0,0 % |
| 256 µm, θ = 0, dx 0,5 | 1,544e-3 (z = 0,9) | — | 1,5195e-3 | −1,6 % |
| 512 µm, θ = 0,05, dx 0,5 | 2,283e-4 (z = 1,4) | — | 2,2706e-4 | −0,5 % |
| sin esponja, θ = 0 | 9,241e-2 | — | 9,245e-2 | +0,0 % |
| sin esponja, θ = 0,08 | 3,949e-1 | — | 3,9405e-1 | −0,2 % |

Conclusión: la cifra de D1 queda reproducida con otra malla y con un integrador distinto. Las cifras de θ = 0 y 0,02 son idénticas a 4 cifras. En haz inclinado con dx = 0,5 µm el ADI da entre 5 y 8 % más que la integración exacta en z (θ = 0,05: ADI 6,306e-3, DST 5,976e-3). Con dz = 1,25 µm el ADI baja a 6,058e-3 y se acerca a la DST (cociente de diferencias 0,33 → 0,08, orden 2 en z): es error de división del ADI, no de la frontera. No cambia ningún veredicto (K1 falla por 15 a 160 veces).

### Atribución de causas

(a) Error temprano por discretización. El solver espectral da ΔP_u ≈ 0 donde el ADI da 5e-3:

| θ | z (mm) | ΔP_u/P0 FD (DST, dx 0,5) | ΔP_u/P0 espectral (dx 0,5) |
|---|---|---|---|
| 0,05 | 0,4 | 4,93e-3 | −5,5e-9 |
| 0,05 | 0,5 | 5,98e-3 | 5,5e-7 |
| 0,08 | 0,4 | 1,49e-2 | 1,4e-7 |

Confirmado: el error temprano es dispersión numérica de las diferencias finitas. El campo analítico de 009c queda además validado de forma independiente: el espectral en 512 µm sin absorbente reproduce el analítico con |ΔP_u|/P0 ≤ 2,4e-9 en todo z (θ = 0,05), y E ≈ 1e-14 antes de la llegada.
Corrección al texto: el autor mide un cociente ~3,3 al pasar de dx 0,5 a 0,25 y deduce un orden ≈ 1,7. Con integración exacta en z el cociente es 4,00 (θ = 0,05, z = 0,4) y 4,10 (z = 0,5): orden 2 limpio. El orden 1,7 es un artefacto de mezclar el error en z del ADI. La extrapolación de la sección 11 del autor ("dx ≈ 0,12 µm") vale solo para θ = 0. Con orden 2 desde el máximo temprano de θ = 0,08 (1,49e-2 a dx 0,5) harían falta dx ≈ 0,04 µm para llegar a 1e-4 (extrapolación mía, no calculada), unas 3100 celdas por lado en 128 µm.

(b) Frontera tardía. Falsable y no refutada:
- Con 512 µm y absorbente, el espectral da |ΔP_u|/P0 ≤ 3,7e-10 (θ = 0,05) y ≤ 8,6e-10 (θ = 0,08): la residual de 2,3e-4 y 1,7e-4 que el autor encuentra en 512 µm es 100 % de diferencias finitas, no del absorbente. Coincide con la lectura del autor (K1 no se cumple "ni con la frontera lejana" por la causa a).
- El absorbente sin pared (variante `pad`, espectral, dx 0,5): |ΔP_u|/P0 ≤ 5,1e-5 hasta z = 1,0 mm en los cuatro ángulos, pero el retorno supera 1e-4 desde z = 1,1 mm en los cuatro ángulos (1,5e-4 a 3,5e-4) y llega a 8,1e-3 (θ = 0), 8,1e-3 (0,02), 6,8e-3 (0,05) y 3,3e-3 (0,08) en z = 2,0 mm. Así, en un modelo sin error de diferencias finitas, el absorbente de 128 µm tampoco cumple −40 dB hasta 2 mm. La pared de Dirichlet no es necesaria para el retorno tardío. Matiz que el autor no da: en z ≤ 1,0 mm el absorbente por sí solo sí está por debajo de 1e-4; el fallo de K1 en esa franja es enteramente de discretización.
- Dependencia con la distancia: DST en 256 µm, θ = 0, z = 2 mm: 1,65e-4 (autor: 1,7e-4).
- Dependencia de la malla del máximo tardío en θ = 0: 6,038e-3 (dx 0,5), 5,880e-3 (0,4), 5,625e-3 (0,25). Cambia un 7 % al doblar la resolución; es casi independiente de la malla, y extrapola (orden 2) a ≈ 5,5e-3. La lectura "independiente de la malla" del autor vale con esa tolerancia.
- B1 en dx = 0,25, θ = 0: el autor da E_suelo = 1,99e-3 (> 1e-3). Con integración exacta en z obtengo 1,75e-3 (> 1e-3): el fallo de B1 se confirma; el ADI aporta un ~14 % de fase de más al campo.

Un solver espectral periódico en la caja de 128 µm (modo `fft`, sin zona de relleno) da 1,2e-2 (θ = 0, dx 0,5 y 0,4) y no es comparable: el campo que sale por un borde reentra por el opuesto. No se usa como referencia.

## 4. Riesgos no cubiertos por los criterios

1. No hay git: las únicas pruebas de preregistro son fechas de modificación, editables. En D el contrato se enmendó en el sitio; el texto original no es recuperable. Recomendación: guardar el hash del contrato antes de calcular.
2. El análisis de D (K0a) compara el runner con salidas del mismo `adi2d.py`; no es una verificación independiente del solver. Aquí se cubre con DST y espectral, pero el informe no lo incluye.
3. El ADI aporta un error en z del 5–8 % en la cifra máxima con haz inclinado y dx = 0,5 µm; el orden espacial aparente (1,7) y la extrapolación dx ≈ 0,12 µm de la sección 11 de `RESULTADOS-009C-VACIO.md` salen de esa mezcla y son optimistas para θ ≥ 0,05.
4. El muestreo cada 0,1 mm no ve los máximos entre muestras (reconocido por el autor). En el espectral sin pared el retorno cambia de signo entre 1,4 y 1,6 mm (−9,6e-4 y +5,2e-4 para θ = 0), por lo que un máximo en W puede no verse; la afirmación "ρ = max(0, ΔP)" omite una pérdida de hasta 9,6e-4 P0 en esa franja.
5. En E: una sola muestra de datos, una sola tarea, un solo punto de control de la activación (V_π = 1, θ_b = 0); IC solo de muestreo de prueba, no de semillas; exactitud sin ajustar por clase (mayoritaria 52,5 %, una clase con 7 de 2000 ejemplos). La explicación causal de la lectura 6 no se sostiene como única según la sonda con V_π = 4 y 8.
6. M_nonlin_off emite la amplitud real con fase cero: no es un dispositivo pasivo (reconocido por el autor).
7. El informe de E titula la pérdida de la activación como "del punto de control". Mi sonda no la reproduce a V_π = 4 y 8, pero tampoco se ha buscado V_π óptimo sobre validación; es una pregunta abierta, no una conclusión.

## 5. Veredicto por criterio de aceptación

| Criterio | Resultado | Evidencia |
|---|---|---|
| Leer contratos y JSON | PASA | Leídos `CONTRATO-ABLACION.md`, `RESULTADOS-ABLACION.md`, `ablacion.py`, `ablacion_resultados.json`, `CONTRATO-VACIO.md`, `RESULTADOS-009C-VACIO.md`, `resultados009c_vacio.json`, `vacio_analisis_salida.txt`, `validacion_vacio_run.py` y `validacion_vacio_analisis.py`. |
| Preregistro con `ls -l --time-style=full-iso` | PASA con reservas | E: contrato 03:31:35 UTC < código 03:40:09 < JSON 03:42:57. D: primeras corridas 03:37, enmienda 03:40:04 declarada, controles posteriores. Sin git. |
| M_full reproduce 0,6425 con semillas 1..8 | PASA | `verif_ablacion.py`: 0,6425, semilla 5, |Δ| = 0; pérdidas de 8 semillas |Δ| = 0; 0 discrepancias de predicción. |
| IC bootstrap con otra semilla, signos de H-A1 y H-A2 | PASA | Semillas 777 y 4242, 10 000 remuestreos: H-A1 IC [−0,2400; −0,1995] (no cumple), H-A2 IC [+0,2450; +0,2985] (cumple); H-A3 [0; 0] (cumple). Bootstrap normal y McNemar exacto concuerdan. |
| Reflexión en vacío de D1 con otra malla | PASA | ADI con dx = 0,4: 5,8805e-3 (θ = 0); DST: 5,8804e-3; espectral: causa (a) confirmada. Cifras de D1 reproducidas (0,0 % en θ ≤ 0,02; −5 % a −8 % en haz inclinado por el esquema ADI). |
