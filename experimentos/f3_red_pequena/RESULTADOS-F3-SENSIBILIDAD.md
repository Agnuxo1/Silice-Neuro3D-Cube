# T12 (control) · sensibilidad de la red F3-b a V_π y θ_b · resultados (2026-10-10)

Contrato: `CONTRATO-F3-SENSIBILIDAD.md`. Código: `sensibilidad_control.py`. Datos: `sensibilidad_resultados.json`. El modelo A no se reentrena: se evalúa el mismo vector de parámetros entrenado con los parámetros de control cambiados.

## Comprobaciones

| Criterio | Valor | Veredicto |
|---|---|---|
| S1: reproducción en (V_π = 1, θ_b = 0) | diferencia 0,0 en entrenamiento y en prueba | cumple (umbral 10⁻¹²) |
| S2: rango de exactitud de prueba en la rejilla | 0,1485 (de 0,535 a 0,684) | sensible (umbral descriptivo 0,05) |

## Rejilla (exactitud)

| V_π | θ_b (rad) | entrenamiento | prueba |
|---|---|---|---|
| 0,5 | −π/4 | 0,6175 | 0,6185 |
| 0,5 | 0 | 0,5845 | 0,5930 |
| 0,5 | +π/4 | 0,5250 | 0,5350 |
| 1,0 | −π/4 | 0,6640 | 0,6595 |
| **1,0** | **0 (entrenado)** | 0,6530 | **0,6425** |
| 1,0 | +π/4 | 0,6045 | 0,5950 |
| 2,0 | −π/4 | 0,6505 | 0,6515 |
| 2,0 | 0 | 0,6735 | 0,6835 |
| 2,0 | +π/4 | 0,6565 | 0,6740 |

## Lectura

- La exactitud depende de V_π y de θ_b. El punto entrenado (V_π = 1, θ_b = 0) no es el máximo de la rejilla.
- **Ese máximo no se usa para elegir nada.** El contrato prohíbe seleccionar sobre prueba. Escoger V_π = 2 porque mejora la prueba sería selección sobre prueba. Cambiar el punto de control exige reentrenar y seleccionar sobre entrenamiento o validación.
- La conclusión de H-F1 no depende del punto de control: **ningún punto de la rejilla alcanza 0,70** (máximo 0,6835). H-F1 sigue sin cumplirse.

## Límites

- Es sensibilidad sin reentrenamiento. Un modelo reentrenado en cada punto podría comportarse de otra manera.
- Es un modelo numérico. No hay medida de V_π ni de θ_b en un dispositivo.
