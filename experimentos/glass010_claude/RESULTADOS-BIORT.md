# GLASS-010 · base biortogonal para modos cuasi-ligados · RESULTADOS-BIORT (2026-10-10)

Contrato: [`CONTRATO-BIORT-r4.md`](CONTRATO-BIORT-r4.md), publicado antes de calcular. Código: `biortogonal_sintetico.py`. Datos: `resultados_biort.json`, con los pass calculados por el código. Solo CPU, numpy, `python -B`, `OMP_NUM_THREADS=1`. La corrida tarda milisegundos; no hubo recortes de malla.

## Veredicto

- **Bloque 1 (preregistrado):** cumplen B1, B2 y B3, las verificaciones V1 a V4, el cierre D1 y la predicción P1.
- **Bloque 2 (barrido adicional, post hoc):** fallan B1, V1 y D1 en el caso de solape más alto (δ = 0,02 µm). Cumplen B2, B3 y V2. Se publica el fallo. No altera el veredicto del bloque 1.
- **Pendiente:** la aplicación a GLASS-010 original. Motivo en la sección "Lo que no se afirma".

## Qué se calcula

- Dos modos sintéticos unitarios: φ_m(x) = exp(−(x − x_m)²/(2·2²)) · exp(i k_m x), con x₁ = 0, k₁ = 0, x₂ = δ, k₂ = 0,7 µm⁻¹ (bloque 1). Malla de 4001 puntos en [−40, 40] (unidades abstractas).
- **Método D (propuesta):** base dual χ = Φ G⁻¹, que cumple ⟨χ_i, φ_j⟩ = δ_ij. Coeficientes c = G⁻¹ d con d_m = ⟨φ_m, ψ⟩. η_D = ‖Φc‖² / ‖ψ‖².
- **Método A (GLASS-010, modo a modo):** c_m = d_m / G_mm. η_A = Σ_m |c_m|² G_mm / ‖ψ‖². Es el mismo cálculo por modo que `run010.py` (línea 50), usado aquí como contraste.
- Campos: T1 genérico (a = (0,8+0,3i; −0,5+0,9i)), T2 destructivo (a = (1; −1)), T4 constructivo (a = (1; 1)) y T3 fuera del span (T1 más un residuo aleatorio de semilla fija, 0,3 veces su norma).

## Bloque 1 (preregistrado)

| Criterio | Umbral | Valor máximo | Veredicto |
|---|---|---|---|
| B1 reconstrucción con base dual | < 10⁻¹² | 3,3·10⁻¹⁵ | cumple |
| B2 η_D ≤ 1 en todos los casos | ≤ 1 + 10⁻¹² | 1 + 3·10⁻¹⁵ | cumple |
| B3 recuperación de coeficientes | < 10⁻¹⁰ | 4,8·10⁻¹⁵ | cumple |
| V1 biortogonalidad | < 10⁻¹² | 1,0·10⁻¹⁵ | cumple |
| V2 cruce con `lstsq` | < 10⁻¹⁰ | 4,8·10⁻¹⁵ | cumple |
| V3 caso analítico R² (recupera (1; −1)) | < 10⁻¹² | 3,1·10⁻¹⁶ | cumple |
| V4 caso analítico R² (η_A = 1 + G₁₂ = 1,6) | < 10⁻¹² | 0 | cumple |
| D1 cierre P_tot = P_g + P_r (T3) | < 10⁻¹² | 4,6·10⁻¹⁵ | cumple |
| P1 (predicción) η_A > 1 en T4 con \|G₁₂\| ≥ 0,6 | — | η_A = 1,601 (δ = 0,5); 1,612 (δ = 0,1) | cumple |

