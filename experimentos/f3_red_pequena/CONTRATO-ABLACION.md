# F3 · ablación: separar detección intermedia y no linealidad de activación · contrato (2026-10-10, 03:35 UTC)

Publicado antes de calcular nada. Tarea E del encargo. Modelo numérico en CPU, **no es un dispositivo**. Ninguna cifra de este contrato es una medida.

Continúa `CONTRATO-F3-RED-FUNCIONAL.md` (F3-b) y `RESULTADOS-F3-B.md`. Se reutilizan, sin modificar, `run_f3.py` (tarea congelada y malla unitaria) y `run_f3b.py` (activación, pérdida, paired_ci). No se escribe en ningún otro archivo existente.

## Pregunta

La red A de F3-b combina dos cosas a la vez: una detección intermedia por intensidad, |·|², y una activación de modulador Mach-Zehnder (MZM) que modula la amplitud que pasa a la segunda capa. ¿Cuánto de la ganancia de A frente a una sola malla unitaria se debe a la activación MZM y cuánto a la detección intermedia?

## Modelos (32 parámetros salvo M1)

Todos usan la tarea congelada (X_TR, Y_TR, X_TE, Y_TE de `run_f3.py`).

- **M_full.** Igual que A de F3-b: U₁ = exp(iH₁), I₁ = |X U₁ᵀ|², a₂ = √T(I₁) con T(I) = (1 + cos(πI/V_π + θ_b))/2, V_π = 1, θ_b = 0; salida |a₂ U₂ᵀ|². Se usa `run_f3b.logits_A`.
- **M_nonlin_off.** Detección intermedia |·|² conservada, activación desactivada: la amplitud se reemite como a₂ = √I₁ = |X U₁ᵀ| (real, fase cero). Salida |a₂ U₂ᵀ|². Aísla la no linealidad de activación: misma detección, sin MZM.
- **M_det_off.** Dos mallas unitarias en cascada en amplitud compleja: Z₁ = X U₁ᵀ, Z₂ = Z₁ U₂ᵀ, salida |Z₂|². Sin detección intermedia y sin activación. Aísla la detección intermedia.
- **M_real.** Igual que B de F3-b (pesos reales W₁, W₂, misma activación). Se usa `run_f3b.logits_B`. Referencia electrónica.
- **M1 (referencia F3).** Malla unitaria de una capa, 16 parámetros, `run_f3.logits('m1')`. Se compara con las predicciones guardadas en `f3_resultados.json`.

## Protocolo (idéntico al de F3-b)

- Entrenamiento: entropía cruzada media en entrenamiento, L-BFGS-B, `maxiter = 300`.
- 8 reinicios, semillas 1..8, p₀ = 0,5 · N(0,1) muestreado con `np.random.default_rng(s)`.
- Selección: el reinicio con menor pérdida de entrenamiento. Nunca por prueba.
- Reportado: exactitud de entrenamiento y de prueba del seleccionado. Los valores de prueba de los demás reinicios son informativos y no se usan para decidir.
- IC 95 %: bootstrap pareado sobre las 2000 muestras de prueba, 1000 remuestreos, percentiles 2,5 y 97,5, `run_f3b.paired_ci` con su semilla por defecto (20261013). La misma semilla y los mismos índices en todas las comparaciones.
- Entorno: `python -B`, `OMP_NUM_THREADS=1`, solo CPU, sin instalaciones.

## Controles (bloqueantes: si uno falla, el análisis no es válido)

- **E0 (reproducción de A).** M_full con semillas 1..8 debe reproducir F3-b:
  - exactitud de prueba del seleccionado = 0,6425, con |Δ| < 1e-12;
  - semilla seleccionada = 5;
  - para cada semilla s, |pérdida de entrenamiento − pérdida guardada en `f3b_seeds/a_s{s}.json`| < 1e-9.
- **E1 (reproducción de M1).** `run_f3.train('m1')` debe reproducir exactitud de prueba 0,5905 con |Δ| < 1e-12, y predicciones de prueba idénticas a las guardadas (0 discrepancias).
- **E2 (reproducción de B).** M_real debe reproducir exactitud de prueba 0,8455 (guardado en `f3b_resultados.json`) con |Δ| < 1e-12.

