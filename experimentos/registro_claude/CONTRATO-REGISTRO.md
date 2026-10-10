# Tarea K · registro entre caras y tolerancias correlacionadas (modelo) · contrato prospectivo (2026-10-10)

Publicado antes de calcular. Alcance: solo **modelo numérico** en CPU. La medida real de desplazamiento y de rendimiento es de laboratorio y queda **bloqueada**. Ninguna cifra de este contrato es una medida.

## Modelo

- Dos guías del acoplador escritas desde caras distintas tienen un desplazamiento lateral δ que cambia la separación efectiva: d_eff = d + δ (caso favorable) y d_eff = d − δ (caso peor, el que fija la tolerancia).
- Acoplo κ(d) en µm⁻¹: tomado de `experimentos/acoplo_claude/acoplo_paralelo.py` (función `kappa`, importada tal cual; no se reimplementa).
- Potencia transferida a la guía 2 tras L = 10 mm = 10 000 µm, con fase igualada: P₂(d_eff) = sin²(κ(d_eff) · L).
- Criterio de diseño: P₂ ≤ 0,10.
- d* = separación con P₂(d*) = 0,10 en la rama de transferencia monótona (primera raíz de κ(d)·L = arcsin √0,10 = 0,32175 rad).
- Tolerancia simétrica del caso peor: δ_max(d) = d − d*. Si δ_max < 0, el diseño falla aun sin desplazamiento.

## Supuestos declarados (no medidos)

- **σ** ∈ {0,5; 1; 2} µm: desviación típica del desplazamiento entre caras. Supuesto, no medido.
- **l** ∈ {0 (sin correlación, referencia iid), 1, 3, 10} celdas: longitud de correlación. Supuesto, no medido.
- **Kernel de correlación**: exponencial, C(k) = exp(−|k|/l). Sensibilidad: kernel gaussiano para σ = 1 µm (solo como comprobación).
- **N = 200** acopladores por chip (una celda por acoplador). Supuesto.
- **σ_res = 0,2 µm**: residuo tras corrección. Supuesto. Residuo independiente entre acopladores (iid).
- Desplazamiento solo a lo largo de la línea de separación, como define la tarea. El desplazamiento transversal solo cambia d a segundo orden (√(d² + δ²)) y no se modela.
- Proceso gaussiano estacionario, de media cero. Simetría del signo: la distribución de d_eff con d + δ y con d − δ es idéntica en ley; se comprueba numéricamente.

## Método

- **κ(d)**: tabla en d ∈ [12, 40] µm con paso 0,01 µm, interpolada linealmente en ln κ. Se verifica contra la llamada directa a `kappa`.
- **Enmienda E-2 (antes de calcular)**: la comparación de K3-C2 usa el valor analítico con tolerancia 1e-4 (error de cuadratura). Los criterios de K2 usan el Monte Carlo tal como se ha fijado. Los factores de correlación se obtienen por descomposición espectral (eigh con recorte de autovalores negativos a 0), no por Cholesky, porque el kernel gaussiano con l = 10 es numéricamente singular. Se comprueba la reconstrucción max|AAᵀ − C| < 1e-8.
- **Enmienda E-1 (antes de calcular)**: una muestra con d_eff < 12 µm (núcleos solapados, fuera del dominio del modelo de guías separadas) cuenta como **fallo** (regla conservadora). Su número se reporta. Para d_eff > 40 µm se usa κ(40 µm) = 1,15·10⁻⁵ µm⁻¹, que da P₂ ≈ 0,013 ≤ 0,10: la decisión de cumplimiento coincide con la real, porque P₂ decrece con d.
- **d\***: `brentq` sobre κ(d)·L − arcsin √0,10 en [16, 30] µm.
- **Monte Carlo (K2, K3)**: R = 2000 realizaciones, semilla fija 20261010 (`numpy.random.default_rng`). δ = σ · Lₒ · z, con Lₒ el factor de Cholesky de la matriz de correlación de 200 × 200 (jitter 1e-10). Fracción por chip f = media de 1{P₂(d + δ_i) ≤ 0,10}.
- **Valor analítico** de la media de f: E = ∫ 1{P₂(d + δ) ≤ 0,10} φ_σ(δ) dδ, por cuadratura fina. Sirve para verificar el Monte Carlo.
- **Barrido de diseño**: d en pasos de 0,05 µm alrededor de d*, para hallar d_chip95(σ, l), el mínimo d con rendimiento por chip Y ≥ 0,95.

