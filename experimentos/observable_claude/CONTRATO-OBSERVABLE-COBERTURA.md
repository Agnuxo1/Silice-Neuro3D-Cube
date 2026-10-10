# Tarea H · Observable de potencia en el núcleo con área parcial y perfil por cobertura

Contrato prospectivo (2026-10-10, antes de ejecutar cálculos de H1 a H3). Carpeta: `experimentos/observable_claude/`. Autor: Claude (subagente de la tarea H).

Modelo numérico escalar paraxial en 2D, no un dispositivo. Separamos modelo, predicción y medida: aquí solo hay modelo y verificación numérica. Ningún resultado de esta tarea es una medida de laboratorio.

## Hipótesis

- **H-A (observable).** El observable original de 009 (`core_fraction` en `adi2d.py`, indicador `x²+y²<a²` en el centro de cada píxel) introduce un error de cuadratura de frontera que solo cae como O(h) si el núcleo es un disco. Pesar cada celda por la fracción de su área dentro del núcleo (cobertura) debería dar orden observado ≥ 2 en la guía de salto, con un límite inferior de 1,8.
- **H-B (009b/009d).** Si el observable cambia de centro a cobertura, algún veredicto Q2, Q3 o Q4 de 009d puede cambiar. Se prueba, no se supone.
- **H-C (réplica GLASS-007 V2).** Se busca en el repositorio. Hallazgo previo a este contrato: `Docs/GLASS-007-V2-CONTRACT.md`, `Docs/GLASS-007-V2-RESULTS.md` y `resultados/codex/glass007_v2_run1*.json` existen, aunque `coordinacion/tareas/PLAN-22-TAREAS-20261010.md` diga "GLASS-007 no está en el repositorio". No se usan como oráculo.

## Definiciones (fijadas aquí)

- Malla: `x_i = (i − N//2)·h`, `N = round(L/h)`, igual que `adi2d.coords`. Solo se importa el solver `adi2d.py` de `experimentos/glass009_claude/` para H3 (no se copia ni se modifica). Se registra su SHA-256.
- Cobertura `w_ij`: fracción del área de la celda de lado h centrada en `(x_i, y_j)` que cae en `r<a`. Método primario (H1): clasificación exacta de celdas interiores (`r_c < a − h/√2`, w=1) y exteriores (`r_c > a + h/√2`, w=0); en las celdas de frontera, submuestreo 64×64. Se reporta también el submuestreo 16×16 de 009b/009d.
- Observable original (O_c): `Σ_{r_ij<a} |ψ_ij|² h²` (indicador en centro).
- Observable de cobertura (O_w): `Σ w_ij |ψ_ij|² h²`.
- Perfiles de 009d (solo H3): modificación `δn = −0,003·cov_ij`, cov por submuestreo 16×16 (como 009d; el perfil no cambia).

## H1 · Reimplementación

Código nuevo en `observable_cobertura.py`, independiente del de 009b/009d (no se toca ningún archivo original).

Criterios (fijados ahora):
- **H1-G1** `|Σ w h² − π a²| / (π a²) < 1e-4` para h ∈ {0,8; 0,4; 0,2; 0,1; 0,05} µm.
- **H1-G2** `0 ≤ w ≤ 1`; w=1 en celdas con `r_c < a − h/√2` y w=0 en `r_c > a + h/√2` (cero excepciones).
- **H1-G3** el área total con submuestreo 16×16 (convención de 009b/009d) y con 64×64 difieren en `< 1e-4` relativo. Se reporta además `max|Δw|` por celda, sin criterio (la cuantización de 16×16 puede dar hasta ~1/16 por celda de frontera; no es un fallo).
(Revisión previa a cualquier cálculo: el criterio de `max|Δw| < 0,05` se sustituyó por el de área total, porque la cuantización por celda de 16×16 puede superar 0,05 sin ser un error.)

## H2 · Convergencia con h en la guía de salto

Referencia analítica. Guía de salto: `a = 6 µm`, `λ = 1,55 µm`, `n1 = 1,444`, `n2 = 1,439`, `k0 = 2π/λ`. `V = k0·a·√(n1²−n2²)`. Modo fundamental LP01 con `u²+w²=V²`, `u·J1(u)/J0(u) = w·K1(w)/K0(w)`, `u ∈ (0,V)`. Campo: `ψ = J0(u r/a)/J0(u)` en el núcleo y `ψ = K0(w r/a)/K0(w)` fuera, normalizado a potencia analítica total 1.