## Verificaciones analíticas

- **V1 (unitariedad).** Para 100 vectores p aleatorios, máx |U Uᴴ − I| < 1e-12 en `unpack_unitary`.
- **V2 (identidad de clase).** Para p aleatorios, los logits de M_det_off son iguales a |X (U₂U₁)ᵀ|² (salida de una malla unitaria con U = U₂U₁). Umbral: máx |diferencia| < 1e-10. Si se cumple, M_det_off y M1 tienen la misma clase de funciones, aunque M_det_off tenga 32 parámetros redundantes.
- **V2b (equivalencia constructiva con M1).** Para 20 vectores p₃₂ aleatorios, U = U₂U₁ se escribe como exp(iH) con H hermítica (H = −i log U). Existe p₁₆ con `unpack_unitary(p₁₆) = U` (máx error < 1e-8) y los logits de M1(p₁₆) coinciden con los de M_det_off(p₃₂) (máx |diferencia| < 1e-8). Confirma que M1 puede representar cualquier salida de M_det_off.
- **V3 (bootstrap).** `paired_ci(p, p)` debe dar [0, 0] exacto.
- **V5 (reproducción del IC de F3-b).** `paired_ci(pred_A, pred_M1)` debe reproducir exactamente la diferencia +0,0523535 y el IC [0,0190; 0,0840] guardados en `f3b_aggregate.json` (|Δ| < 1e-12).
- **V4 (activación).** T(0) = 1 y T(1) = 0 con V_π = 1 y θ_b = 0, con error < 1e-15.
- **C-CONV (convergencia).** El reinicio seleccionado de cada modelo debe terminar con `success = True` de L-BFGS-B. Si no, se publica como "no convergido" y no se afirma la cifra como óptimo.

## Hipótesis y criterios (umbrales fijados aquí)

- **H-A1.** Δ₁ = exact(M_full) − exact(M_nonlin_off) en prueba. **Cumple** si el IC 95 % inferior de Δ₁ es > 0. Mide el aporte de la activación MZM con la detección intermedia constante.
- **H-A2.** Δ₂ = exact(M_nonlin_off) − exact(M_det_off) en prueba. **Cumple** si el IC 95 % inferior de Δ₂ es > 0. Mide el aporte de la detección intermedia |·|² sin activación.
- **H-A3.** Δ₃ = exact(M_det_off) − exact(M1) en prueba. Predicción analítica: Δ₃ = 0 por V2. **Cumple** si el IC 95 % contiene 0 (IC inferior ≤ 0 ≤ IC superior). Operacionalización mía, fijada aquí, porque el encargo pedía solo "diferencia con IC". Si el IC excluye 0, la diferencia se atribuye a optimización (distintos mínimos locales), no a capacidad, y se informa así.

Un criterio es pass = true solo si lo evalúa el código entregado (`ablacion.py`), y se escribe en `ablacion_resultados.json`.

## Lo que NO afirmo

- No afirmo nada sobre un dispositivo, una fabricación, medidas ni energía. Las cifras son de un modelo numérico con tarea sintética.
- La activación usa electrónica de control y fotodetector: no es totalmente óptica.
- M_nonlin_off conserva un módulo |·| de detección; su "sin activación" no equivale a una red lineal.
- El IC bootstrap solo captura la variabilidad del muestreo de prueba. No captura la variabilidad entre semillas de entrenamiento ni entre tareas (una sola muestra congelada).
- No afirmo que M_det_off sea más o menos capaz que M1 por encima de V2: son la misma clase de funciones.
- Ninguna comparación se usa para seleccionar modelo ni hiperparámetro; la prueba solo informa.
- Ningún criterio se modifica después de ver resultados. Si un criterio falla, se publica así.

## Salidas

- `ablacion.py` (código del análisis, solo lectura de `run_f3.py` y `run_f3b.py`).
- `ablacion_resultados.json` (cifras, IC, controles, verificaciones, veredictos).
- `RESULTADOS-ABLACION.md` (lectura de resultados, incluidos los fallos).
