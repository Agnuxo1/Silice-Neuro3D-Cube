# Tarea 10 · estabilidad y control de fase: presupuesto de error con correlación y deriva · contrato (2026-10-10)

Publicado antes de calcular. Es un **modelo** de presupuesto de error, no una medida. Continúa el análisis de GLASS-004 (errores de fase independientes, σ = 0,10 rad) y añade correlación espacial y deriva lineal.

## Modelo

- Objetivo ideal: DFT₄ (matriz unitaria 4×4 con factor 1/2). Entrada e₀; salidas I_k = |(U e₀)_k|² = 1/4.
- Errores de fase en los 16 elementos: φ_jk ~ N(0, σ²) con correlación ρ(d) = exp(−d/ℓ), donde d es la distancia entre índices de elemento en la lista plana. ℓ = 0 significa independencia.
- Deriva: φ_jk ← φ_jk + s·t·g_jk, con t ∈ [0,1] y g_jk ~ N(0,1) independiente de φ. Se toma t = 1.
- Métrica: error relativo máximo de intensidad e = max_k |I_k^err − I_k^ideal| / I_k^ideal.

## Barrido

σ ∈ {0,02; 0,05; 0,10} rad; ℓ ∈ {0; 1; 3} elementos; s ∈ {0; 0,01} rad. 20 000 muestras por combinación, semilla 20261030.

## Criterios y predicciones fijados

- **H10a (sanidad frente a GLASS-004).** Con ℓ = 0 y s = 0 y σ = 0,10, la media de e debe ser comparable con la media de GLASS-004 (error relativo de intensidad en el puerto brillante, 11,10 %). Criterio: diferencia menor que 3 puntos. Si no se cumple, la métrica de este análisis difiere de la de GLASS-004 y se reporta.
- **H10b (correlación).** p95(ℓ = 3) / p95(ℓ = 0), con σ = 0,10 y s = 0, está entre 0,8 y 1,25. Es decir, la correlación cambia el p95 menos de 25 %. Si no, la correlación es un factor dominante del presupuesto.
- **H10c (deriva).** Con s = 0,01 y σ = 0,02, la media de e aumenta menos de 50 % frente a s = 0. Si no, la deriva domina sobre el error estático a esa escala.

## Lo que no afirma

- No es una medida de fase real: no hay deriva térmica, ni calibración, ni instrumento.
- La métrica es de intensidad de un solo puerto de entrada, no de la red completa.
