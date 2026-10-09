# Tarea 3 · reflexión del absorbente frente al ángulo · resultados (2026-10-10)

Contrato: [`CONTRATO-ABSORBENTE.md`](CONTRATO-ABSORBENTE.md). Código: `absorbente_pml.py`. Datos: `absorbente_resultados.json`.

Problema de onda completa en una dimensión: capa absorbente (PML) de espesor D, σ(x) = σ_max (x/D)², pared perfecta, diseño R₀ = 10⁻⁴ a incidencia normal. Ecuación: (1/s) d/dx[(1/s) du/dx] + κ²u = 0, s = 1 + iσ/k₀n₀, κ = k₀n₀ sin θ.

## Validación

- **V0 (sin absorbente).** R = 1 para todo θ. Cumple.
- **V1 (incidencia normal).** R = 1.0000e-04 frente al diseño R₀ = 10⁻⁴. Cumple (error relativo 4·10⁻¹¹).

## Resultado principal: ley de reflexión rasante

| θ (rad) | R medida (D = 10 µm) | R₀^sinθ | desviación |
|---|---|---|---|
| 0.005 | 9.5499e-01 | 9.5499e-01 | 0.00 % |
| 0.01 | 9.1201e-01 | 9.1201e-01 | 0.00 % |
| 0.02 | 8.3177e-01 | 8.3177e-01 | 0.00 % |
| 0.04 | 6.9190e-01 | 6.9190e-01 | 0.00 % |
| 0.08 | 4.7901e-01 | 4.7901e-01 | 0.00 % |
| 0.16 | 2.3053e-01 | 2.3053e-01 | 0.00 % |
| 0.3 | 6.5754e-02 | 6.5754e-02 | 0.00 % |
| 0.7 | 2.6493e-03 | 2.6493e-03 | 0.00 % |
| 1.2 | 1.8700e-04 | 1.8700e-04 | 0.00 % |
| 1.571 | 1.0000e-04 | 1.0000e-04 | 0.00 % |

**R(θ) = R₀^(sin θ)** con desviación máxima relativa de 0.00 % en todo el rango. Es una ley cerrada: la atenuación total del absorbente que ve un haz de ángulo θ es ln(1/R₀)·sin θ.

## Predicciones

| Predicción | Resultado | Veredicto |
|---|---|---|
| P-T1 R(0,04 rad) < 10⁻³ para D = 10 µm | R = 0.692 | **No cumple** |
| P-T2 R(0,01) > R(0,04) (más reflexión al ser más rasante) | 0.912 > 0.692 | **Cumple** |
| P-T3 D = 20 µm reduce R en todo el rango | R idéntica en D = 5, 10 y 20 µm | **No cumple** |

**Motivo de P-T3.** Con un diseño fijo en R₀, la absorción integrada ∫σ dx = ln(1/R₀)/2 no depende de D. Aumentar D solo cambia la pendiente de σ, no la absorción total. La predicción era errónea.

## Consecuencias para el proyecto

- El absorbente lateral de **este tipo** no atenúa componentes casi paralelos al eje (θ ≲ 0,1 rad). Con R₀ = 10⁻⁴, a θ = 0,04 rad refleja un 69 %. Para llegar a R < 10⁻³ a θ = 0,04 rad haría falta R₀ ≈ 10⁻⁷⁵, impracticable.
- El límite θ > 0,04 rad de GLASS-009c es **insuficiente** para descartar reflexión: a ese ángulo el absorbente refleja mucho. Ese límite debe revisarse, o se debe usar otro tratamiento de frontera (dominio mayor con ventana temporal, filtrado angular, o absorbente que no dependa de θ).
- El efecto no depende de D. Aumentar el dominio no basta.

## Lo que no hace

- Una dimensión, sin estructura de guía, sin pérdida de material. La reflexión se mide para una onda plana con κ dado, no para el haz de BPM.
- El esquema de BPM de `src/silice/bpm.py` usa una esponja exponencial, no una PML. Esta comprobación no cubre esa esponja; cubre una PML equivalente.
