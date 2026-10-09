# T12 · control: sensibilidad de la red F3-b a V_π y θ_b · contrato (2026-10-10)

Publicado antes de calcular. Es solo un análisis de sensibilidad: no hay reentrenamiento y no se elige nada sobre el conjunto de prueba. El modelo A se entrenó con V_π = 1 y θ_b = 0 (`CONTRATO-F3-RED-FUNCIONAL.md`). Aquí se evalúan los parámetros entrenados cambiando solo los dos parámetros de control.

## Diseño
- Parámetros entrenados: inicio con menor pérdida de entrenamiento (`f3b_seeds/a_s{semilla}.json`, semilla de `f3b_resultados.json`).
- Rejilla: V_π ∈ {0,5; 1; 2} y θ_b ∈ {−π/4; 0; π/4}. Nueve puntos.
- Métrica: exactitud en entrenamiento y en prueba en cada punto.

## Criterios (fijados ahora)
- **S1 (reproducción).** En (V_π = 1, θ_b = 0), la exactitud de entrenamiento y de prueba coincide con `f3b_resultados.json` a 10⁻¹². Si no coincide, el análisis no es válido.
- **S2 (descriptivo).** Se considera sensible a los parámetros de control si el rango de exactitud de prueba en la rejilla supera 0,05. Este umbral es descriptivo y se fija aquí.

## Qué no afirma
- No es un control real de un modulador: no hay medida de V_π ni del sesgo θ_b.
- No sustituye la fabricación ni la caracterización del dispositivo.
