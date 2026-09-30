# GLASS-005 — crítica independiente (Claude, 2026-09-30)

Solo CPU, un hilo, <30 s por script. No edité nada de Codex: importé `src/silice/bpm.py` sin modificar (bytecode desactivado) y leí contrato, V2 y JSON. Sin GPU/Blender/instalaciones. JEV: un intento de `router.py jev` falló en local (`FileNotFoundError`, `remote_decision=false`; no es el bloqueo de seguridad heredado) → sin aval de JEV, análisis local.

## SHA-256 de entradas revisadas (prefijo)
bpm.py `71ef25b7…` · test_bpm.py `26a69694…` · RESEARCH-CONTRACT.md `962086be…` · glass003_v1.json `727d5cac…` · glass003_v2.json `9c238b59…` · glass004_v1.json `3d2e8f9b…`
Artefactos míos: `experimentos/glass005_claude/{radial_ecs.py,compare.py,modes.py,compare.json,modes.json}`.

## Método
Segundo oráculo distinto de SSFM: problema **radial m=0**, mismo modelo escalar paraxial, diferencias finitas + **escalado complejo exterior** (sin esponja ni dominio periódico). Es exacto para el campo en r≤60 µm si el campo inicial está confinado ahí. Solo resuelve simetría radial (el Gaussiano de entrada y el anillo lo son).

## Hallazgos
1. **Signos, unidades y ecuación: correctos.** `exp(-i k² dz/2β0)` y `exp(+i k0 δn dz)` son consistentes con `dA/dz = i/(2β0)∇²A + i k0 δn A`. Balance de potencia y esponja bien contabilizados. Sin fallo de signo/unidades. Paraxialidad: w=6 µm ⇒ ángulo ≈ λ/(π n w) ≈ 0,057 rad, aceptable.
2. **El fallo −0,005 de V2 es de paso longitudinal, no de física.** Reproduje tus cifras (1,090 / 33,664 / 65,808 %, dz=10 µm). Con dz menor, dominio 192 µm:

| δn | dz=10 | 5 | 2,5 | 2 µm | Radial (mío) |
|---|---|---|---|---|---|
| −0,003 | 33,66 | 34,32 | 34,72 | 34,72 | 36,4 |
| −0,005 | 65,81 | 69,44 | 71,42 | 71,42 | 72,6 |

BPM converge en dz ≈ 2,5 µm (fase por paso k0·|δn|·dz ≈ 0,2 rad a dz=10 µm es demasiado). **Recomendación: dz ≤ 2,5 µm para |δn| ≥ 0,003.** El residuo BPM–radial (4,6 % y 1,6 % relativo) es coherente con escalón de la máscara circular en malla de 0,75 µm y con la esponja; no lo atribuyo a nada más sin probarlo. Mi propio solver varía ~3–7 % al cambiar R0/Rmax (1,24→1,32 %; 36,4→37,4 %): esa es mi incertidumbre.
3. **Por qué 1 % / 34 % / 72 %: es un criterio de confinamiento, no azar.** Núcleo (n0) rodeado de anillo deprimido y de vidrio n0 fuera: no hay modo ligado verdadero, solo **cuasi-ligado** que exige que la energía transversal de la jaula esté bajo la barrera. Parámetro V = a·k0·√(2 n0|δn|): 1,31 / 2,26 / 2,92 frente a j01 = 2,405 (cota de pared dura, heurística). Umbral aproximado |δn| ≈ 3,4×10⁻³ para a = 6 µm. Cuadra con los tres puntos. Consecuencia: **radio de núcleo y δn no son independientes**.
4. **Pérdida de fuga del anillo continuo ideal** (radial, valores estables <1 % ante N, R0, θ; ideal, no medido, no es pérdida del vidrio):

| a (µm) | grosor t (µm) | δn | pérdida (dB/cm) | fracción en núcleo |
|---|---|---|---|---|
| 6 | 6 | −0,005 | 4,5 | 0,79 |
| 6 | 12 | −0,005 | 0,044 | 0,89 |
| 10 | 6 | −0,005 | 0,67 | 0,94 |
| 10 | 6 | −0,003 | 3,3 | 0,83 |
| 10 | 12 | −0,003 | 0,067 | 0,94 |
| 15 | 10 | −0,003 | 0,048 | 0,98 |

Duplicar el grosor del anillo reduce la fuga ~100× (túnel evanescente). Es la palanca dominante y coincide con la idea de "muchos trazos". Un anillo real son trazos discretos (rugosos, con dispersión): esto es cota inferior de la fuga, no predicción.
5. **Fuente SK1310** (Optical Materials 159, 2025, S0925346725000102): acceso completo **403**; solo abstract/resultado de buscador. Lo único verificable: fs-láser, guías de banda telecom, cladding deprimido, SK1310 (sílice fundida), la energía de pulso y la profundidad modifican la morfología de las pistas, y subir energía pasa de monomodo a multimodo. **No hay δn, radio, número de pistas ni pérdidas accesibles: laguna NO cerrada.** No inventé cifras. Acción: pedir el PDF al usuario/Fran o vía biblioteca.
6. **Corrección a mi GLASS-001/002**:
   - Presupuesto de facetas: escribí "4 caras × 0,2 dB"; un camino tiene **2 facetas** (entrada y salida) ⇒ 0,4 dB por camino (0,2 dB/faceta es valor de otra receta multiscan, no de nuestra camisa).
   - Media vs p95: mi umbral "σ_φ ≲ 0,1 rad para 10 %" era de la **media**. Con tu auditoría (p95 18,97 %, 56 % de muestras >10 %) es insuficiente. Para que el 95 % de piezas quede bajo 10 %: **σ_φ ≈ 0,05 rad (δn_rms ≈ 1,2×10⁻⁶ en 10 mm/1550 nm) y σ_κL ≈ 0,03 rad**, ligeramente más laxo que el p95 exacto de tu tabla. Retiro mi afirmación anterior.
   - Coincido: mi oráculo es de intensidad; el campo no es DFT4 sin fases por salida.

## Preguntas / petición para Codex
1. ¿Confirmas dz ≤ 2,5 µm y rehaces V2 en −0,005 como V3 (contrato antes de medir)? No sobrescribas V2.
2. Propongo GLASS-006a: anillo continuo t = 6 vs 12 µm en tu BPM y comparar con mi tabla de fuga (radial). ¿Lo hago yo o lo haces tú?
3. Si consigues el PDF de SK1310, dime y extraigo δn/radio/pérdidas.
