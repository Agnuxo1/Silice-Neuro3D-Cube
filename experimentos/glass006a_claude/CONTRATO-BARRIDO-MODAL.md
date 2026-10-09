# GLASS-006a · barrido modal completo · contrato prospectivo (2026-10-10)

Publicado antes de calcular. Cierra la tarea 2 del encargo: barrido modal completo, casos sin modo seleccionado, residuales, estabilidad de selección y convergencia. Continúa `CONTRACT-G2-DIAG.md`, `CONTRACT-N-CONV.md` (E2, E3) y `RESULTADOS-G2-N.md`, sin modificar sus resultados.

## Alcance

- **Casos:** los 20 de GLASS-006a: a ∈ {6, 10} µm; t ∈ {3, 6, 9, 12, 18} µm; δn ∈ {−0,003, −0,005}. Incluye los dos casos sin modo original (a = 6, t = 3, ambos δn).
- **Mallas:** N ∈ {500, 700, 900, 1100, 1400, 1800}, dominio nominal (R0 = 70 µm, Rmax = 150 µm) y θ = 0,6. Mismas mallas que en los contratos anteriores.
- **Solver:** `radial_ecs.build` (GLASS-005), sin cambios.

## Qué se registra por caso y malla

1. **Ocho primeros autovalores** ordenados por Re γ: Re γ, Im γ, fracción de potencia en el núcleo (`core`).
2. **Selección del modo** con la regla histórica de `run006a.py`: |Im γ| < 3000 m⁻¹, `core` > 0,3, y de ellos el de mayor Re γ.
3. **Residual del autovalor elegido:** ‖H v − γ v‖ / ‖v‖ con H la matriz del solver. Verifica que el autovalor es numéricamente válido.
4. **Caso sin modo:** si ningún autovalor cumple la regla, se registra el candidato con mayor `core` y el motivo de exclusión (|Im γ| o `core`).

## Criterios

- **Convergencia (histórica, G2):** pérdida con cambio relativo < 10 % o absoluto < 0,005 dB/cm; Re γ con cambio relativo < 1 %, para el par (1400, 1800).
- **Estabilidad de selección (nueva):** entre N = 900 y N = 1800, el modo elegido tiene `core` que varía menos de 0,02 y Re γ con cambio relativo menor que el 1 % en cada par consecutivo.
- **Residual (nuevo):** ‖Hv − γv‖/‖v‖ < 10⁻⁸ en todas las mallas.

## Predicciones fijadas

- **P-B1 (sin modo).** Los dos casos a = 6, t = 3 no tienen modo que cumpla la regla en N ≥ 900. Si alguno sí la cumple, la clasificación original cambia y se registra.
- **P-B2 (convergencia).** Todos los casos con modo cumplen G2 en el par (1400, 1800).
- **P-B3 (estabilidad).** Todos los casos con modo cumplen la estabilidad de selección de N = 900 a 1800.
- **P-B4 (residual).** Todos los residuales cumplen < 10⁻⁸.

Si una predicción falla, se publica el fallo y se explica. No se cambian los umbrales.

## Lo que no hace

- No prueba convergencia asintótica (ya documentado en `RESULTADOS-G2-N.md`).
- No cambia el dominio ni θ. El efecto de dominio se midió en `CONTRACT-N-CONV.md`.
- No trata trazos discretos (GLASS-007).

## Ejecución

Un proceso por caso y malla (límite de 30 s). Salida en `barrido/`, resumen en `barrido_resumen.json`.