## Criterios (umbrales fijados AHORA, antes de calcular)

Verificaciones (si fallan, el resultado no es fiable):
- **V-K0** (κ): error relativo máximo entre interpolación y `kappa` directo < 1e-4 en 50 puntos de d ∈ [12, 35] µm.
- **V-K1** (raíz): |P₂(d*) − 0,10| < 1e-9, y un único cambio de signo de κL − 0,32175 en [16, 30] µm.
- **V-K2** (generador gaussiano): |corr. empírica(k) − exp(−k/l)| < 0,02 para k = 1..10 y l ∈ {1, 3, 10}; |sd − 1| < 0,02.
- **V-K3** (MC frente a analítico): |media MC − E analítico| < 0,005 en las 12 celdas (l ∈ {0,1,3,10} × σ ∈ {0,5,1,2}, d = 20 µm).
- **V-K4** (semilla): con dos semillas adicionales, la media cambia menos de 0,01 en cada celda.

Criterios de resultado:
- **K1-C1**: δ_max(d = 20 µm) = 20 − d* ≥ 0. Predicción: **falla** (δ_max ≈ −0,43 µm), porque P₂(20) = 0,141 sin desplazamiento (RESULTADOS-ACOPLO.md).
- **K2-C1 (primario)**: fracción media ≥ 0,95 en d = 20 µm, en cada una de las 9 celdas (σ, l ≥ 1) y en la referencia l = 0. Predicción: **falla en todas**.
- **K2-H-a**: |media(l) − media(0)| < 0,01 para l ∈ {1,3,10} y cada σ (la media no depende de la correlación). Predicción: **cumple**.
- **K2-H-b**: sd(f_chip) crece con l para cada σ. Predicción: **cumple**.
- **K2-C2**: Y(d_min(σ)) ≥ 0,95 en cada celda, con d_min(σ) = d* + 1,645 σ (diseño que cumple la media del 95 %). Predicción: **falla** (Y ≈ 0,5 cuando la media está en el umbral).
- **K3-C1**: fracción media con residuo σ_res = 0,2 µm en d = 20 µm ≥ 0,95. Predicción: **falla** (≈ 1,6 %).
- **K3-C2**: fracción media en d_min,cal = d* + 1,645 · 0,2 ≥ 0,95, evaluada sobre el valor analítico con tolerancia de cuadratura 1e-4 (enmienda E-2, fijada antes de calcular), y además |media MC − analítico| < 0,005. Predicción: **cumple** (validación de la regla de diseño).
- **K3-C3** (comparación con K2): fracción K3 en d = 20 µm < mín_σ fracción K2 en d = 20 µm. Predicción: **cumple**. Motivo: la calibración centra la distribución en cero y el umbral está en +0,43 µm, así que la dispersión sin corregir ayuda en el caso nominal. Es un resultado de diseño, no una mejora.
- **K3-C4**: d_min,cal < d_min(σ) para cada σ. Predicción: **cumple** (la calibración reduce la separación de guarda).
- **K3-C5**: Y_cal(d_min,cal) ≥ 0,95. Predicción: **falla** (≈ 0,5).

Descriptivos (sin umbral de aprobación): δ_min favorable = d* − d; desplazamientos del conjunto P₂ ≤ 0,10 en la rama no monótona (d_eff < 16 µm); d_chip95(σ, l); P5 de f_chip; sensibilidad al kernel gaussiano.

## Qué NO afirmo

- No hay medidas. σ, l, σ_res y N son supuestos. Las cifras son del modelo.
- El prefactor de κ hereda la limitación de `acoplo_paralelo.py`: V3 valida la forma, no el valor absoluto. Por tanto d* y δ_max dependen de un prefactor no verificado de forma independiente.
- No es una simulación vectorial de la escritura fs ni de la trinchera; el modelo es escalar, isótropo y de fibra análoga.
- No afirmo que el ajuste P₂ ≤ 0,10 sea una tolerancia continua fuera de d*. La curva P₂(d) oscila en d_eff < 16 µm y tiene ventanas de cumplimiento puntuales. Se reportan, no se usan como diseño.
- No afirmo que el residuo de calibración sea independiente entre acopladores en la realidad. Es un supuesto de modelo.
- JEV: el intento de consulta con `enrutador-jev/scripts/router.py jev` falló en la validación local del esquema (stage `local_schema`). La provenance no es `jev`. Las decisiones de método de este contrato son locales y se declaran como fallback explícito.
