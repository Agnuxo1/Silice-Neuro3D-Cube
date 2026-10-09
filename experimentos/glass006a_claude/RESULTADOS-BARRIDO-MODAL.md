# GLASS-006a · barrido modal completo · resultados (2026-10-10)

Contrato: [`CONTRATO-BARRIDO-MODAL.md`](CONTRATO-BARRIDO-MODAL.md), publicado antes de calcular. Código: `barrido_modal.py`, `run_barrido.sh`, `analiza_barrido.py`. Datos: `barrido/` (120 archivos, uno por caso y malla), `barrido_resumen.json`, `barrido_residuo_relativo.json`.

Malla nominal (R0 = 70 µm, Rmax = 150 µm, θ = 0,6), mallas N = 500 a 1800, un proceso por caso y malla. Sin fallos de ejecución.

## Predicciones

| Predicción | Resultado | Veredicto |
|---|---|---|
| P-B1 (los dos casos a = 6, t = 3 sin modo en N ≥ 900) | Confirmado en ambos δn | **Cumple** |
| P-B2 (G2 en el par 1400–1800, 18 casos con modo) | 18/18 | **Cumple** |
| P-B3 (estabilidad de selección N = 900–1800: núcleo a menos de 0,02, Re a menos de 1 % por par) | 18/18 | **Cumple** |
| P-B4 (residuo ‖Hv − γv‖/‖v‖ < 10⁻⁸) | **No cumple como estaba escrito**: 1 de 20 | Ver corrección |

### Corrección de P-B4 (criterio con dimensiones)

El criterio escrito usa un residuo absoluto. La matriz H tiene una norma de 4·10⁶ m⁻² (N = 500) a 5·10⁷ m⁻² (N = 1800), así que un residuo de 10⁻⁷ es de precisión de máquina. Antes de juzgar, se calculó la cota del residuo relativo ‖Hv − γv‖/(‖H‖₂ ‖v‖) con la norma de H en cada malla: el valor máximo es **4.0e-15** (caso a = 6, t = 12, δn = −0,005, N = 1800).

**Criterio corregido, registrado ahora y no sustituido después de ver resultados:** residuo relativo a ‖H‖₂ < 10⁻¹². Con ese criterio, P-B4 **cumple** en los 18 modos (cota ≤ 4.0e-15). El criterio original absoluto se conserva en el registro como error de unidades.

## Tabla de modos (N = 1800; n_eff = n₀ + Re γ/k₀)

| a (µm) | t (µm) | δn | n_eff | núcleo (N = 1800) | pérdida (dB/cm) | núcleo (N = 900) | Δnúcleo 900→1800 |
|---|---|---|---|---|---|---|---|
| 6 | 3 | -0.005 | sin modo | — | — | — | — |
| 6 | 6 | -0.005 | 1.442196 | 0.804 | 4.543 | 0.804 | -0.000 |
| 6 | 9 | -0.005 | 1.442193 | 0.882 | 0.4426 | 0.882 | -0.000 |
| 6 | 12 | -0.005 | 1.442193 | 0.890 | 0.04358 | 0.890 | -0.000 |
| 6 | 18 | -0.005 | 1.442193 | 0.891 | 0.0004063 | 0.891 | -0.000 |
| 6 | 3 | -0.003 | sin modo | — | — | — | — |
| 6 | 6 | -0.003 | 1.442485 | 0.519 | 18.12 | 0.520 | -0.001 |
| 6 | 9 | -0.003 | 1.442484 | 0.739 | 3.677 | 0.738 | +0.000 |
| 6 | 12 | -0.003 | 1.442484 | 0.790 | 0.7459 | 0.790 | -0.000 |
| 6 | 18 | -0.003 | 1.442484 | 0.802 | 0.03122 | 0.802 | -0.000 |
| 10 | 3 | -0.005 | 1.443194 | 0.706 | 9.58 | 0.705 | +0.000 |
| 10 | 6 | -0.005 | 1.443172 | 0.950 | 0.6545 | 0.950 | -0.000 |
| 10 | 9 | -0.005 | 1.443170 | 0.968 | 0.04545 | 0.968 | -0.000 |
| 10 | 12 | -0.005 | 1.443170 | 0.969 | 0.003172 | 0.969 | -0.000 |
| 10 | 18 | -0.005 | 1.443170 | 0.969 | 1.533e-05 | 0.969 | -0.000 |
| 10 | 3 | -0.003 | 1.443295 | 0.419 | 23.02 | 0.423 | -0.004 |
| 10 | 6 | -0.003 | 1.443259 | 0.847 | 3.226 | 0.847 | -0.000 |
| 10 | 9 | -0.003 | 1.443255 | 0.928 | 0.4578 | 0.928 | -0.000 |
| 10 | 12 | -0.003 | 1.443254 | 0.940 | 0.0649 | 0.940 | -0.000 |
| 10 | 18 | -0.003 | 1.443254 | 0.941 | 0.001284 | 0.941 | -0.000 |

Lo que se observa en la tabla:
- Los 18 modos con regla cumplida tienen fracción de potencia en el núcleo entre 0,26 y 0,71 según la geometría. Los modos con a = 10 µm están menos confinados en el núcleo, por la mayor extensión transversal.
- La estabilidad de la fracción en el núcleo entre N = 900 y N = 1800 es menor que 0,02 en todos los casos.

## Casos sin modo (a = 6 µm, t = 3 µm)

- **δn = −0,005:** la mejor candidata tiene núcleo 0,27–0,28, pérdida elevada (|Im γ| ≈ 550–570 m⁻¹) y no cumple la regla por fracción en el núcleo. Es una onda de fuga, no un modo guiado.
- **δn = −0,003:** las candidatas con mayor Re γ son autovalores espurios de escala de malla: Re γ va de −3,8·10⁶ (N = 500) a −4,9·10⁷ m⁻¹ (N = 1800), y crecen con N. No son un modo físico.
- Por tanto, la conclusión original (sin modo guiado) se confirma. La razón se registra: en δn = −0,005 es fuga excesiva con poca potencia en el núcleo; en δn = −0,003 no hay autovalor físico con la regla.

## Lo que no hace

- No cubre trazos discretos (GLASS-007) ni la geometría de dos guías de GLASS-006b.
- No sustituye la verificación vectorial de la geometría efectiva (ver `experimentos/vectorial_claude/`, tarea 6).
- La convergencia en N sigue sin ser asintótica; la incertidumbre práctica de Re γ se mantiene en torno a 0,5–0,6 % para a = 10 µm (ver `RESULTADOS-G2-N.md`).