- Rango de solape del bloque 1: \|G₁₂\| = 0,001 a 0,612 (cond(G) = 1,0 a 4,2). Este bloque no llega a solape alto.
- Lectura de B2: en campos dentro del span, η_D = 1 hasta el redondeo. Para T3, η_D ≈ 0,917. La cota η_D ≤ 1 se cumple por construcción, porque la proyección ortogonal no puede aumentar la norma. Por eso B2 verifica la implementación, no la física. La parte informativa es el contraste con el método A.
- **Contraste con el método A (GLASS-010):** para T4 (constructiva), η_A = 1,09 (δ = 4), 1,43 (δ = 2), 1,57 (δ = 1), 1,60 (δ = 0,5) y 1,61 (δ = 0,1). Es decir, la suma por modo supera la potencia total, mientras que η_D no. Para T1, η_A llega a 1,08 (δ = 1) y 1,30 (δ = 0,1).
- Los resultados de V3 y V4 son analíticos y los dos cumplen. Confirman el cálculo de η_A, que da 1 + G₁₂ = 1,6.

## Bloque 2 (barrido adicional, post hoc)

Declaración: se añadió después de ver el bloque 1, porque su solape máximo (0,61) es bajo. Usa k₂ = 0 y δ ∈ {0,5; 0,1; 0,05; 0,02} µm, con los mismos umbrales. No cambia el veredicto del bloque 1.

| Criterio | Valor máximo | Veredicto |
|---|---|---|
| B1 | 2,1·10⁻¹¹ (T2, δ = 0,02, cond 8,0·10⁴) | **falla** (umbral 10⁻¹²) |
| B2 | 1 + 9,4·10⁻¹⁴ | cumple |
| B3 | 3,3·10⁻¹¹ | cumple |
| V1 | 1,1·10⁻¹¹ | **falla** (umbral 10⁻¹²) |
| V2 | 3,3·10⁻¹¹ | cumple |
| D1 | 4,2·10⁻¹¹ (T2, δ = 0,02) | **falla** (umbral 10⁻¹²) |
| P1 | η_A(T4) = 1,98 a 2,00 | cumple |

- B1 pasa en T2 con δ = 0,05 (4,2·10⁻¹³) y falla en δ = 0,02. El límite de 10⁻¹² se cruza entre cond ≈ 1,3·10⁴ y 8·10⁴.
- P2, la escala de B3: el error de B3 se mantiene entre 0,07 y 5,9 veces cond(G)·ε_máquina. Es decir, el error crece con el número de condición, como se espera.
- Interpretación (no medida por separado): en T2 la norma de ψ es pequeña cuando los modos casi coinciden, y eso amplifica los errores relativos de B1 y D1. La causa de V1 no se desglosó por caso; el JSON guarda solo el máximo.

## Lo calculado y lo supuesto

- **Calculado por el código:** todas las cifras y todos los pass de ambos bloques. Los modos sintéticos, la malla y los coeficientes son supuestos de diseño, fijados en el contrato.
- **Supuesto:** que la forma gaussiana con fase representa un modo cuasi-ligado. Es una hipótesis de diseño, no un resultado.

## Lo que no se afirma (pendiente)

1. **Aplicación a GLASS-010 original: pendiente.** Requiere los modos de trinchera con fuga del solver (`run010.py`) y su producto bilineal. Esta prueba sintética no los contiene. Va en un contrato aparte.
2. **Convención bilineal de un operador no hermítico: no probada.** Aquí la base dual está en span(Φ) y se construye con el producto hermítico. En un operador no hermítico, los vectores por la izquierda son los modos adjuntos, que no tienen por qué estar en span(Φ). En ese caso cambiaría el reparto del residuo, es decir D1. Pendiente.
3. **η_D por modo: no evaluado.** En bases oblicuas, la fracción de un modo individual no tiene por qué quedar en [0, 1]. Esta ronda solo evalúa la fracción total.
4. **Modos sintéticos:** gaussianos con fase, no soluciones de un operador. No son los modos de GLASS-010.
5. **JEV:** se consultó `router.py plan` (remote_decision = true; ejecutor main_agent; esfuerzo medio; sin segunda opinión). La salida no trae campo `provenance=jev`, así que no cuenta como decisión de JEV. No se ejecutó `router.py jev`.

## Archivos

- `CONTRATO-BIORT-r4.md`
- `biortogonal_sintetico.py`
- `resultados_biort.json`
- `RESULTADOS-BIORT.md` (este archivo)
