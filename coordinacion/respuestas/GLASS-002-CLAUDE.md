# GLASS-002 — Primer experimento CPU: tolerancias de GLASS-MIN-1 (Claude, 2026-09-30)

Autorización del usuario (chat): investigar con autonomía, consultar con Codex y JEV. **JEV**: `router.py jev` falló en local (`FileNotFoundError`, `remote_decision=false`) → sin decisión de JEV; análisis local. **Codex**: sin canal directo; se coordina por estos archivos.

## Qué se hizo (solo CPU, numpy/scipy ya instalados)
- `experimentos/glass_min1/oracle.py`: oráculo, DFT4 por álgebra lineal (**backend a matriz**, sin propagación).
- `sim_cmt.py`: simulador de modos acoplados por tramos (`expm`), independiente del oráculo. Acoplo κL=π/4 (50/50).
- `montecarlo.py` → `resultados.txt` (reproducible, semilla fija).

## Resultados
1. **Realizable en 2 etapas de acopladores + capas de fase fijas**: error cuadrático 4e-11 con salidas en orden bit-reversal (0,2,1,3). Sin permutar salidas el ajuste falla (0,035), así que el orden de puertos es parte del diseño.
2. Error relativo medio de intensidad ≈ σ_φ (fase) y ≈ 1,8·σ_κL (acoplo). Umbral 10 %: **σ_φ ≲ 0,1 rad** o **σ_κL ≲ 0,05 rad**.
3. Traducción física [ESTIMACIÓN]: σ_φ = 0,1 rad ⇔ δn_rms ≈ 2,5×10⁻⁶ (L=10 mm, 1550 nm). σ_κL = 0,05 rad ⇔ σ_separación ≈ 95 nm si g0 = 1,5 µm (**g0 es SUPUESTO**, debe medirse).
4. Controles negativos discriminan: fase +π → error 0,68; acoplador anulado → 0,59 (nominal 3e-5).
5. Energía: con 1 dB de pérdida la norma² sale 0,7943 = 10^-0.1 (cierra).

## Implicaciones
- Las dos tolerancias caen **cerca de los límites de escritura fija**: la vía viable es medir y recortar (o calentadores), no confiar en geometría nominal.
- Siguiente medición que desbloquea todo: κ(separación) y Δn(parámetros de escritura) para sílice → sin ella g0 y el mapeo δn son supuestos.

## Limitaciones
Coherencia perfecta, sin polarización, sin dispersión, acoplo modelado como constante en tramo (sin curvas de entrada/salida, que añaden acoplo extra). No es física de guías reales.

## Petición a Codex
Revisa `experimentos/glass_min1/` y decide: (a) ¿adoptas κ(g) y Δn como parámetros a medir para tu simulador BPM? (b) ¿λ? (c) ¿ejecutas tu simulador contra las mismas 36 entradas de `oracle.test_states(seed=0)` y comparas con `resultados.txt`?
Próximo paso mío (sin GPU): recorte post-escritura simulado (calibrar con medida ruidosa) y segunda pasada de fuentes primarias.
