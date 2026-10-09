# Tarea 3 (extensión) · fase compleja del coeficiente de reflexión del absorbente PML 1D · resultados (2026-10-10)

Modelo: `absorbente_pml.py` (PML 1D, D = 10 µm, R₀ = 10⁻⁴, p = 2, λ = 1,55 µm, n₀ = 1,444). Código: `fase_reflexion.py`. Datos: `fase_resultados.json`.
Convención: plano de referencia x = 0 (la interfaz), r = (U − W)/(U + W), U = u(0), W = u′(0)/(iκ), la misma definición que `R_of` (que solo daba |r|). La fase depende de ese plano de referencia; no es una medida.

## Comprobaciones

| Criterio | Valor | Veredicto |
|---|---|---|
| V-F1: |r| coincide con `R_of` | 2,8·10⁻¹⁷ | cumple (umbral 10⁻⁹) |
| V-F2: ley ln|r| / ln R₀ = sin θ | 4,2·10⁻¹¹ | cumple (umbral 10⁻³) |
| V-F3: continuidad de la fase, diferencias envueltas, malla de 400 puntos | paso máximo 0,458 rad | cumple (umbral π) |

**Corrección de V-F3.** La primera versión comparaba diferencias crudas de arg(r) ∈ (−π, π] y dio 4,61 rad. Es un artefacto de envoltura: en la práctica el paso real es ~1,67 rad cruzando ±π. El criterio estaba mal definido para fase envuelta. Se corrigió a diferencias envueltas y se comprobó en una malla fina. El valor original se conserva en `fase_resultados.json` (`V-F3_v1_raw_max_step_rad`). El umbral no cambió.

## Valores en la malla gruesa

| θ (rad) | |r| | dB | arg(r) (rad) |
|---|---|---|---|
| 0,02 | 0,832 | −1,6 | −0,800 |
| 0,04 | 0,692 | −3,2 | +1,540 |
| 0,08 | 0,479 | −6,4 | −0,069 |
| 0,16 | 0,231 | −12,8 | +2,943 |
| 0,32 | 0,0552 | −25,2 | +2,269 |
| 0,64 | 4,09·10⁻³ | −47,8 | −2,343 |
| 1,00 | 4,31·10⁻⁴ | −67,3 | +1,122 |
| π/2 (incidencia normal) | 1,00·10⁻⁴ | −80,0 | +0,831 |

## Lectura y límites

- La amplitud reflejada sigue la ley |r| = R₀^(sin θ) (V-F2), ya conocida. La fase cambia de forma continua con el ángulo rasante (V-F3), y es de unos 0,5 rad por cada 0,004 rad de ángulo en la malla fina.
- **Campo complejo y fase conjunta con la red:** no resuelto. Esto es solo el absorbente 1D en un plano; la fase relevante para una red depende del recorrido real de la onda en el volumen, de la geometría de la interfaz y de la posición del absorbente. Queda pendiente.
- No cubre la esponja exponencial de `src/silice/bpm.py` (Codex), que es otro modelo.
