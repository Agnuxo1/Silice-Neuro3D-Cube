# F3-b · red funcional de dos capas con activación optoelectrónica · resultados (2026-10-10)

Contrato: [`CONTRATO-F3-RED-FUNCIONAL.md`](CONTRATO-F3-RED-FUNCIONAL.md), publicado antes de entrenar. Código: `run_f3b.py` (un inicio por proceso; selección por pérdida de entrenamiento). Datos: `f3b_seeds/` (16 archivos), `f3b_resultados.json`, `f3b_aggregate.json`.

**Resultado negativo para H-F1 y H-F2.** La activación optoelectrónica con segunda capa mejora la malla de una capa, pero queda muy por debajo de la red electrónica de la misma topología.

## Hipótesis

| Hipótesis | Criterio | Valor | Veredicto |
|---|---|---|---|
| H-F1 exactitud de A | ≥ 0,70 | 0.6425 | **No cumple** |
| H-F2 frente a B (misma topología) | A ≥ B − 0,02 | A = 0.6425, B = 0.8455; diferencia emparejada -0.2024, IC95 [-0.2200; -0.1840] | **No cumple** |
| H-F3 mejora frente a una capa (F3 M1 = 0,5905) | diferencia emparejada > 0, IC95 excluye 0 | +0.0524, IC95 [+0.0190; +0.0840] | **Cumple** |

## Modelos

| Modelo | Parámetros | Exactitud train | Exactitud prueba | Mejor inicio (pérdida mínima) |
|---|---|---|---|---|
| A: malla unitaria → activación MZM → malla unitaria | 32 | 0.653 | 0.6425 | semilla 5 de 8 |
| B: pesos reales, misma topología y activación | 32 | 0.847 | 0.8455 | semilla 7 de 8 |

## Lectura

- **La segunda capa y la activación aportan capacidad.** H-F3 se cumple: A supera la malla de una capa del contrato F3 (59 %) con intervalo emparejado por encima de cero.
- **La restricción unitaria sigue siendo el límite principal.** Con igual topología y activación, pesos reales llegan a 84.5 %, y las mallas unitarias a 64.2 %. La diferencia no es de optimización: los entrenamientos de A convergen en un rango estrecho de pérdida.
- **Lo que esto significa para el proyecto.** La red funcional definida aquí (detección, activación, entrenamiento y control) existe como modelo, pero sin pesos reales no es competitiva en esta tarea. La no linealidad optoelectrónica no compensa la unitariedad.

## Límites

- Activación con electrónica de control y fotodetector: no es una red totalmente óptica.
- Tarea sintética con semillas fijas; no generalizable.
- Sin medidas ni energía. Modelo numérico, no dispositivo.
- Parámetros de modulador fijos (V_π = 1, θ_b = 0), sin búsqueda sobre prueba.