La integral analítica en el núcleo es `Γ = (1 + J1²(u)/J0²(u)) / (J1²(u)/J0²(u) + K1²(w)/K0²(w))`. Se verifica con cuadratura numérica de 1D (`scipy.integrate.quad`), no se acepta sin comprobación.

Protocolo: `ψ` analítico muestreado en nodos de la malla (no se usa un autovalor discreto), dominio L = 80 µm (semiancho 40 µm), h ∈ {0,8; 0,4; 0,2; 0,1; 0,05} µm. Error `e_h = O_h − Γ`.

Criterios (fijados ahora; no se cambian tras ver resultados):
- **H2-G0 (validez de la referencia).** Residuo de la ecuación de autovalor < 1e-10; `|Γ_cerrada − Γ_quad| / Γ < 1e-8`; potencia total analítica `|P_tot_quad − 1| < 1e-8`.
- **H2-G1 (criterio principal).** Orden observado del observable de cobertura `p_w = −d log|e_h| / d log h`, pendiente de mínimos cuadrados sobre h ∈ {0,4; 0,2; 0,1; 0,05}: **p_w ≥ 1,8**.
- **H2-G2 (sanidad).** Área relativa de cobertura < 1e-4 para cada h (ya en H1-G1).
- Se reportan también: orden del observable original (no gate), orden del par más fino (0,1 → 0,05) y el error absoluto en h = 0,05 de cada observable.

Lo que H2 no afirma: no es un orden asintótico certificado (solo cuatro mallas), no prueba que el solver ADI converja, y no cubre LP11 (V ≈ 2,9 > 2,405, el LP11 está guiado; el criterio solo mide el LP01).

## H3 · Recalcular Q2, Q3 y Q4 de 009d con cobertura

Solo cambia el observable. Se mantiene `adi2d.py`, λ, geometría, perfil de 009d, dz = 2,5 µm, 800 pasos, σmax = 4e4 m⁻¹ y dominio 128 µm. Se propagan de nuevo Cd y T96d con dx ∈ {0,5; 0,625; 0,4 (dos trozos de 400 pasos)}, un hijo por proceso, `OMP_NUM_THREADS=1`, `python -B`.

Para cada campo final se calculan tres observables: (a) el de 009d (cobertura 16×16, reproducción), (b) el de cobertura de H1 (64×64 en frontera), (c) el original (centro, indicador).

Criterios de 009d, sin cambios:
- **Q2 (continuo):** `|P(0,4) − P(0,5)| < 0,005` y `< 10 %`.
- **Q3 (96 trazos):** mismos umbrales.
- **Q4 (monotonía):** `|P(0,5) − P(0,625)| ≥ |P(0,4) − P(0,5)|` en ambos perfiles. Si falla se reporta, sin declarar convergencia.

Control previo: **R0** reproducción de (a) respecto a `resultados009d.json` (`|ΔP| < 1e-9`). Si R0 falla, H3 no es válido y se dice.

Veredicto: se declara si cada Q cambia respecto a 009d al cambiar el observable (a→b y a→c).

## Qué NO afirmo

- No afirmo que la cobertura sea "la" respuesta física; es un cambio de cuadratura del observable.
- No afirmo convergencia de 009d ni de 009b; solo compruebo sensibilidad al observable.
- No pruebo la réplica GLASS-007 V2 (no la reejecuto ni la uso de oráculo; se cita).
- No modifico `src/silice/`, `tests/`, `scripts/`, `coordinacion/`, `Docs/` ni los resultados de 009b/009d (solo leo).
- No hay GPU, Blender, instalación ni caché fuera de `D:`.
- Si un criterio falla, se publica como falla con sus cifras.

## Límites de tiempo y medio

- Límite de 30 s por proceso hijo (heredado de 009/009d), 1 hilo CPU, límite duro 05:50 UTC.
- Si no llego a H3 o a una malla, se entrega parcial: se dice lo medido y lo que falta.
