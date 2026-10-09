# GLASS-006a · diagnóstico del fallo de G2 en a = 10 µm · contrato prospectivo (2026-10-09)

Este contrato se publica **antes** de ejecutar el diagnóstico. No reemplaza ni modifica `resultados.json`, que conserva los resultados originales, incluidos los fallos de G2.

## Pregunta

En los diez casos de radio a = 10 µm, la constante de propagación Re γ no cumple G2 (cambio < 1 % entre configuraciones). Los casos de a = 6 µm sí cumplen. ¿Qué parámetro numérico causa el cambio: la malla (N, θ) o el dominio (R0, Rmax)?

## Método

Un factor cada vez, sobre la configuración nominal, con el mismo solver y la misma selección de modo que `run006a.py`:

| Configuración | N | R0 (µm) | Rmax (µm) | θ | Factor que cambia |
|---|---|---|---|---|---|
| nom | 500 | 70 | 150 | 0,6 | — (referencia) |
| Nx | 700 | 70 | 150 | 0,6 | malla |
| Th | 500 | 70 | 150 | 0,8 | malla (θ) |
| Dom | 500 | 90 | 200 | 0,6 | dominio |
| B | 700 | 90 | 200 | 0,5 | combinación de la config. B original (reproducción) |

Casos: a = 10 µm con t ∈ {3, 6, 9, 12, 18} µm y δn ∈ {−0,003, −0,005} (diez casos). Selección de modo: `cands` de `run006a.py` (|Im γ| < 3000 m⁻¹, fracción de potencia en el núcleo > 0,3, mayor Re γ). Se reportan todos los candidatos.

## Predicciones y reglas fijadas

- **P1 (reproducibilidad).** Las configuraciones nom y B reproducen los valores guardados en `resultados.json` con error relativo ≤ 10⁻⁶ en Re γ. Si P1 falla, el entorno de cálculo no coincide con el original; el diagnóstico se detiene y se documenta.
- **P2 (atribución).** Para cada caso, Δ_B = |Re γ_B − Re γ_nom| / |Re γ_nom|. El factor responsable es el que, cambiado solo, produce |Re γ_factor − Re γ_nom| / |Re γ_nom| ≥ 0,5 Δ_B. Si ninguno llega al 50 %, la causa se declara **no atribuida** y se registra.
- **P3 (sin predicción de dirección).** No se predice si el factor responsable será malla o dominio. El resultado se registra tal cual.

## Lo que este contrato no hace

- No declara un veredicto nuevo de G2. Un veredicto nuevo exige otro contrato con una configuración corregida, declarada antes de ejecutarla.
- No reajusta umbrales. G2 sigue siendo cambio relativo < 1 % en Re γ.
- No sustituye ni borra resultados históricos.

## Ejecución

Un proceso por caso, cada uno por debajo de 30 s en un hilo (regla del repositorio). Salida: `diag_g2_radius10.json`, con los valores de cada configuración por caso y los dos cocientes de P2.
